import { createApi } from '@reduxjs/toolkit/query/react';
import { createBaseQuery } from './baseQuery';
import type {
  CarInfoByVinDataSchema,
  CreateReminderSchema,
  CreateUserVehicleSchema,
  GuessByVinResponseSchema,
  ReminderDetailSchema,
  UpdateMileageSchema,
  UpdateReminderSchema,
  UserVehicleDetailSchema,
  UserVehicleListSchema,
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
} from '../types/schema-types';

export type {
  ChoiceFieldSchema,
  CreateReminderSchema,
  CreateUserVehicleSchema,
  GuessByVinResponseSchema,
  ReminderDetailSchema,
  UpdateMileageSchema,
  UpdateReminderSchema,
  UserVehicleDetailSchema,
  UserVehicleListSchema,
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
} from '../types/schema-types';

export interface ListRemindersArgs {
  userVehicleId: string;
  isCompleted?: boolean;
}

export const vehiclesApi = createApi({
  reducerPath: 'vehiclesApi',
  baseQuery: createBaseQuery('vehicles/'),
  tagTypes: ['Reminder', 'UserVehicle'],
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
      invalidatesTags: [{ type: 'UserVehicle', id: 'LIST' }],
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

    // Get user's vehicles list (минимальный набор данных)
    getUserVehicles: builder.query<UserVehicleListSchema[], void>({
      query: () => 'user-vehicles/',
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'UserVehicle' as const, id })),
              { type: 'UserVehicle' as const, id: 'LIST' },
            ]
          : [{ type: 'UserVehicle' as const, id: 'LIST' }],
    }),

    // Детальная информация о ТС пользователя (все характеристики)
    getUserVehicle: builder.query<UserVehicleDetailSchema, string>({
      query: (userVehicleId) => `user-vehicles/${userVehicleId}/`,
      providesTags: (_result, _error, userVehicleId) => [
        { type: 'UserVehicle', id: userVehicleId },
      ],
    }),

    // Обновить пробег ТС пользователя
    updateUserVehicleMileage: builder.mutation<
      UserVehicleDetailSchema,
      { userVehicleId: string; body: UpdateMileageSchema }
    >({
      query: ({ userVehicleId, body }) => ({
        url: `user-vehicles/${userVehicleId}/mileage/`,
        method: 'PATCH',
        body,
      }),
      invalidatesTags: (_result, _error, { userVehicleId }) => [
        { type: 'UserVehicle', id: userVehicleId },
        { type: 'UserVehicle', id: 'LIST' },
      ],
    }),

    // Delete user vehicle
    deleteUserVehicle: builder.mutation<void, string>({
      query: (vehicleId) => ({
        url: `user-vehicles/${vehicleId}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, vehicleId) => [
        { type: 'UserVehicle', id: vehicleId },
        { type: 'UserVehicle', id: 'LIST' },
        { type: 'Reminder', id: 'LIST' },
      ],
    }),

    // Получить список напоминаний по ТС (опц. фильтр по статусу выполнения)
    getReminders: builder.query<ReminderDetailSchema[], ListRemindersArgs>({
      query: ({ userVehicleId, isCompleted }) => {
        const search =
          isCompleted === undefined
            ? ''
            : `?is_completed=${isCompleted ? 'true' : 'false'}`;
        return `user-vehicles/${userVehicleId}/reminders/${search}`;
      },
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Reminder' as const, id })),
              { type: 'Reminder' as const, id: 'LIST' },
            ]
          : [{ type: 'Reminder' as const, id: 'LIST' }],
    }),

    // Создать напоминание для ТС
    createReminder: builder.mutation<
      ReminderDetailSchema,
      { userVehicleId: string; body: CreateReminderSchema }
    >({
      query: ({ userVehicleId, body }) => ({
        url: `user-vehicles/${userVehicleId}/reminders/`,
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Reminder', id: 'LIST' }],
    }),

    // Редактировать напоминание (частичное обновление)
    updateReminder: builder.mutation<
      ReminderDetailSchema,
      { reminderId: string; body: UpdateReminderSchema }
    >({
      query: ({ reminderId, body }) => ({
        url: `reminders/${reminderId}/`,
        method: 'PATCH',
        body,
      }),
      invalidatesTags: (_result, _error, { reminderId }) => [
        { type: 'Reminder', id: reminderId },
        { type: 'Reminder', id: 'LIST' },
      ],
    }),

    // Отметить напоминание выполненным
    completeReminder: builder.mutation<ReminderDetailSchema, string>({
      query: (reminderId) => ({
        url: `reminders/${reminderId}/complete/`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _error, reminderId) => [
        { type: 'Reminder', id: reminderId },
        { type: 'Reminder', id: 'LIST' },
      ],
    }),

    // Снять отметку о выполнении напоминания
    uncompleteReminder: builder.mutation<ReminderDetailSchema, string>({
      query: (reminderId) => ({
        url: `reminders/${reminderId}/uncomplete/`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _error, reminderId) => [
        { type: 'Reminder', id: reminderId },
        { type: 'Reminder', id: 'LIST' },
      ],
    }),

    // Удалить напоминание
    deleteReminder: builder.mutation<void, string>({
      query: (reminderId) => ({
        url: `reminders/${reminderId}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, reminderId) => [
        { type: 'Reminder', id: reminderId },
        { type: 'Reminder', id: 'LIST' },
      ],
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
  useGetUserVehicleQuery,
  useUpdateUserVehicleMileageMutation,
  useDeleteUserVehicleMutation,
  useGetRemindersQuery,
  useCreateReminderMutation,
  useUpdateReminderMutation,
  useCompleteReminderMutation,
  useUncompleteReminderMutation,
  useDeleteReminderMutation,
} = vehiclesApi;
