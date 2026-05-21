import { createApi } from '@reduxjs/toolkit/query/react';
import type { CountryDetailSchema } from '../types/schema-types';
import { createBaseQuery } from './baseQuery';

export const geoApi = createApi({
  reducerPath: 'geoApi',
  baseQuery: createBaseQuery('geo/'),
  endpoints: (builder) => ({
    getCountries: builder.query<CountryDetailSchema[], void>({
      query: () => 'country/',
    }),
  }),
});

export const { useGetCountriesQuery } = geoApi;
