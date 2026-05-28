import { useForm } from 'react-hook-form';
import { Button, Paper, Stack, Text, TextInput } from '../../ui';
import {
  useLazyGuessByVinQuery,
  type GuessByVinResponseSchema,
} from '../../api/vehiclesApi';

export interface VinLookupFormProps {
  /** Вызывается при успешном подборе вариантов по VIN. */
  onGuess: (data: GuessByVinResponseSchema) => void;
  /** Кнопка "Назад". */
  onBack?: () => void;
  /** Кнопка "Заполнить вручную" — пропустить VIN-шаг. */
  onSkipToManual?: () => void;
}

const VIN_LENGTH = 17;

export const VinLookupForm = ({
  onGuess,
  onBack,
  onSkipToManual,
}: VinLookupFormProps) => {
  const [triggerGuess, { isFetching, error }] = useLazyGuessByVinQuery();

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
  const isValidVin = vin && vin.length === VIN_LENGTH;

  const onSubmit = async (data: { vin: string }) => {
    try {
      const response = await triggerGuess(data.vin).unwrap();
      onGuess(response);
    } catch (err) {
      console.error('Ошибка поиска по VIN:', err);
    }
  };

  return (
    <Paper p="md" style={{ position: 'relative' }}>
      {isFetching && (
        <div className="absolute inset-0 flex items-center justify-center bg-(--color-surface)/70 rounded-md z-10">
          <div className="animate-spin h-8 w-8 rounded-full border-4 border-(--color-primary) border-t-transparent" />
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
                value: VIN_LENGTH,
                message: 'VIN должен содержать 17 символов',
              },
              maxLength: {
                value: VIN_LENGTH,
                message: 'VIN должен содержать 17 символов',
              },
            })}
            error={errors.vin?.message}
          />

          <div className="flex gap-3 flex-wrap">
            {onBack && (
              <Button type="button" variant="ghost" onClick={onBack}>
                Назад
              </Button>
            )}
            {onSkipToManual && (
              <Button type="button" variant="ghost" onClick={onSkipToManual}>
                Заполнить вручную
              </Button>
            )}
            <Button
              type="submit"
              variant="filled"
              disabled={!isValidVin}
              loading={isFetching}
            >
              Найти по VIN
            </Button>
          </div>

          {error && (
            <Text color="red" size="sm">
              Не удалось получить данные по VIN. Попробуйте ввести данные
              вручную.
            </Text>
          )}
        </Stack>
      </form>
    </Paper>
  );
};
