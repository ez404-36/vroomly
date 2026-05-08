import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { CurrentUser } from '../types/schemas';

const formDataBody = (data: Record<string, unknown>) =>
  Object.entries(data)
    .map(
      ([key, value]) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`,
    )
    .join('&');

const baseQuery = fetchBaseQuery({
  baseUrl: 'http://localhost:8077/api/accounts/',
  credentials: 'include',
  prepareHeaders: (headers) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    headers.set('Accept', 'application/json');
    return headers;
  },
});

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQuery,
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
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useGetCurrentUserQuery,
  useUpdateCurrentUserMutation,
} = authApi;
