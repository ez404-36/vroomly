import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import {
  useGetCurrentUserQuery,
  useUpdateCurrentUserMutation,
} from '../api/authApi';
import { useGetCountriesQuery } from '../api/geoApi';
import { toProfileUpdatePayload, type ProfileFormData } from '../utils/profile';

export interface CountryOption {
  value: string;
  label: string;
}

/**
 * Инкапсулирует логику формы профиля: загрузку пользователя/стран, синхронизацию
 * формы с данными пользователя, построение опций стран и сабмит (маппинг +
 * мутация + навигация). Страница остаётся презентационной.
 */
export function useProfileForm() {
  const navigate = useNavigate();
  const { data: user, isLoading: isLoadingUser } = useGetCurrentUserQuery();
  const { data: countries, isLoading: isLoadingCountries } =
    useGetCountriesQuery();
  const [updateUser, { isLoading: isUpdating }] =
    useUpdateCurrentUserMutation();

  const form = useForm<ProfileFormData>({
    defaultValues: {
      login: '',
      email: '',
      name: null,
      surname: null,
      birth_date: null,
      country_id: null,
    },
  });
  const { setValue } = form;

  useEffect(() => {
    if (!user) {
      return;
    }
    setValue('login', user.login);
    setValue('email', user.email);
    setValue('name', user.name);
    setValue('surname', user.surname);
    setValue('country_id', user.countryId);
    if (user.birthDate) {
      setValue('birth_date', new Date(user.birthDate));
    }
  }, [user, setValue]);

  const countryOptions: CountryOption[] =
    countries?.map((country) => ({
      value: country.id,
      label: country.name,
    })) ?? [];

  const submit = async (data: ProfileFormData) => {
    try {
      await updateUser(toProfileUpdatePayload(data)).unwrap();
      alert('Профиль обновлён');
      navigate('/');
    } catch {
      alert('Не удалось обновить профиль');
    }
  };

  return {
    form,
    countryOptions,
    isLoading: isLoadingUser || isLoadingCountries,
    isUpdating,
    submit,
    cancel: () => navigate(-1),
  };
}
