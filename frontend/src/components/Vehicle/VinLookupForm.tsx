import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Paper, Stack, Text, TextInput } from '../../ui';
import {
  useCreateUserVehicleByVinMutation,
  type UserVehicleDetailSchema,
  type UserVehicleWithChoicesSchema,
} from '../../api/vehiclesApi';

export interface VinLookupFormProps {
  onSuccess?: (data: UserVehicleDetailSchema) => void;
  onMultipleChoices?: (data: UserVehicleWithChoicesSchema) => void;
}

export const VinLookupForm = ({
  onSuccess,
  onMultipleChoices,
}: VinLookupFormProps) => {
  const [result, setResult] = useState<
    UserVehicleDetailSchema | UserVehicleWithChoicesSchema | null
  >(null);
  const [createVehicle, { isLoading: isCreating }] =
    useCreateUserVehicleByVinMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<{ vin: string }>({
    defaultValues: { vin: '' },
    mode: 'onChange',
  });

  const vin = watch('vin');
  const isValidVin = vin && vin.length === 17;

  const onSubmit = async (data: { vin: string }) => {
    try {
      const response = await createVehicle({ vin: data.vin }).unwrap();
      setResult(response);

      if ('choices' in response) {
        onMultipleChoices?.(response);
      } else {
        onSuccess?.(response);
      }
    } catch (err) {
      console.error('Ошибка поиска по VIN:', err);
    }
  };

  const isResultWithChoices = result && 'choices' in result;

  return (
    <Paper withBorder p="md" style={{ position: 'relative' }}>
      {isCreating && (
        <div className="absolute inset-0 flex items-center justify-center bg-[--color-surface]/70 rounded-md z-10">
          <div className="animate-spin h-8 w-8 rounded-full border-4 border-[--color-primary] border-t-transparent" />
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack>
          <TextInput
            label="VIN-номер"
            placeholder="Введите 17-значный VIN-номер"
            {...register('vin', {
              required: 'Введите VIN-номер',
              minLength: {
                value: 17,
                message: 'VIN должен содержать 17 символов',
              },
              maxLength: {
                value: 17,
                message: 'VIN должен содержать 17 символов',
              },
            })}
            error={errors.vin?.message}
          />

          <Button type="submit" disabled={!isValidVin} loading={isCreating}>
            Найти по VIN
          </Button>
        </Stack>
      </form>

      {result && !isResultWithChoices && 'brand' in result && (
        <div className="mt-4 rounded-md border border-green-500 bg-green-500/10 p-4">
          <p className="text-sm font-medium text-green-700 mb-1">Автомобиль найден</p>
          <Text size="sm">
            <strong>
              {result.brand} {result.series}
            </strong>
            {result.generation && ` ${result.generation}`}
          </Text>
          <Text size="sm" c="dimmed">
            Год выпуска: {result.production_year || 'не указан'} | Цвет:{' '}
            {result.color || 'не указан'}
          </Text>
        </div>
      )}

      {isResultWithChoices && (
        <div className="mt-4 rounded-md border border-yellow-500 bg-yellow-500/10 p-4">
          <p className="text-sm font-medium text-yellow-700 mb-1">Выберите комплектацию</p>
          <Text size="sm">
            Найдено несколько вариантов. Выберите подходящую комплектацию.
          </Text>
        </div>
      )}
    </Paper>
  );
};
