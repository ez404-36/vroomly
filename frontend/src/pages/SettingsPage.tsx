import {
  Container,
  Paper,
  Title,
  TextInput,
  Button,
  Stack,
  Select,
} from '../ui';
import { CustomDatePickerInput } from '../components/Common/CustomDatePickerInput';
import { useProfileForm } from '../hooks/useProfileForm';

export const SettingsPage = () => {
  const { form, countryOptions, isLoading, isUpdating, submit, cancel } =
    useProfileForm();
  const { register, handleSubmit, watch, setValue } = form;

  if (isLoading) {
    return (
      <Container size="sm" py="xl">
        <div className="flex justify-center py-8">
          <div className="animate-spin h-8 w-8 rounded-full border-4 border-(--color-primary) border-t-transparent" />
        </div>
      </Container>
    );
  }

  return (
    <Container size="sm" py="xl">
      <Paper p="xl" radius="md">
        <Stack>
          <Title order={2}>Настройки профиля</Title>

          <form onSubmit={handleSubmit(submit)}>
            <Stack>
              <TextInput
                label="Username"
                placeholder="Введите username"
                {...register('login')}
                disabled
                readOnly
              />

              <TextInput
                label="Email"
                placeholder="Введите ваш email"
                {...register('email')}
                disabled
                readOnly
              />

              <TextInput
                label="Имя"
                placeholder="Введите имя"
                {...register('name')}
              />

              <TextInput
                label="Фамилия"
                placeholder="Введите фамилию"
                {...register('surname')}
              />

              <CustomDatePickerInput
                label="Дата рождения"
                onChange={(value) => setValue('birth_date', value)}
                value={watch('birth_date')}
                clearable
                maxDate={new Date()}
                defaultLevel="decade"
              />

              <Select
                label="Страна"
                placeholder="Выберите страну"
                options={countryOptions}
                searchable
                clearable
                onChange={(value) => setValue('country_id', value)}
                value={watch('country_id')}
              />

              <div className="flex justify-end gap-3 mt-4">
                <Button variant="ghost" onClick={cancel}>
                  Отмена
                </Button>
                <Button type="submit" loading={isUpdating}>
                  Сохранить
                </Button>
              </div>
            </Stack>
          </form>
        </Stack>
      </Paper>
    </Container>
  );
};
