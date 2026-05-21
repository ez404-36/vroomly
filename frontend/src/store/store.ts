import { configureStore } from '@reduxjs/toolkit';
import { authApi } from '../api/authApi';
import { vehiclesApi } from '../api/vehiclesApi';
import { geoApi } from '../api/geoApi';
import authReducer from './authSlice';
import layoutReducer from './layoutSlice';

// Для демонстрации моков настроим vehicle endpoints при инициализации
import('../mocks/demoConfig').then(({ setupVehicleMocks, setupGeoMocks }) => {
  import('../mocks').then(({ MockService }) => {
    if (MockService.isEnabledFromEnv()) {
      setupVehicleMocks();
      setupGeoMocks();
      console.log('[MockService] Demo mocks configured');
    }
  });
});

export const store = configureStore({
  reducer: {
    auth: authReducer,
    layout: layoutReducer,
    [authApi.reducerPath]: authApi.reducer,
    [vehiclesApi.reducerPath]: vehiclesApi.reducer,
    [geoApi.reducerPath]: geoApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      authApi.middleware,
      vehiclesApi.middleware,
      geoApi.middleware,
    ),
});

// Логируем состояние моков при инициализации
import('../mocks').then(({ MockService }) => {
  if (MockService.isEnabledFromEnv()) {
    console.log('[MockService] Mocks enabled via VITE_USE_MOCKS=true');
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
