import { useEffect, useMemo, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Select,
  Button,
  Stack,
  Paper,
  Text,
  NumberInput,
  TextInput,
  Switch,
} from '../../ui';
import {
  useCreateUserVehicleMutation,
  useGetVehicleBrandsQuery,
  useGetVehicleSeriesQuery,
  useGetVehicleGenerationsQuery,
  useGetVehicleTrimsQuery,
  type CreateUserVehicleSchema,
  type GuessByVinResponseSchema,
} from '../../api/vehiclesApi';

interface VehicleFormData {
  brandId: string;
  seriesId: string;
  generationId: string;
  trimId: string;
  productionYear: number | undefined;
  color: string;
  mileage: number | undefined;
  avgFuelConsumption: number | undefined;
  isMileageInMiles: boolean;
  vin: string;
}

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

interface SelectOption {
  value: string;
  label: string;
}

const toOption = <T extends { id: string; name: string }>(
  item: T,
): SelectOption => ({
  value: item.id,
  label: item.name,
});

export const VehicleForm = ({
  prefill,
  onSuccess,
  onBack,
}: VehicleFormProps) => {
  const [createVehicle, { isLoading, error: createError }] =
    useCreateUserVehicleMutation();
  const { data: brands } = useGetVehicleBrandsQuery();

  // Single generation/trim из prefill авто-выбираются ниже через useEffect.
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

  // Если brand/series пришли из prefill — не запрашиваем series у API,
  // но если пользователь сменит бренд вручную, мы переключимся на API-данные.
  const [seriesOverride, setSeriesOverride] = useState<boolean>(
    Boolean(prefill),
  );
  const [generationOverride, setGenerationOverride] = useState<boolean>(
    Boolean(prefill),
  );
  const [trimOverride, setTrimOverride] = useState<boolean>(Boolean(prefill));

  const { data: seriesList, isLoading: isSeriesLoading } =
    useGetVehicleSeriesQuery(selectedBrand || '', {
      skip: !selectedBrand || seriesOverride,
    });

  const { data: generations, isLoading: isGenerationsLoading } =
    useGetVehicleGenerationsQuery(selectedSeries || '', {
      skip: !selectedSeries || generationOverride,
    });

  const { data: trims, isLoading: isTrimsLoading } = useGetVehicleTrimsQuery(
    selectedGeneration || '',
    { skip: !selectedGeneration || trimOverride },
  );

  // При ручной смене бренда отключаем override и чистим зависимые поля.
  useEffect(() => {
    if (prefill && selectedBrand !== prefillBrandId) {
      setSeriesOverride(false);
      setGenerationOverride(false);
      setTrimOverride(false);
    }
    if (!selectedBrand) {
      setValue('seriesId', '', { shouldValidate: false });
      setValue('generationId', '', { shouldValidate: false });
      setValue('trimId', '', { shouldValidate: false });
    }
  }, [selectedBrand, prefill, prefillBrandId, setValue]);

  useEffect(() => {
    if (prefill && selectedSeries !== prefillSeriesId) {
      setGenerationOverride(false);
      setTrimOverride(false);
    }
    if (!selectedSeries) {
      setValue('generationId', '', { shouldValidate: false });
      setValue('trimId', '', { shouldValidate: false });
    }
  }, [selectedSeries, prefill, prefillSeriesId, setValue]);

  useEffect(() => {
    if (prefill && selectedGeneration !== prefillGenerationId) {
      setTrimOverride(false);
    }
    if (!selectedGeneration) {
      setValue('trimId', '', { shouldValidate: false });
    }
  }, [selectedGeneration, prefill, prefillGenerationId, setValue]);

  // Options:
  // - если override и есть prefill — берём из prefill
  // - иначе — из API.
  const brandOptions = useMemo<SelectOption[]>(() => {
    const base = brands?.map(toOption) ?? [];
    if (prefill) {
      const id = String(prefill.brand.id);
      const exists = base.some((opt) => opt.value === id);
      if (!exists) {
        base.unshift({ value: id, label: prefill.brand.name });
      }
    }
    return base;
  }, [brands, prefill]);

  const seriesOptions = useMemo<SelectOption[]>(() => {
    if (seriesOverride && prefill) {
      return [{ value: String(prefill.model.id), label: prefill.model.name }];
    }
    return seriesList?.map(toOption) ?? [];
  }, [seriesList, seriesOverride, prefill]);

  const generationOptions = useMemo<SelectOption[]>(() => {
    if (generationOverride && prefill) {
      return (
        prefill.generations?.map((g) => ({
          value: String(g.id),
          label: g.name,
        })) ?? []
      );
    }
    return generations?.map(toOption) ?? [];
  }, [generations, generationOverride, prefill]);

  const trimOptions = useMemo<SelectOption[]>(() => {
    if (trimOverride && prefill) {
      return (
        prefill.trims?.map((t) => ({
          value: String(t.id),
          // description содержит двигатель/КПП/привод/кузов — показываем его,
          // чтобы из селектора было понятно, какую именно комплектацию выбирают.
          label: t.description ? `${t.name} — ${t.description}` : t.name,
        })) ?? []
      );
    }
    return trims?.map(toOption) ?? [];
  }, [trims, trimOverride, prefill]);

  const onSubmit = async (data: VehicleFormData) => {
    if (data.productionYear === undefined) {
      return;
    }
    const payload: CreateUserVehicleSchema = {
      generationId: data.generationId || null,
      trimId: data.trimId || null,
      productionYear: data.productionYear,
      color: data.color || null,
      mileage: data.mileage ?? null,
      isMileageInMiles: data.isMileageInMiles,
      avgFuelConsumption: data.avgFuelConsumption ?? null,
      vin: data.vin || null,
    };
    try {
      await createVehicle(payload).unwrap();
      onSuccess?.();
    } catch (err) {
      console.error('Ошибка создания ТС:', err);
    }
  };

  return (
    <Paper p="md">
      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack>
          <Select
            label="Марка"
            required
            placeholder="Выберите марку автомобиля"
            options={brandOptions}
            searchable
            clearable
            onChange={(value) => setValue('brandId', value || '')}
            value={selectedBrand || ''}
            error={errors.brandId?.message}
          />

          <Select
            key={`series-${selectedBrand}`}
            label="Модель"
            required
            placeholder="Выберите модель"
            options={seriesOptions}
            searchable
            clearable
            disabled={!selectedBrand || isSeriesLoading}
            onChange={(value) => setValue('seriesId', value || '')}
            value={selectedSeries || ''}
            error={errors.seriesId?.message}
          />

          <Select
            key={`generation-${selectedSeries}`}
            label="Поколение"
            placeholder="Выберите поколение"
            options={generationOptions}
            searchable
            clearable
            disabled={!selectedSeries || isGenerationsLoading}
            onChange={(value) => setValue('generationId', value || '')}
            value={selectedGeneration || ''}
            error={errors.generationId?.message}
          />

          <Select
            key={`trim-${selectedGeneration}`}
            label="Комплектация"
            placeholder="Выберите комплектацию (опционально)"
            options={trimOptions}
            searchable
            clearable
            disabled={!selectedGeneration || isTrimsLoading}
            onChange={(value) => setValue('trimId', value || '')}
            value={watch('trimId') || ''}
            error={errors.trimId?.message}
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
