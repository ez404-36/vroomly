import { createApi } from '@reduxjs/toolkit/query/react';
import type { CurrentUser } from '../types/schema-types';
import { createBaseQuery } from './baseQuery';
import { formatApiError } from './errors';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// Заданы как type-алиасы (а не interface), чтобы быть присваиваемыми
// `Record<string, string>` в `formDataBody` (у interface нет неявной
// index-сигнатуры).
export type LoginRequest = {
  username: string;
  password: string;
};

export type RegisterRequest = {
  login: string;
  email: string;
  password: string;
  confirm_password: string;
};

const formDataBody = <T extends Record<string, string>>(data: T): string =>
  Object.entries(data)
    .map(
      ([key, value]) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`,
    )
    .join('&');

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: createBaseQuery('accounts/'),
  endpoints: (builder) => ({
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (body) => ({
        url: 'login',
        method: 'POST',
        body: formDataBody(body),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }),
      transformErrorResponse: formatApiError,
    }),

    register: builder.mutation<string, RegisterRequest>({
      query: (body) => ({
        url: 'registration',
        method: 'POST',
        body: formDataBody(body),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }),
      transformErrorResponse: formatApiError,
    }),

    getCurrentUser: builder.query<CurrentUser, void>({
      query: () => 'me',
    }),

    updateCurrentUser: builder.mutation<
      CurrentUser,
      Partial<Omit<CurrentUser, 'id'>>
    >({
      query: (body) => ({
        url: 'me',
        method: 'PATCH',
        body,
        headers: {
          'Content-Type': 'application/json',
        },
      }),
    }),

    logout: builder.mutation<void, void>({
      query: () => ({
        url: 'logout',
        method: 'POST',
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useGetCurrentUserQuery,
  useUpdateCurrentUserMutation,
  useLogoutMutation,
} = authApi;
