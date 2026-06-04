import dayjs from 'dayjs';

export interface ProfileFormData {
  login: string;
  email: string;
  name: string | null;
  surname: string | null;
  birth_date: Date | null;
  country_id: string | null;
}

export interface ProfileUpdatePayload {
  name: string | null;
  surname: string | null;
  country_id: string | null;
  birth_date: string | null;
}

/**
 * Преобразует данные формы профиля в payload для обновления.
 *
 * Пустые строки имени/фамилии нормализуются в `null`; дата рождения
 * форматируется в `YYYY-MM-DD` (или `null`). Чистая функция — без побочных
 * эффектов, тестируется изолированно.
 */
export function toProfileUpdatePayload(
  data: ProfileFormData,
): ProfileUpdatePayload {
  return {
    name: data.name || null,
    surname: data.surname || null,
    country_id: data.country_id,
    birth_date: data.birth_date
      ? dayjs(data.birth_date).format('YYYY-MM-DD')
      : null,
  };
}
