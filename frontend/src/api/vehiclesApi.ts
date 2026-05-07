import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

// Types for UserVehicle API
export interface CreateUserVehicleByVinDTO {
  vin: string;
}

export interface CreateUserVehicleByChoiceDTO {
  brand_id: string;
  series_id: string;
  generation_id: string;
  trim_id?: string;
}

export interface CreateUserVehicleManualDTO {
  brand_id?: string;
  series_id?: string;
  generation_id?: string;
  trim_id?: string;
  production_year?: number;
  color?: string;
}

export interface UserVehicleDetailSchema {
  id: string;
  vehicle_id: string | null;
  user_id: string;
  mileage: number | null;
  is_mileage_in_miles: boolean;
  avg_fuel_consumption: number | null;
  brand: string | null;
  series: string | null;
  generation: string | null;
  trim: string | null;
  production_year: number | null;
  color: string | null;
}

export interface ChoiceFieldSchema {
  id: string;
  name: string;
}

export interface ChoiceFieldWithParentSchema extends ChoiceFieldSchema {
  parent: ChoiceFieldSchema;
}

export interface UserVehicleChoiceSchema {
  brand: ChoiceFieldSchema;
  model: ChoiceFieldSchema;
  generation: ChoiceFieldSchema[];
  configuration: ChoiceFieldWithParentSchema[];
}

export interface UserVehicleWithChoicesSchema {
  choices: UserVehicleChoiceSchema[];
  vin: string;
  year: number;
  color: string | null;
}

export const vehiclesApi = createApi({
  reducerPath: 'vehiclesApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8077/api/vehicles/',
    credentials: 'include',
    prepareHeaders: (headers) => {
      headers.set('Content-Type', 'application/json');
      headers.set('Accept', 'application/json');
      return headers;
    },
  }),
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
      query: (brandId) => `series/?brand_id=${brandId}`,
    }),
  }),
});

export interface CarInfoByVinDataSchema {
  model: string;
  year: number;
  frame: string | null;
  vin: string;
  carplate: string;
  color: string;
  type: string;
  volume: number;
  power: number;
  frame_id: number;
  vehicle_type: string;
}

export interface VehicleBrandDetailSchema {
  id: string;
  countryId: string;
  code: string;
  name: string;
  originalName: string | null;
}

export interface VehicleSeriesListSchema {
  id: string;
  name: string;
  brandId: string;
}

export const {
  useLookupByVinQuery,
  useCreateUserVehicleByVinMutation,
  useCreateUserVehicleByChoiceMutation,
  useCreateUserVehicleManualMutation,
  useGetVehicleBrandsQuery,
  useGetVehicleSeriesQuery,
} = vehiclesApi;
