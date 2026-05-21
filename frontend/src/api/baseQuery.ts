import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import { logout } from '../store/authSlice';
import { routes } from '../utils/routes';

const createRawBaseQuery = (baseUrl: string) =>
  fetchBaseQuery({
    baseUrl: `http://localhost:8077/api/${baseUrl}`,
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

export const createBaseQuery = (
  baseUrl: string,
): BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> => {
  const rawBaseQuery = createRawBaseQuery(baseUrl);

  return async (args, api, extraOptions) => {
    const result = await rawBaseQuery(args, api, extraOptions);

    if (result.error && result.error.status === 401) {
      api.dispatch(logout());
      window.location.href = routes.login;
    }

    return result;
  };
};
