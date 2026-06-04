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
import { useLoginSubmit } from '../hooks/useAuthSubmit';

export interface LoginDataForm {
  username: string;
  password: string;
}

export const LoginPage = () => {
  const { submit, isLoading, error } = useLoginSubmit();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginDataForm>({
    defaultValues: { username: '', password: '' },
    mode: 'onChange',
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

        <Paper p="xl" radius="md" style={{ flex: 1 }}>
          <Stack>
            <Title order={2}>Вход</Title>
            <form onSubmit={handleSubmit(submit)}>
              <Stack>
                <TextInput
                  label="Username or Email"
                  placeholder="Введите username или email"
                  {...register('username', {
                    required: 'Введите username или email',
                  })}
                  error={errors.username?.message}
                />
                <PasswordInput
                  label="Password"
                  placeholder="Введите пароль"
                  {...register('password', {
                    required: 'Введите пароль',
                    minLength: {
                      value: 6,
                      message: 'Минимум 6 символов',
                    },
                  })}
                  error={errors.password?.message}
                />

                {error && (
                  <Text c="red" size="sm">
                    {error}
                  </Text>
                )}

                <Button type="submit" loading={isLoading} fullWidth mt="md">
                  Войти
                </Button>
              </Stack>
            </form>

            <Text size="sm" ta="center">
              Нет аккаунта?{' '}
              <Link
                to={routes.registration}
                className="text-(--color-primary) hover:underline"
              >
                Зарегистрироваться
              </Link>
            </Text>
          </Stack>
        </Paper>
      </div>
    </div>
  );
};
