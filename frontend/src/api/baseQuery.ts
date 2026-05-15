import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const createBaseQuery = (baseUrl: string) =>
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