import { useEffect } from 'react';
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
  useCreateUserVehicleManualMutation,
  useGetVehicleBrandsQuery,
  useGetVehicleSeriesQuery,
  useGetVehicleGenerationsQuery,
  useGetVehicleTrimsQuery,
} from '../../api/vehiclesApi';

export interface VehicleFormData {
  brand_id?: string;
  series_id?: string;
  generation_id?: string;
  trim_id?: string;
  production_year?: number;
  color?: string;
  mileage?: number;
  avg_fuel_consumption?: number;
  is_mileage_in_miles?: boolean;
}

export interface VehicleFormProps {
  onSuccess?: () => void;
  onBack?: () => void;
}

export const VehicleForm = ({ onSuccess, onBack }: VehicleFormProps) => {
  const [createVehicle, { isLoading, error }] =
    useCreateUserVehicleManualMutation();
  const { data: brands } = useGetVehicleBrandsQuery();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    formState: { errors },
  } = useForm<VehicleFormData>({
    defaultValues: {
      brand_id: '',
      series_id: '',
      generation_id: '',
      trim_id: '',
      production_year: undefined,
      color: '',
      mileage: undefined,
      avg_fuel_consumption: undefined,
      is_mileage_in_miles: false,
    },
    mode: 'onChange',
  });

  const selectedBrand = watch('brand_id');
  const selectedSeries = watch('series_id');
  const selectedGeneration = watch('generation_id');

  const { data: series, isLoading: isSeriesLoading } = useGetVehicleSeriesQuery(
    selectedBrand || '',
    { skip: !selectedBrand },
  );

  const { data: generations, isLoading: isGenerationsLoading } =
    useGetVehicleGenerationsQuery(selectedSeries || '', {
      skip: !selectedSeries,
    });

  const { data: trims, isLoading: isTrimsLoading } = useGetVehicleTrimsQuery(
    selectedGeneration || '',
    { skip: !selectedGeneration }
  );

  useEffect(() => {
    if (!selectedBrand) {
      setValue('series_id', '', { shouldValidate: false });
      setValue('generation_id', '', { shouldValidate: false });
      setValue('trim_id', '', { shouldValidate: false });
    }
  }, [selectedBrand, setValue]);

  useEffect(() => {
    if (!selectedSeries) {
      setValue('generation_id', '', { shouldValidate: false });
      setValue('trim_id', '', { shouldValidate: false });
    }
  }, [selectedSeries, setValue]);

  useEffect(() => {
    if (!selectedGeneration) {
      setValue('trim_id', '', { shouldValidate: false });
    }
  }, [selectedGeneration, setValue]);

  const brandOptions =
    brands?.map((brand) => ({
      value: brand.id,
      label: brand.name,
    })) || [];

  const seriesOptions =
    series?.map((s) => ({
      value: s.id,
      label: s.name,
    })) || [];

  const generationOptions =
    generations?.map((g) => ({
      value: g.id,
      label: g.name,
    })) || [];

  const trimOptions =
    trims?.map((t) => ({
      value: t.id,
      label: t.name,
    })) || [];

  const onSubmit = async (data: VehicleFormData) => {
    try {
      await createVehicle({
        ...data,
        production_year: data.production_year,
        mileage: data.mileage,
        avg_fuel_consumption: data.avg_fuel_consumption,
        is_mileage_in_miles: data.is_mileage_in_miles ?? false,
      }).unwrap();
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
            onChange={(value) => setValue('brand_id', value || '')}
            value={selectedBrand || ''}
            error={errors.brand_id?.message}
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
            onChange={(value) => setValue('series_id', value || '')}
            value={selectedSeries || ''}
            error={errors.series_id?.message}
          />

          <Select
            key={`generation-${selectedSeries}`}
            label="Поколение"
            required
            placeholder="Выберите поколение"
            options={generationOptions}
            searchable
            clearable
            disabled={!selectedSeries || isGenerationsLoading}
            onChange={(value) => setValue('generation_id', value || '')}
            value={selectedGeneration || ''}
            error={errors.generation_id?.message}
          />

          <Select
            key={`trim-${selectedGeneration}`}
            label="Комплектация"
            placeholder="Выберите комплектацию (опционально)"
            options={trimOptions}
            searchable
            clearable
            disabled={!selectedGeneration || isTrimsLoading}
            onChange={(value) => setValue('trim_id', value || '')}
            value={watch('trim_id') || ''}
            error={errors.trim_id?.message}
          />

          <NumberInput
            label="Год выпуска"
            placeholder="2020"
            min={1900}
            max={new Date().getFullYear() + 1}
            {...register('production_year', {
              setValueAs: (value: unknown) => (value ? Number(value) : undefined),
            })}
            error={errors.production_year?.message}
          />

          <TextInput
            label="Цвет"
            placeholder="Например: Серебристый"
            {...register('color')}
          />

          <NumberInput
            label="Пробег"
            placeholder="0"
            min={0}
            {...register('mileage', {
              setValueAs: (value: unknown) => (value ? Number(value) : undefined),
            })}
            error={errors.mileage?.message}
          />

          <Controller
            name="is_mileage_in_miles"
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
            {...register('avg_fuel_consumption', {
              setValueAs: (value: unknown) => (value ? Number(value) : undefined),
            })}
            error={errors.avg_fuel_consumption?.message}
          />

          {error && (
            <Text color="red" size="sm">
              {JSON.stringify(error)}
            </Text>
          )}

          <div className="flex gap-3">
            <Button type="button" variant="ghost" onClick={onBack}>
              Назад
            </Button>
            <Button
              type="submit"
              variant="filled"
              loading={isLoading}
              disabled={!selectedBrand || !selectedSeries || !selectedGeneration}
            >
              Сохранить
            </Button>
          </div>
        </Stack>
      </form>
    </Paper>
  );
};
