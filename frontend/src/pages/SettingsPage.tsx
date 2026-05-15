import {
  Container,
  Paper,
  Title,
  TextInput,
  Button,
  Stack,
  Group,
  Select,
  Loader,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import dayjs from 'dayjs';
import { CustomDatePickerInput } from '../components/Common/CustomDatePickerInput';
import { useForm } from 'react-hook-form';
import { useGetCurrentUserQuery, useUpdateCurrentUserMutation } from '../api/authApi';
import { useGetCountriesQuery } from '../api/geoApi';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

interface ProfileFormData {
  login: string;
  email: string;
  name: string | null;
  surname: string | null;
  birth_date: Date | null;
  country_id: string | null;
}

export const SettingsPage = () => {
  const navigate = useNavigate();
  const { data: user, isLoading: isLoadingUser } = useGetCurrentUserQuery();
  const { data: countries, isLoading: isLoadingCountries } = useGetCountriesQuery();
  const [updateUser, { isLoading: isUpdating }] = useUpdateCurrentUserMutation();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ProfileFormData>({
    defaultValues: {
      login: '',
      email: '',
      name: null,
      surname: null,
      birth_date: null,
      country_id: null,
    },
  });

  useEffect(() => {
    if (user) {
      setValue('login', user.login);
      setValue('email', user.email);
      setValue('name', user.name);
      setValue('surname', user.surname);
      setValue('country_id', user.countryId);
      if (user.birthDate) {
        setValue('birth_date', new Date(user.birthDate));
      }
    }
  }, [user, setValue]);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      const formattedData = {
        name: data.name || null,
        surname: data.surname || null,
        country_id: data.country_id,
        birth_date: data.birth_date
          ? dayjs(data.birth_date).format('YYYY-MM-DD')
          : null,
      };

      await updateUser(formattedData).unwrap();
      notifications.show({
        title: 'Успешно',
        message: 'Профиль обновлён',
        color: 'green',
      });
      navigate('/');
    } catch (err) {
      notifications.show({
        title: 'Ошибка',
        message: 'Не удалось обновить профиль',
        color: 'red',
      });
    }
  };

  const countryOptions =
    countries?.map((country) => ({
      value: country.id,
      label: country.name,
    })) || [];

  if (isLoadingUser || isLoadingCountries) {
    return (
      <Container size="sm" py="xl">
        <Group justify="center">
          <Loader />
        </Group>
      </Container>
    );
  }

  return (
    <Container size="sm" py="xl">
      <Paper p="xl" radius="md">
        <Stack>
          <Title order={2}>Настройки профиля</Title>

          <form onSubmit={handleSubmit(onSubmit)}>
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
                data={countryOptions}
                searchable
                clearable
                onChange={(value) => setValue('country_id', value)}
                value={watch('country_id')}
              />

              <Group justify="flex-end" mt="md">
                <Button variant="subtle" onClick={() => navigate(-1)}>
                  Отмена
                </Button>
                <Button type="submit" loading={isUpdating}>
                  Сохранить
                </Button>
              </Group>
            </Stack>
          </form>
        </Stack>
      </Paper>
    </Container>
  );
};
