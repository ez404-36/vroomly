import {
  Paper,
  Title,
  Text,
  TextInput,
  PasswordInput,
  Button,
  Stack,
} from '../ui';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { routes } from '../utils/routes';
import type { RegistrationDataForm } from '../types/schema-types';
import { useRegisterSubmit } from '../hooks/useAuthSubmit';

export const RegistrationPage = () => {
  const { submit, isLoading, error } = useRegisterSubmit();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegistrationDataForm>({
    defaultValues: { login: '', email: '', password: '', confirm_password: '' },
    mode: 'onChange',
    reValidateMode: 'onChange',
  });

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '40px 24px',
      }}
    >
      <div
        style={{
          display: 'flex',
          gap: '24px',
          width: '100%',
          alignItems: 'stretch',
        }}
      >
        <Paper p="xl" radius="md" style={{ flex: 1 }}>
          <Stack>
            <Title order={2}>Регистрация</Title>
            <form onSubmit={handleSubmit(submit)}>
              <Stack>
                <TextInput
                  label="Username"
                  placeholder="Введите username"
                  {...register('login', { required: 'Введите username' })}
                  error={errors.login?.message}
                />
                <TextInput
                  label="Email"
                  placeholder="Введите ваш email"
                  {...register('email', {
                    required: 'Введите email',
                    pattern: {
                      value: /^\S+@\S+$/i,
                      message: 'Некорректный email',
                    },
                  })}
                  error={errors.email?.message}
                />
                <PasswordInput
                  label="Password"
                  placeholder="Введите пароль"
                  {...register('password', {
                    required: 'Введите пароль',
                    minLength: { value: 6, message: 'Минимум 6 символов' },
                  })}
                  error={errors.password?.message}
                />
                <PasswordInput
                  label="Confirm Password"
                  placeholder="Повторите пароль"
                  {...register('confirm_password', {
                    required: 'Подтвердите пароль',
                    validate: (value) =>
                      value === watch('password') || 'Пароли не совпадают',
                  })}
                  error={errors.confirm_password?.message}
                />

                {error && (
                  <Text c="red" size="sm">
                    {error}
                  </Text>
                )}

                <Button type="submit" loading={isLoading} fullWidth mt="md">
                  Создать аккаунт
                </Button>
              </Stack>
            </form>

            <Text size="sm" ta="center">
              У меня уже есть аккаунт{' '}
              <Link
                to={routes.login}
                className="text-(--color-primary) hover:underline"
              >
                Войти
              </Link>
            </Text>
          </Stack>
        </Paper>

        <Paper
          p="xl"
          radius="md"
          style={{ flex: 1, background: 'var(--color-bg-muted)' }}
        >
          <Stack justify="center" style={{ height: '100%' }}>
            <Title order={1}>Vroomly</Title>
            <Text size="xl">Ваш автомобильный помощник</Text>
          </Stack>
        </Paper>
      </div>
    </div>
  );
};
