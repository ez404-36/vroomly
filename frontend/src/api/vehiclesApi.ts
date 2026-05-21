import { createApi } from '@reduxjs/toolkit/query/react';
import { createBaseQuery } from './baseQuery';
import type {
  CarInfoByVinDataSchema,
  ChoiceFieldSchema,
  ChoiceFieldWithParentSchema,
  CreateUserVehicleByChoiceSchema,
  CreateUserVehicleByVinSchema,
  CreateUserVehicleManualSchema,
  UserVehicleDetailSchema,
  UserVehicleWithChoicesSchema,
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
} from '../types/schema-types';

// Types for UserVehicle API
export type CreateUserVehicleByVinDTO = CreateUserVehicleByVinSchema;

export type CreateUserVehicleByChoiceDTO = CreateUserVehicleByChoiceSchema;

export type CreateUserVehicleManualDTO = CreateUserVehicleManualSchema;

export type {
  ChoiceFieldSchema,
  ChoiceFieldWithParentSchema,
  UserVehicleDetailSchema,
  UserVehicleWithChoicesSchema,
} from '../types/schema-types';

// UserVehicleChoiceSchema is defined inline as it's used in UserVehicleWithChoicesSchema
export interface UserVehicleChoiceSchema {
  brand: ChoiceFieldSchema;
  model: ChoiceFieldSchema;
  generation: ChoiceFieldSchema[];
  configuration: ChoiceFieldWithParentSchema[];
}

export const vehiclesApi = createApi({
  reducerPath: 'vehiclesApi',
  baseQuery: createBaseQuery('vehicles/'),
  endpoints: (builder) => ({
    // Lookup car info by VIN
    lookupByVin: builder.query<CarInfoByVinDataSchema, string>({
      query: (vin) => `by_vin/?vin=${vin}`,
    }),

    // Create user vehicle by VIN (returns UserVehicleDetailSchema or UserVehicleWithChoicesSchema)
    createUserVehicleByVin: builder.mutation<
      UserVehicleDetailSchema | UserVehicleWithChoicesSchema,
      CreateUserVehicleByVinDTO
    >({
      query: (body) => ({
        url: 'user-vehicles/',
        method: 'POST',
        body,
      }),
    }),

    // Create user vehicle by choice (after selecting from multiple options)
    createUserVehicleByChoice: builder.mutation<
      UserVehicleDetailSchema,
      CreateUserVehicleByChoiceDTO
    >({
      query: (body) => ({
        url: 'user-vehicles/by-choice/',
        method: 'POST',
        body,
      }),
    }),

    // Create user vehicle manually (without VIN)
    createUserVehicleManual: builder.mutation<
      UserVehicleDetailSchema,
      CreateUserVehicleManualDTO
    >({
      query: (body) => ({
        url: 'user-vehicles/manual/',
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
    getVehicleGenerations: builder.query<VehicleGenerationListSchema[], string>({
      query: (seriesId) => `generation/?series=${seriesId}`,
    }),

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
  useCreateUserVehicleByVinMutation,
  useCreateUserVehicleByChoiceMutation,
  useCreateUserVehicleManualMutation,
  useGetVehicleBrandsQuery,
  useGetVehicleSeriesQuery,
  useGetVehicleGenerationsQuery,
  useGetVehicleTrimsQuery,
  useGetUserVehiclesQuery,
  useDeleteUserVehicleMutation,
} = vehiclesApi;
