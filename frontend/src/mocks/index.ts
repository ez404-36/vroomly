/**
 * Mocks module - utilities for creating mock data from TypeScript types.
 *
 * Переключение между моками и реальным API:
 * - Через env: VITE_USE_MOCKS=true в frontend/.env
 * - Программно: MockService.enable() / MockService.disable()
 */

export { MockService, mockGenerators, generateMock } from './mockService';
export type { MockDataGenerator, MockEndpointConfig } from './mockService';
export {
  createMockedBaseQuery,
  createMockEndpoint,
  createMockMiddleware,
} from './mockApiFactory';
export * as mockSchemas from './factories';
export { setupVehicleMocks, setupGeoMocks, setupAllMocks, clearAllMocks } from './demoConfig';
export * from './autoRegister';
export { generateReminders, generateRecommendations, generateGarageMocks } from './garageMocks';
export type { Reminder, Recommendation } from './garageMocks';