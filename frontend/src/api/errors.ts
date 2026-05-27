import type { FetchBaseQueryError } from '@reduxjs/toolkit/query/react';

interface ApiErrorDetail {
  detail?: string;
}

const ERROR_MESSAGES: Record<string, string> = {
  'User not found': 'Пользователь не найден',
  'Invalid password': 'Неверный пароль',
  'User already exists': 'Пользователь уже существует',
  'Account is inactive': 'Аккаунт неактивен',
  'Token expired': 'Сессия истекла. Войдите снова',
  'Invalid token': 'Недействительный токен',
};

export function formatApiError(response: FetchBaseQueryError): string {
  const data = response.data as ApiErrorDetail | undefined;
  const status = response.status;

  if (data && typeof data === 'object' && 'detail' in data) {
    const detail = data.detail ?? '';
    return ERROR_MESSAGES[detail] ?? detail;
  }

  if (typeof status === 'number') {
    return `Ошибка ${status}`;
  }

  return String(status);
}

export function isApiError(error: unknown): error is FetchBaseQueryError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'status' in error &&
    'data' in error
  );
}
