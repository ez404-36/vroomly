/**
 * Convenience type aliases for schemas.ts component types.
 * This file extracts flat types from the nested openapi-typescript output.
 */
import type { components } from './schemas';

export type CarInfoByVinDataSchema =
  components['schemas']['CarInfoByVinDataSchema'];
export type ChoiceFieldSchema = components['schemas']['ChoiceFieldSchema'];
export type CountryDetailSchema = components['schemas']['CountryDetailSchema'];
export type CreateReminderSchema =
  components['schemas']['CreateReminderSchema'];
export type CreateUserVehicleSchema =
  components['schemas']['CreateUserVehicleSchema'];
export type CurrentUser = components['schemas']['CurrentUser'];
export type GuessByVinResponseSchema =
  components['schemas']['GuessByVinResponseSchema'];
export type RegistrationDataForm =
  components['schemas']['RegistrationDataForm'];
export type ReminderDetailSchema =
  components['schemas']['ReminderDetailSchema'];
export type UpdateReminderSchema =
  components['schemas']['UpdateReminderSchema'];
export type UpdateMileageSchema = components['schemas']['UpdateMileageSchema'];
export type UserVehicleDetailSchema =
  components['schemas']['UserVehicleDetailSchema'];
export type UserVehicleListSchema =
  components['schemas']['UserVehicleListSchema'];
export type VehicleBrandDetailSchema =
  components['schemas']['VehicleBrandDetailSchema'];
export type VehicleSeriesDetailSchema =
  components['schemas']['VehicleSeriesDetailSchema'];
export type VehicleSeriesListSchema =
  components['schemas']['VehicleSeriesListSchema'];
export type VehicleGenerationListSchema =
  components['schemas']['VehicleGenerationListSchema'];
export type VehicleTrimListSchema =
  components['schemas']['VehicleTrimListSchema'];
export type TrimChoiceSchema = components['schemas']['TrimChoiceSchema'];
export type TrimEngineSchema = components['schemas']['TrimEngineSchema'];
export type TrimTransmissionSchema =
  components['schemas']['TrimTransmissionSchema'];
