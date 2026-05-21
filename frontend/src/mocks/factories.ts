/**
 * Pre-built mock factories for common schema types.
 *
 * Использование:
 *   // Включить моки через env: VITE_USE_MOCKS=true
 *   // Или программно: MockService.enable()
 *
 *   import { MockService } from '@/mocks';
 *   import { mockSchemas } from '@/mocks/factories';
 *
 *   // Установить mock для эндпоинта
 *   MockService.setMockGenerator('vehicles/brands/', () => mockSchemas.vehicleBrands(5));
 */

import { mockGenerators } from './mockService';
import type {
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleSeriesDetailSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
  ChoiceFieldSchema,
  ChoiceFieldWithParentSchema,
  CurrentUser,
  UserVehicleDetailSchema,
  CountryDetailSchema,
  CarInfoByVinDataSchema,
} from '../types/schema-types';

/** Генератор для VehicleBrandDetailSchema */
export function vehicleBrand(overrides?: Partial<VehicleBrandDetailSchema>): VehicleBrandDetailSchema {
  return {
    id: mockGenerators.uuid(),
    countryId: 'US',
    code: 'TOY',
    name: mockGenerators.vehicleName().split(' ')[0],
    originalName: null,
    ...overrides,
  };
}

/** Генератор для VehicleBrandDetailSchema[] */
export function vehicleBrands(count: number, overrides?: Partial<VehicleBrandDetailSchema>): VehicleBrandDetailSchema[] {
  return Array.from({ length: count }, () => vehicleBrand(overrides));
}

/** Генератор для VehicleSeriesListSchema */
export function vehicleSeriesList(overrides?: Partial<VehicleSeriesListSchema>): VehicleSeriesListSchema {
  const brandId = overrides?.brandId ?? mockGenerators.uuid();
  return {
    id: mockGenerators.uuid(),
    name: mockGenerators.vehicleName().split(' ')[1] ?? 'Model',
    brandId,
    ...overrides,
  };
}

/** Генератор для VehicleSeriesListSchema[] */
export function vehicleSeriesListArray(count: number, brandId?: string): VehicleSeriesListSchema[] {
  return Array.from({ length: count }, (_, i) => vehicleSeriesList({
    brandId: brandId ?? mockGenerators.uuid(),
    name: `Model ${i + 1}`,
  }));
}

/** Генератор для VehicleSeriesDetailSchema */
export function vehicleSeriesDetail(overrides?: Partial<VehicleSeriesDetailSchema>): VehicleSeriesDetailSchema {
  return {
    id: mockGenerators.uuid(),
    name: 'Corolla',
    brand: vehicleBrand(),
    ...overrides,
  };
}

/** Генератор для VehicleGenerationListSchema */
export function vehicleGeneration(overrides?: Partial<VehicleGenerationListSchema>): VehicleGenerationListSchema {
  return {
    id: mockGenerators.uuid(),
    name: `Generation ${Math.floor(Math.random() * 10) + 1}`,
    seriesId: overrides?.seriesId ?? mockGenerators.uuid(),
    startYear: mockGenerators.year(2010, 2018),
    endYear: Math.random() > 0.5 ? mockGenerators.year(2018, 2024) : null,
    ...overrides,
  };
}

/** Генератор для VehicleGenerationListSchema[] */
export function vehicleGenerations(count: number, seriesId?: string): VehicleGenerationListSchema[] {
  return Array.from({ length: count }, () => vehicleGeneration({ seriesId }));
}

/** Генератор для VehicleTrimListSchema */
export function vehicleTrim(overrides?: Partial<VehicleTrimListSchema>): VehicleTrimListSchema {
  return {
    id: mockGenerators.uuid(),
    name: `Trim ${['Base', 'Comfort', 'Luxury', 'Sport'][Math.floor(Math.random() * 4)]}`,
    generationId: overrides?.generationId ?? mockGenerators.uuid(),
    ...overrides,
  };
}

/** Генератор для VehicleTrimListSchema[] */
export function vehicleTrims(count: number, generationId?: string): VehicleTrimListSchema[] {
  return Array.from({ length: count }, () => vehicleTrim({ generationId }));
}

/** Генератор для ChoiceFieldSchema */
export function choiceField(overrides?: Partial<ChoiceFieldSchema>): ChoiceFieldSchema {
  return {
    id: mockGenerators.uuid(),
    name: mockGenerators.vehicleName(),
    ...overrides,
  };
}

