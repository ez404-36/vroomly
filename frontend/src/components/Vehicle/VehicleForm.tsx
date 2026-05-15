import { useForm } from 'react-hook-form';
import {
  TextInput,
  NumberInput,
  Select,
  Button,
  Stack,
  Paper,
  Text,
} from '@mantine/core';
import {
  useCreateUserVehicleManualMutation,
  useGetVehicleBrandsQuery,
  useGetVehicleSeriesQuery,
} from '../../api/vehiclesApi';

export interface VehicleFormData {
  brand_id?: string;
  series_id?: string;
  generation_id?: string;
  production_year?: number;
  color?: string;
}

export interface VehicleFormProps {
  onSuccess?: () => void;
}

export const VehicleForm = ({ onSuccess }: VehicleFormProps) => {
  const [createVehicle, { isLoading, error }] =
    useCreateUserVehicleManualMutation();
  const { data: brands } = useGetVehicleBrandsQuery();
  const { data: series } = useGetVehicleSeriesQuery;

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<VehicleFormData>({
    defaultValues: {
      brand_id: '',
      series_id: '',
      production_year: undefined,
      color: '',
    },
    mode: 'onChange',
  });

  const selectedBrand = watch('brand_id');
  const selectedSeries = watch('series_id');

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

  const onSubmit = async (data: VehicleFormData) => {
    try {
      await createVehicle({
        ...data,
        production_year: data.production_year,
      }).unwrap();
      onSuccess?.();
    } catch (err) {
      console.error('Ошибка создания ТС:', err);
    }
  };

  return (
    <Paper withBorder p="md">
      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack>
          <Select
            label="Марка"
            placeholder="Выберите марку автомобиля"
            data={brandOptions}
            searchable
            clearable
            onChange={(value) => setValue('brand_id', value || undefined)}
            value={selectedBrand || undefined}
            error={errors.brand_id?.message}
          />

          <Select
            label="Модель"
            placeholder="Выберите модель"
            data={seriesOptions}
            searchable
            clearable
            disabled={!selectedBrand}
            onChange={(value) => setValue('series_id', value || undefined)}
            value={selectedSeries || undefined}
            error={errors.series_id?.message}
          />

          <NumberInput
            label="Год выпуска"
            placeholder="2020"
            min={1900}
            max={new Date().getFullYear() + 1}
            {...register('production_year', {
              setValueAs: (value) => (value ? Number(value) : undefined),
            })}
            error={errors.production_year?.message}
          />

          <TextInput
            label="Цвет"
            placeholder="Например: Серебристый"
            {...register('color')}
          />

          {error && (
            <Text c="red" size="sm">
              {JSON.stringify(error)}
            </Text>
          )}

          <Button type="submit" loading={isLoading}>
            Сохранить
          </Button>
        </Stack>
      </form>
    </Paper>
  );
};
