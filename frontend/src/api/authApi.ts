import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const formDataBody = (data: Record<string, unknown>) =>
  Object.entries(data)
    .map(
      ([key, value]) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`,
    )
    .join('&');

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8077/api/accounts/', // baseurl
    credentials: 'include',
    prepareHeaders: (headers) => {
      headers.set('Content-Type', 'application/x-www-form-urlencoded');
      headers.set('Accept', '*/*');
      return headers;
    },
  }),
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (body) => ({
        url: 'login',
        method: 'POST',
        body: formDataBody(body),
      }),
    }),

    register: builder.mutation({
      query: (body) => ({
        url: 'registration',
        method: 'POST',
        body: formDataBody(body),
      }),
    }),
  }),
});

export const { useLoginMutation, useRegisterMutation } = authApi;
