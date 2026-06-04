import { useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Button,
  Stack,
  Paper,
  Text,
  NumberInput,
  TextInput,
  Switch,
} from '../../ui';
import type { GuessByVinResponseSchema } from '../../api/vehiclesApi';
import {
  useVehicleCatalogCascade,
  type CascadeReset,
} from '../../hooks/useVehicleCatalogCascade';
import {
  useCreateVehicleSubmit,
  type VehicleFormData,
} from '../../hooks/useCreateVehicleSubmit';
import { VehicleCatalogSelects } from './VehicleCatalogSelects';

export interface VehicleFormProps {
  /**
   * Опциональное предзаполнение из guess_by_vin.
   * Если задано — brand/series/generations/trims подмешиваются в опции селектов,
   * production_year/color/vin предзаполняются.
   */
  prefill?: GuessByVinResponseSchema;
  onSuccess?: () => void;
  onBack?: () => void;
}

const MIN_PRODUCTION_YEAR = 1900;

export const VehicleForm = ({
  prefill,
  onSuccess,
  onBack,
}: VehicleFormProps) => {
  const prefillBrandId = prefill?.brand.id ? String(prefill.brand.id) : '';
  const prefillSeriesId = prefill?.model.id ? String(prefill.model.id) : '';
  const prefillGenerationId =
    prefill?.generations && prefill.generations.length === 1
      ? String(prefill.generations[0].id)
      : '';
  const prefillTrimId =
    prefill?.trims && prefill.trims.length === 1
      ? String(prefill.trims[0].id)
      : '';

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    formState: { errors },
  } = useForm<VehicleFormData>({
    defaultValues: {
      brandId: prefillBrandId,
      seriesId: prefillSeriesId,
      generationId: prefillGenerationId,
      trimId: prefillTrimId,
      productionYear: prefill?.year ?? undefined,
      color: prefill?.color ?? '',
      mileage: undefined,
      avgFuelConsumption: undefined,
      isMileageInMiles: false,
      vin: prefill?.vin ?? '',
    },
    mode: 'onChange',
  });

  const selectedBrand = watch('brandId');
  const selectedSeries = watch('seriesId');
  const selectedGeneration = watch('generationId');
  const selectedTrim = watch('trimId');

  const handleResetFields = useCallback(
    (fields: CascadeReset) => {
      if (fields.series) {
        setValue('seriesId', '', { shouldValidate: false });
      }
      if (fields.generation) {
        setValue('generationId', '', { shouldValidate: false });
      }
      if (fields.trim) {
        setValue('trimId', '', { shouldValidate: false });
      }
    },
    [setValue],
  );

  const {
    brandOptions,
    seriesOptions,
    generationOptions,
    trimOptions,
    isSeriesLoading,
    isGenerationsLoading,
    isTrimsLoading,
  } = useVehicleCatalogCascade({
    prefill,
    selectedBrand,
    selectedSeries,
    selectedGeneration,
    onResetFields: handleResetFields,
  });

  const {
    submit,
    isLoading,
    error: createError,
  } = useCreateVehicleSubmit(onSuccess);

  return (
    <Paper p="md">
      <form onSubmit={handleSubmit(submit)}>
        <Stack>
          <VehicleCatalogSelects
            brandOptions={brandOptions}
            seriesOptions={seriesOptions}
            generationOptions={generationOptions}
            trimOptions={trimOptions}
            selectedBrand={selectedBrand}
            selectedSeries={selectedSeries}
            selectedGeneration={selectedGeneration}
            selectedTrim={selectedTrim}
            isSeriesLoading={isSeriesLoading}
            isGenerationsLoading={isGenerationsLoading}
            isTrimsLoading={isTrimsLoading}
            errors={{
              brandId: errors.brandId?.message,
              seriesId: errors.seriesId?.message,
              generationId: errors.generationId?.message,
              trimId: errors.trimId?.message,
            }}
            onBrandChange={(value) => setValue('brandId', value)}
            onSeriesChange={(value) => setValue('seriesId', value)}
            onGenerationChange={(value) => setValue('generationId', value)}
            onTrimChange={(value) => setValue('trimId', value)}
          />

          <NumberInput
            label="Год выпуска"
            placeholder="2020"
            required
            min={MIN_PRODUCTION_YEAR}
            max={new Date().getFullYear() + 1}
            {...register('productionYear', {
              required: 'Укажите год выпуска',
              valueAsNumber: true,
              min: {
                value: MIN_PRODUCTION_YEAR,
                message: `Год должен быть не раньше ${MIN_PRODUCTION_YEAR}`,
              },
            })}
            error={errors.productionYear?.message}
          />

          <TextInput
            label="Цвет"
            placeholder="Например: Серебристый"
            {...register('color')}
          />

          <TextInput
            label="VIN-номер"
            placeholder="17 символов (опционально)"
            {...register('vin', {
              validate: (value) =>
                !value ||
                value.length === 17 ||
                'VIN должен содержать 17 символов',
            })}
            error={errors.vin?.message}
          />

          <NumberInput
            label="Пробег"
            placeholder="0"
            min={0}
            {...register('mileage', {
              setValueAs: (value: unknown) =>
                value === '' || value === null || value === undefined
                  ? undefined
                  : Number(value),
            })}
            error={errors.mileage?.message}
          />

          <Controller
            name="isMileageInMiles"
            control={control}
            render={({ field }) => (
              <Switch
                label="Пробег в милях"
                checked={field.value}
                onCheckedChange={(checked) => field.onChange(checked)}
              />
            )}
          />

          <NumberInput
            label="Средний расход топлива"
            placeholder="0.0"
            min={0}
            decimalScale={1}
            {...register('avgFuelConsumption', {
              setValueAs: (value: unknown) =>
                value === '' || value === null || value === undefined
                  ? undefined
                  : Number(value),
            })}
            error={errors.avgFuelConsumption?.message}
          />

          {createError && (
            <Text color="red" size="sm">
              {JSON.stringify(createError)}
            </Text>
          )}

          <div className="flex gap-3">
            {onBack && (
              <Button type="button" variant="ghost" onClick={onBack}>
                Назад
              </Button>
            )}
            <Button
              type="submit"
              variant="filled"
              loading={isLoading}
              disabled={!selectedBrand || !selectedSeries}
            >
              Сохранить
            </Button>
          </div>
        </Stack>
      </form>
    </Paper>
  );
};
