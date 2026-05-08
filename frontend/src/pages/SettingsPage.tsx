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
  birth_date: string;
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
    setValue,
    formState: { errors },
  } = useForm<ProfileFormData>({
    defaultValues: {
      login: '',
      email: '',
      name: null,
      surname: null,
      birth_date: '',
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
        setValue('birth_date', user.birthDate);
      }
    }
  }, [user, setValue]);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      const formattedData = {
        login: data.login,
        email: data.email,
        name: data.name || null,
        surname: data.surname || null,
        country_id: data.country_id,
        birth_date: data.birth_date || null,
      };

      await updateUser(formattedData).unwrap();
      navigate('/');
    } catch (err) {
      console.error('Ошибка обновления профиля:', err);
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
                {...register('login', { required: 'Введите username' })}
                error={errors.login?.message}
              />

              <TextInput
                label="Email"
                placeholder="Введите ваш email"
                {...register('email', {
                  required: 'Введите email',
                  pattern: {
                    value: /^\S+@\S+$/i,
                    message: 'Некорректный email',
                  },
                })}
                error={errors.email?.message}
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

              <TextInput
                label="Дата рождения"
                placeholder="ГГГГ-ММ-ДД"
                {...register('birth_date')}
              />

              <Select
                label="Страна"
                placeholder="Выберите страну"
                data={countryOptions}
                searchable
                clearable
                {...register('country_id')}
                onChange={(value) => setValue('country_id', value)}
                value={user?.countryId || null}
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