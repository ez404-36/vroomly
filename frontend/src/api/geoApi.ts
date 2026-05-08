import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { CountryDetailSchema } from '../types/schemas';

export const geoApi = createApi({
  reducerPath: 'geoApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8077/api/geo/',
    credentials: 'include',
    prepareHeaders: (headers) => {
      headers.set('Accept', 'application/json');
      return headers;
    },
  }),
  endpoints: (builder) => ({
    getCountries: builder.query<CountryDetailSchema[], void>({
      query: () => 'country/',
    }),
  }),
});

export const { useGetCountriesQuery } = geoApi;