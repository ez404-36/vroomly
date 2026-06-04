import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  isAuthenticated: boolean;
}

const getInitialAuthState = (): boolean => {
  const token = localStorage.getItem('access_token');
  return token !== null && token !== '';
};

const initialState: AuthState = {
  isAuthenticated: getInitialAuthState(),
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuthenticated: (state, action: PayloadAction<boolean>) => {
      state.isAuthenticated = action.payload;
    },
    /**
     * Успешный вход: сохраняет токен и помечает сессию аутентифицированной.
     * Запись токена инкапсулирована в auth-слое (симметрично `logout`).
     */
    loginSucceeded: (state, action: PayloadAction<string>) => {
      localStorage.setItem('access_token', action.payload);
      state.isAuthenticated = true;
    },
    logout: (state) => {
      localStorage.removeItem('access_token');
      state.isAuthenticated = false;
    },
  },
});

export const { setAuthenticated, loginSucceeded, logout } = authSlice.actions;
export default authSlice.reducer;