/** Генератор для ChoiceFieldSchema[] */
export function choiceFields(count: number): ChoiceFieldSchema[] {
  return Array.from({ length: count }, () => choiceField());
}

/** Генератор для ChoiceFieldWithParentSchema */
export function choiceFieldWithParent(overrides?: Partial<ChoiceFieldWithParentSchema>): ChoiceFieldWithParentSchema {
  const parent = choiceField();
  return {
    id: mockGenerators.uuid(),
    name: `Configuration ${Math.floor(Math.random() * 100)}`,
    parent,
    ...overrides,
  };
}

/** Генератор для ChoiceFieldWithParentSchema[] */
export function choiceFieldsWithParent(count: number): ChoiceFieldWithParentSchema[] {
  return Array.from({ length: count }, () => choiceFieldWithParent());
}

/** Генератор для CurrentUser */
export function currentUser(overrides?: Partial<CurrentUser>): CurrentUser {
  return {
    id: mockGenerators.uuid(),
    login: `user_${Math.floor(Math.random() * 1000)}`,
    email: mockGenerators.email(),
    name: mockGenerators.name().split(' ')[0],
    surname: mockGenerators.name().split(' ')[1],
    birthDate: null,
    countryId: null,
    ...overrides,
  };
}

/** Генератор для UserVehicleDetailSchema */
export function userVehicleDetail(overrides?: Partial<UserVehicleDetailSchema>): UserVehicleDetailSchema {
  return {
    id: mockGenerators.uuid(),
    vehicle_id: mockGenerators.uuid(),
    user_id: mockGenerators.uuid(),
    mileage: Math.floor(Math.random() * 200000),
    is_mileage_in_miles: false,
    avg_fuel_consumption: Math.round(Math.random() * 15 * 10) / 10,
    brand: 'Toyota',
    series: 'Camry',
    generation: 'X50',
    trim: 'Comfort',
    production_year: mockGenerators.year(2018, 2023),
    color: mockGenerators.color(),
    ...overrides,
  };
}

/** Генератор для UserVehicleDetailSchema[] */
export function userVehicles(count: number): UserVehicleDetailSchema[] {
  return Array.from({ length: count }, () => userVehicleDetail());
}

/** Генератор для CountryDetailSchema */
export function countryDetail(overrides?: Partial<CountryDetailSchema>): CountryDetailSchema {
  const countries = [
    { id: 'US', name: 'United States', shortName: 'USA' },
    { id: 'DE', name: 'Germany', shortName: 'GER' },
    { id: 'JP', name: 'Japan', shortName: 'JPN' },
    { id: 'RU', name: 'Russia', shortName: 'RUS' },
    { id: 'GB', name: 'United Kingdom', shortName: 'UK' },
  ];
  const country = countries[Math.floor(Math.random() * countries.length)];
  return {
    id: country.id,
    name: country.name,
    shortName: country.shortName,
    ...overrides,
  };
}

/** Генератор для CountryDetailSchema[] */
export function countries(count: number): CountryDetailSchema[] {
  const allCountries = [
    { id: 'US', name: 'United States', shortName: 'USA' },
    { id: 'DE', name: 'Germany', shortName: 'GER' },
    { id: 'JP', name: 'Japan', shortName: 'JPN' },
    { id: 'RU', name: 'Russia', shortName: 'RUS' },
    { id: 'GB', name: 'United Kingdom', shortName: 'UK' },
    { id: 'FR', name: 'France', shortName: 'FRA' },
    { id: 'IT', name: 'Italy', shortName: 'ITA' },
    { id: 'CN', name: 'China', shortName: 'CHN' },
    { id: 'KR', name: 'South Korea', shortName: 'KOR' },
    { id: 'ES', name: 'Spain', shortName: 'ESP' },
  ];
  return allCountries.slice(0, count);
}

/** Генератор для CarInfoByVinDataSchema */
export function carInfoByVin(overrides?: Partial<CarInfoByVinDataSchema>): CarInfoByVinDataSchema {
  return {
    model: 'Camry',
    year: mockGenerators.year(2018, 2023),
    frame: 'AWVZZZ',
    vin: mockGenerators.vin(),
    carplate: `A${Math.floor(Math.random() * 1000)}MP`,
    color: mockGenerators.color(),
    type: 'Sedan',
    volume: Math.round(Math.random() * 3 * 10) / 10,
    power: Math.floor(Math.random() * 200) + 100,
    frame_id: Math.floor(Math.random() * 10000),
    vehicle_type: 'passenger',
    ...overrides,
  };
}