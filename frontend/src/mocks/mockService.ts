/**
 * Mock Service - динамическая генерация mock-данных из TypeScript типов.
 *
 * Использование:
 * 1. Включить моки: MockService.enable()
 * 2. Определить mock-данные для эндпоинтов: MockService.setMockData(endpoint, data)
 * 3. Использовать вместо реального baseQuery в API
 */

import type { BaseQueryFn } from '@reduxjs/toolkit/query/react';
import type { FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import { createBaseQuery } from '../api/baseQuery';

// ============================================================================
// Types
// ============================================================================

/** Callback для генерации mock-данных на основе параметров запроса */
export type MockDataGenerator<T = unknown> = (args: FetchArgs | string) => T;

/** Конфигурация мока для одного эндпоинта */
export interface MockEndpointConfig<T = unknown> {
  /** Фиксированные данные (возвращаются всегда) */
  data?: T;
  /** Динамический генератор данных */
  generator?: MockDataGenerator<T>;
  /** Задержка в мс (имитация сетевого latency) */
  delay?: number;
  /** Ошибка для возврата */
  error?: FetchBaseQueryError;
}

/** Мапа моков: ключ = URL эндпоинта + метод */
type MockEndpoints = Map<string, MockEndpointConfig>;

// ============================================================================
// Mock Data Generators - генераторы для примитивных типов
// ============================================================================

const STRING_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

function randomString(length: number): string {
  let result = '';
  for (let i = 0; i < length; i++) {
    result += STRING_CHARS[Math.floor(Math.random() * STRING_CHARS.length)];
  }
  return result;
}

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomBool(): boolean {
  return Math.random() > 0.5;
}

function randomChoice<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

// ============================================================================
// Mock Data Generator from Type
// ============================================================================

/**
 * Рекурсивно генерирует mock-значение из TypeScript типа.
 * Работает только с типами, которые можно инферить в runtime.
 */
export function generateMock<T>(
  type: T,
  options: {
    required?: boolean;
    depth?: number;
    overrides?: Partial<T>;
  } = {}
): T {
  const { required = true, depth = 0, overrides = {} } = options;

  // Don't recurse too deep
  if (depth > 10) {
    return overrides as T;
  }

  // Handle overrides
  if (depth === 0 && Object.keys(overrides).length > 0) {
    return { ...overrides } as T;
  }

  // Handle null/undefined
  if (!required) {
    if (randomBool()) {
      return generateMock(type, { ...options, required: true, depth: depth + 1 });
    }
    return null as T;
  }

  const actualType = typeof type;

  // Primitive types
  if (actualType === 'string') {
    return (overrides as Record<string, unknown>)?.['' as keyof typeof overrides] as unknown as T
      ?? randomString(10) as T;
  }

  if (actualType === 'number') {
    const numType = type as unknown as number;
    // Check for enum-like numbers (1 | 2)
    if (Number.isInteger(numType) && numType >= 1 && numType <= 100) {
      return numType as T;
    }
    return (randomInt(1, 100)) as T;
  }

  if (actualType === 'boolean') {
    return randomBool() as T;
  }

  // Array type
  if (Array.isArray(type) || (actualType === 'object' && (type as unknown) instanceof Array)) {
    const arr = type as unknown as readonly unknown[];
    const elementType = arr[0] as unknown;
    const count = randomInt(1, 3);
    const result: unknown[] = [];

    for (let i = 0; i < count; i++) {
      result.push(generateMock(elementType, { ...options, depth: depth + 1 }));
    }

    return result as T;
  }

  // Object type
  if (actualType === 'object' && type !== null) {
    const obj = type as Record<string, unknown>;
    const result: Record<string, unknown> = {};

    for (const [key, value] of Object.entries(obj)) {
      const isOptional = key.endsWith('?') || key.startsWith('_');
      const actualKey = key.replace(/[?]$/, '');

      if (isOptional && !randomBool()) {
        continue;
      }

      result[actualKey] = generateMock(value, {
        ...options,
        required: !isOptional,
        depth: depth + 1,
      });
    }

    return result as T;
  }

  // Fallback
  return randomString(8) as T;
}

// ============================================================================
// Mock Service
// ============================================================================

/** Проверяет, должны ли использоваться моки (из env или runtime) */
function shouldUseMocks(): boolean {
  // Сначала проверяем runtime-флаг (явное включение/выключение)
  if (runtimeEnabled !== null) {
    return runtimeEnabled;
  }
  // Затем проверяем переменную окружения
  return import.meta.env.VITE_USE_MOCKS === 'true';
}

/** Runtime-флаг для включения/выключения моков (приоритетнее env) */
let runtimeEnabled: boolean | null = null;

class MockServiceImpl {
  private mockEndpoints: MockEndpoints = new Map();
  private warnedEndpoints: Set<string> = new Set();
  private defaultDelay = 300;

  /**
   * Включить mock-режим для всех API запросов (runtime flag)
   * Приоритетнее, чем VITE_USE_MOCKS
   */
  enable(): void {
    runtimeEnabled = true;
  }

  /**
   * Выключить mock-режим (переключиться на реальный API)
   */
  disable(): void {
    runtimeEnabled = false;
  }

  /**
   * Сбросить runtime-флаг (использовать значение из env)
   */
  resetRuntimeFlag(): void {
    runtimeEnabled = null;
  }

  /**
   * Проверить, включен ли mock-режим
   */
  isEnabled(): boolean {
    return shouldUseMocks();
  }

  /**
   * Проверить, включены ли моки через env (не учитывая runtime flag)
   */
  isEnabledFromEnv(): boolean {
    return import.meta.env.VITE_USE_MOCKS === 'true';
  }

  /**
   * Установить mock-данные для конкретного эндпоинта
   */
  setMockData<T>(endpoint: string, config: MockEndpointConfig<T>): void {
    this.mockEndpoints.set(endpoint, config as MockEndpointConfig);
  }

  /**
   * Установить mock-данные из типа (с автогенерацией)
   */
  setMockFromType<T>(endpoint: string, type: T, options?: { delay?: number; overrides?: Partial<T> }): void {
    this.mockEndpoints.set(endpoint, {
      generator: () => generateMock(type, { overrides: options?.overrides }),
      delay: options?.delay ?? this.defaultDelay,
    });
  }

  /**
   * Установить callback для ленивой генерации mock-данных
   */
  setMockGenerator<T>(endpoint: string, generator: MockDataGenerator<T>, options?: { delay?: number }): void {
    this.mockEndpoints.set(endpoint, {
      generator,
      delay: options?.delay ?? this.defaultDelay,
    });
  }

  /**
   * Удалить mock для эндпоинта
   */
  clearMock(endpoint: string): void {
    this.mockEndpoints.delete(endpoint);
  }

  /**
   * Очистить все моки
   */
  clearAll(): void {
    this.mockEndpoints.clear();
  }

  /**
   * Получить mock-конфигурацию для эндпоинта
   */
  getMockConfig(endpoint: string): MockEndpointConfig | undefined {
    return this.mockEndpoints.get(endpoint);
  }

  /**
   * Получить все определённые mock-эндпоинты
   */
  getMockEndpoints(): string[] {
    return Array.from(this.mockEndpoints.keys());
  }

/**
   * Создать mock baseQuery для RTK Query
   * @param baseUrl - базовый URL API (например 'vehicles/' или 'geo/')
   */
  createMockBaseQuery(
    baseUrl: string = ''
  ): BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> {
    const realBaseQuery = createBaseQuery(baseUrl);

    return async (args, api, extraOptions) => {
      const mocksEnabled = shouldUseMocks();

      if (!mocksEnabled) {
        return realBaseQuery(args, api, extraOptions);
      }

      // Parse endpoint from args
      const url = typeof args === 'string' ? args : args.url;
      const method = typeof args === 'object' ? (args.method ?? 'GET') : 'GET';
      // Normalize: remove leading/trailing slashes from both, then join
      const normalizedBase = baseUrl.replace(/^\/|\/$/g, '');
      const normalizedUrl = url.replace(/^\/|\/$/g, '');
      const fullUrl = `${normalizedBase}/${normalizedUrl}`.replace(/\/+/g, '/');
      const endpointKey = `${method}:${fullUrl}`;

      const mockConfig = this.mockEndpoints.get(endpointKey);

      if (!mockConfig) {
        if (!this.warnedEndpoints.has(endpointKey)) {
          this.warnedEndpoints.add(endpointKey);
          console.warn(`[MockService] No mock defined for ${endpointKey}. Falling through to real API.`);
        }
        return realBaseQuery(args, api, extraOptions);
      }

      // Handle error case
      if (mockConfig.error) {
        return { error: mockConfig.error };
      }

      // Apply delay if specified
      const delay = mockConfig.delay ?? this.defaultDelay;
      if (delay > 0) {
        await new Promise((resolve) => setTimeout(resolve, delay));
      }

      // Generate response data
      let data: unknown;
      if (mockConfig.data !== undefined) {
        data = mockConfig.data;
      } else if (mockConfig.generator) {
        data = mockConfig.generator(args);
      } else {
        data = undefined;
      }

      return { data };
    };
  }
}

// ============================================================================
// Singleton Instance
// ============================================================================

export const MockService = new MockServiceImpl();

// ============================================================================
// Pre-built Mock Configurations for Common Types
// ============================================================================

export const mockGenerators = {
  /** Генератор для строки UUID */
  uuid: (): string => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  },

  /** Генератор для email */
  email: (): string => {
    return `user${randomInt(1, 1000)}@example.com`;
  },

  /** Генератор для VIN */
  vin: (): string => {
    return randomString(17).toUpperCase();
  },

  /** Генератор для года выпуска */
  year: (min = 1990, max = 2024): number => {
    return randomInt(min, max);
  },

  /** Генератор для телефона */
  phone: (): string => {
    return `+7${randomInt(9000000000, 9999999999)}`;
  },

  /** Генератор для имени */
  name: (): string => {
    const firstNames = ['John', 'Jane', 'Alex', 'Maria', 'Sergei', 'Anna', 'Michael', 'Elena'];
    const lastNames = ['Smith', 'Johnson', 'Doe', 'Petrov', 'Ivanov', 'Kuznetsov', 'Sokolov', 'Popova'];
    return `${randomChoice(firstNames)} ${randomChoice(lastNames)}`;
  },

  /** Генератор для названия автомобиля */
  vehicleName: (): string => {
    const brands = ['Toyota', 'BMW', 'Mercedes', 'Audi', 'Honda', 'Ford', 'Volkswagen', 'Hyundai'];
    const models = ['Camry', 'X5', 'E-Class', 'A4', 'Civic', 'Focus', 'Golf', 'Tucson'];
    return `${randomChoice(brands)} ${randomChoice(models)}`;
  },

  /** Генератор для цвета */
  color: (): string => {
    const colors = ['Black', 'White', 'Silver', 'Blue', 'Red', 'Green', 'Gray', 'Brown'];
    return randomChoice(colors);
  },

  /** Создать delay helper */
  delay: (ms: number): Promise<void> => {
    return new Promise((resolve) => setTimeout(resolve, ms));
  },
};
