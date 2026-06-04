import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useLoginMutation, useRegisterMutation } from '../api/authApi';
import { type AppDispatch } from '../store/store';
import { loginSucceeded, setAuthenticated } from '../store/authSlice';
import { routes } from '../utils/routes';

/**
 * Приводит ошибку мутации к строке для отображения.
 *
 * `transformErrorResponse: formatApiError` уже возвращает готовую строку для
 * ответов API; остаётся обработать ветку `SerializedError` (сетевые/иные сбои).
 */
function toErrorMessage(error: unknown): string | undefined {
  if (error == null) {
    return undefined;
  }
  if (typeof error === 'string') {
    return error;
  }
  if (typeof error === 'object' && 'message' in error) {
    const message = (error as { message?: unknown }).message;
    return typeof message === 'string' ? message : undefined;
  }
  return undefined;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  login: string;
  email: string;
  password: string;
  confirm_password: string;
}

/**
 * Логика входа: мутация + сохранение токена (через auth-слой) + навигация.
 *
 * @param redirectTo путь после успешного входа (по умолчанию `/`).
 */
export function useLoginSubmit(redirectTo = '/') {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [loginUser, { isLoading, error }] = useLoginMutation();

  const submit = async (credentials: LoginCredentials) => {
    try {
      const result = await loginUser(credentials).unwrap();
      dispatch(loginSucceeded(result.access_token));
      navigate(redirectTo);
    } catch {
      // Ошибка доступна вызывающему через `error`; UI её отображает.
    }
  };

  return { submit, isLoading, error: toErrorMessage(error) };
}

/**
 * Логика регистрации: мутация + пометка аутентификации + навигация.
 *
 * @param redirectTo путь после успешной регистрации (по умолчанию — страница входа).
 */
export function useRegisterSubmit(redirectTo: string = routes.login) {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [registerUser, { isLoading, error }] = useRegisterMutation();

  const submit = async (credentials: RegisterCredentials) => {
    try {
      await registerUser(credentials).unwrap();
      dispatch(setAuthenticated(true));
      navigate(redirectTo);
    } catch {
      // Ошибка доступна вызывающему через `error`; UI её отображает.
    }
  };

  return { submit, isLoading, error: toErrorMessage(error) };
}
