/**
 * Демо-конфигурация моков для показа возможностей MockService.
 *
 * Этот файл можно использовать для тестирования или как референс
 * для создания собственных mock-конфигураций.
 */

import { MockService, mockSchemas } from './index';
import type {
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
  ChoiceFieldSchema,
  CountryDetailSchema,
} from '../types/schema-types';

/** Настроить все vehicle-эндпоинты на моки */
export function setupVehicleMocks(): void {
  MockService.setMockGenerator<VehicleBrandDetailSchema[]>(
    'GET:vehicles/brands',
    () => mockSchemas.vehicleBrands(8),
    { delay: 200 }
  );

  MockService.setMockGenerator<VehicleSeriesListSchema[]>(
    'GET:vehicles/series',
    () => mockSchemas.vehicleSeriesListArray(5),
    { delay: 150 }
  );

  MockService.setMockGenerator<VehicleGenerationListSchema[]>(
    'GET:vehicles/generation',
    () => mockSchemas.vehicleGenerations(4),
    { delay: 150 }
  );

  MockService.setMockGenerator<VehicleTrimListSchema[]>(
    'GET:vehicles/trim',
    () => mockSchemas.vehicleTrims(3),
    { delay: 150 }
  );

  MockService.setMockGenerator<ChoiceFieldSchema[]>(
    'GET:vehicles/vehicle/types/choices',
    () => [
      { id: '1', name: 'Легковой' },
      { id: '2', name: 'Грузовой' },
    ]
  );

  console.log('[MockService] Vehicle mocks configured');
}

/** Настроить geo-эндпоинты на моки */
export function setupGeoMocks(): void {
  MockService.setMockGenerator<CountryDetailSchema[]>(
    'GET:geo/country',
    () => mockSchemas.countries(10)
  );

  console.log('[MockService] Geo mocks configured');
}

/** Настроить все моки разом */
export function setupAllMocks(): void {
  setupVehicleMocks();
  setupGeoMocks();
  console.log('[MockService] All mocks configured');
}

/** Очистить все моки */
export function clearAllMocks(): void {
  MockService.clearAll();
  console.log('[MockService] All mocks cleared');
}