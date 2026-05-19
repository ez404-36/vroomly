import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Paper, Stack, Text } from '../../ui';
import { TextInput as MantineTextInput, Alert, LoadingOverlay } from '@mantine/core';
import {
  useCreateUserVehicleByVinMutation,
  UserVehicleDetailSchema,
  UserVehicleWithChoicesSchema,
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
  const isLoading = false;

  const onSubmit = async (data: { vin: string }) => {
    try {
      const response = await createVehicle({ vin: data.vin }).unwrap();
      setResult(response);

      // Check if we got choices (multiple options) or direct result
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
      <LoadingOverlay visible={isLoading} />

      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack>
          <MantineTextInput
            label="VIN-номер"
            placeholder="Введите 17-значный VIN-номер"
            description="Идентификационный номер транспортного средства"
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
        <Alert color="green" title="Автомобиль найден" mt="md">
          <Text size="sm">
            <strong>
              {result.brand} {result.series}
            </strong>
            {result.generation && ` ${result.generation}`}
          </Text>
          <Text size="sm" color="dimmed">
            Год выпуска: {result.production_year || 'не указан'} | Цвет:{' '}
            {result.color || 'не указан'}
          </Text>
        </Alert>
      )}

      {isResultWithChoices && (
        <Alert color="yellow" title="Выберите комплектацию" mt="md">
          <Text size="sm">
            Найдено несколько вариантов. Выберите подходящую комплектацию.
          </Text>
        </Alert>
      )}
    </Paper>
  );
};
