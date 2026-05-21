/**
 * Factory for creating mock RTK Query APIs.
 *
 * Usage:
 *   import { createMockApi } from '@/mocks';
 *
 *   // Create a mock API with all endpoints mocked
 *   const mockVehiclesApi = createMockApi(vehiclesApi, {
 *     'GET:vehicles/brands/': () => mockSchemas.vehicleBrands(5),
 *     'GET:vehicles/series/': () => mockSchemas.vehicleSeriesListArray(3),
 *   });
 *
 *   // Use in tests
 *   render(<ComponentUsingVehiclesApi />, { wrapper: mockVehiclesApi });
 */

import type { BaseQueryFn } from '@reduxjs/toolkit/query/react';
import type { FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';

import { MockService } from './mockService';

/** Переопределения для конкретных эндпоинтов */
export type MockEndpointOverrides = Record<string, {
  data?: unknown;
  generator?: (args: FetchArgs | string) => unknown;
  delay?: number;
  error?: FetchBaseQueryError;
}>;

/**
 * Создать mock baseQuery на основе переопределений.
 */
export function createMockedBaseQuery(
  overrides: MockEndpointOverrides
): BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> {
  return async (args, _api, _extraOptions) => {
    const url = typeof args === 'string' ? args : args.url;
    const method = typeof args === 'object' ? (args.method ?? 'GET') : 'GET';
    const key = `${method}:${url}`;

    const override = overrides[key];

    if (!override) {
      return { data: undefined };
    }

    // Handle error
    if (override.error) {
      return { error: override.error };
    }

    // Apply delay
    if (override.delay && override.delay > 0) {
      await new Promise((resolve) => setTimeout(resolve, override.delay));
    }

    // Return data
    if (override.data !== undefined) {
      return { data: override.data };
    }

    if (override.generator) {
      return { data: override.generator(args) };
    }

    return { data: undefined };
  };
}

/**
 * Утилита для быстрого создания mock-эндпоинта.
 * Используется для programmatic mocking.
 */
export function createMockEndpoint<T>(
  dataOrGenerator: T | ((args: FetchArgs | string) => T),
  options?: { delay?: number; error?: FetchBaseQueryError }
): { data?: T; generator?: (args: FetchArgs | string) => T; delay?: number; error?: FetchBaseQueryError } {
  if (typeof dataOrGenerator === 'function') {
    return {
      generator: dataOrGenerator as (args: FetchArgs | string) => T,
      delay: options?.delay,
      error: options?.error,
    };
  }

  return {
    data: dataOrGenerator,
    delay: options?.delay,
    error: options?.error,
  };
}

/**
 * Создать middleware для RTK Query, который перехватывает запросы
 * и возвращает mock-данные на основе конфигурации MockService.
 *
 * Использование:
 *   export const mockVehiclesApi = vehiclesApi.injectEndpoints({
 *     endpoints: (builder) => ({
 *       ...builder.query(...)
 *     }),
 *     overrideExisting: true,
 *   });
 *
 *   // В тесте:
 *   MockService.enable();
 *   MockService.setMockData('vehicles/brands/', { data: mockBrands });
 */
export function createMockMiddleware() {
  return (baseQuery: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError>) => {
    return async (args: string | FetchArgs, api: unknown, extraOptions: unknown) => {
      if (!MockService.isEnabled()) {
        return baseQuery(args, api as Parameters<typeof baseQuery>[1], extraOptions as Parameters<typeof baseQuery>[2]);
      }

      return MockService.createMockBaseQuery()(args, api as Parameters<BaseQueryFn>[1], extraOptions as Parameters<BaseQueryFn>[2]);
    };
  };
}
