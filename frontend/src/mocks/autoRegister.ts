/**
 * Автоматическая регистрация моков при импорте.
 * Срабатывает только если VITE_USE_MOCKS=true.
 */

import { MockService } from './mockService';
import * as mockSchemas from './factories';
import type {
  VehicleBrandDetailSchema,
  VehicleSeriesListSchema,
  VehicleGenerationListSchema,
  VehicleTrimListSchema,
  ChoiceFieldSchema,
  CountryDetailSchema,
  CurrentUser,
  UserVehicleDetailSchema,
} from '../types/schema-types';

/** Регистрация моков для accounts API */
function registerAccountsMocks(): void {
  MockService.setMockGenerator<CurrentUser>(
    'GET:accounts/me',
    () => mockSchemas.currentUser({
      id: '550e8400-e29b-41d4-a716-446655440000',
      login: 'test_user',
      email: 'test@example.com',
      name: 'Test',
      surname: 'User',
    }),
    { delay: 100 }
  );
}

/** Регистрация моков для vehicle API */
function registerVehicleMocks(): void {
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

  // User vehicles
  MockService.setMockGenerator<UserVehicleDetailSchema[]>(
    'GET:vehicles/user-vehicles',
    () => mockSchemas.userVehicles(3),
    { delay: 150 }
  );
}

/** Регистрация моков для geo API */
function registerGeoMocks(): void {
  MockService.setMockGenerator<CountryDetailSchema[]>(
    'GET:geo/country',
    () => mockSchemas.countries(10),
    { delay: 150 }
  );
}

// Регистрируем моки при импорте модуля, если они включены
if (MockService.isEnabledFromEnv()) {
  registerAccountsMocks();
  registerVehicleMocks();
  registerGeoMocks();
  console.log('[MockService] Auto-registered mocks for all APIs');
}
