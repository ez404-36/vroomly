import { configureStore } from '@reduxjs/toolkit';
import { authApi } from '../api/authApi';
import { vehiclesApi } from '../api/vehiclesApi';
import { geoApi } from '../api/geoApi';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
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

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
