import { createApi } from '@reduxjs/toolkit/query/react';
import type { CurrentUser } from '../types/schema-types';
import { createBaseQuery } from './baseQuery';
import { formatApiError } from './errors';

const formDataBody = (data: Record<string, unknown>) =>
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
    login: builder.mutation({
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

    register: builder.mutation({
      query: (body) => ({
        url: 'registration',
        method: 'POST',
        body: formDataBody(body),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }),
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
