import { createApi } from '@reduxjs/toolkit/query/react';
import { createBaseQuery } from './baseQuery';
import type {
  CarInfoByVinDataSchema,
  CreateUserVehicleSchema,
  GuessByVinResponseSchema,
  UserVehicleDetailSchema,
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
} from '../types/schema-types';

export type {
  ChoiceFieldSchema,
  ChoiceFieldWithParentSchema,
  CreateUserVehicleSchema,
  GuessByVinResponseSchema,
  UserVehicleDetailSchema,
} from '../types/schema-types';

export const vehiclesApi = createApi({
  reducerPath: 'vehiclesApi',
  baseQuery: createBaseQuery('vehicles/'),
  endpoints: (builder) => ({
    // Lookup raw VIN data from external provider (no DB write)
    lookupByVin: builder.query<CarInfoByVinDataSchema, string>({
      query: (vin) => `by_vin/?vin=${vin}`,
    }),

    // Подобрать данные ТС по VIN для предзаполнения формы (read-only, ничего не пишет в БД)
    guessByVin: builder.query<GuessByVinResponseSchema, string>({
      query: (vin) => `guess_by_vin/?vin=${vin}`,
    }),

    // Создать ТС в гараже пользователя (единый эндпоинт)
    createUserVehicle: builder.mutation<
      UserVehicleDetailSchema,
      CreateUserVehicleSchema
    >({
      query: (body) => ({
        url: 'user-vehicles/',
        method: 'POST',
        body,
      }),
    }),

    // Get list of vehicle brands
    getVehicleBrands: builder.query<VehicleBrandDetailSchema[], void>({
      query: () => 'brands/',
    }),

    // Get list of vehicle series by brand ID
    getVehicleSeries: builder.query<VehicleSeriesListSchema[], string>({
      query: (brandId) => `series/?brand=${brandId}`,
    }),

    // Get list of vehicle generations by series ID
    getVehicleGenerations: builder.query<VehicleGenerationListSchema[], string>(
      {
        query: (seriesId) => `generation/?series=${seriesId}`,
      },
    ),

    // Get list of vehicle trims by generation ID
    getVehicleTrims: builder.query<VehicleTrimListSchema[], string>({
      query: (generationId) => `trim/?generation=${generationId}`,
    }),

    // Get user's vehicles list
    getUserVehicles: builder.query<UserVehicleDetailSchema[], void>({
      query: () => 'user-vehicles/',
    }),

    // Delete user vehicle
    deleteUserVehicle: builder.mutation<void, string>({
      query: (vehicleId) => ({
        url: `user-vehicles/${vehicleId}/`,
        method: 'DELETE',
      }),
    }),
  }),
});

export const {
  useLookupByVinQuery,
  useGuessByVinQuery,
  useLazyGuessByVinQuery,
  useCreateUserVehicleMutation,
  useGetVehicleBrandsQuery,
  useGetVehicleSeriesQuery,
  useGetVehicleGenerationsQuery,
  useGetVehicleTrimsQuery,
  useGetUserVehiclesQuery,
  useDeleteUserVehicleMutation,
} = vehiclesApi;
