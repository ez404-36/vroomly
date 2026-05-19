import { Container, Paper, Title, Text, TextInput, PasswordInput, Button, Stack } from '../ui';
import { useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { routes } from '../utils/routes';
import { useRegisterMutation } from '../api/authApi';
import type { RegistrationDataForm } from '../types/schema-types';
import { useNavigate } from 'react-router-dom';
import { type AppDispatch } from '../store/store';
import { setAuthenticated } from '../store/authSlice';

export const RegistrationPage = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [registerUser, { isLoading, error }] = useRegisterMutation();

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

  const onSubmit = async (data: RegistrationDataForm) => {
    try {
      const res = await registerUser({
        login: data.login,
        email: data.email,
        password: data.password,
        confirm_password: data.confirm_password,
      }).unwrap();

      console.log('REGISTER SUCCESS:', res);
      dispatch(setAuthenticated(true));
      navigate(routes.login);
    } catch (err) {
      console.error('Ошибка регистрации:', err);
    }
  };

  return (
    <Container size={1200} py="80px">
      <div className="flex gap-6 items-stretch">
        <Paper p="xl" radius="md" style={{ flex: 1 }}>
          <Stack>
            <Title order={2}>Регистрация</Title>
            <form onSubmit={handleSubmit(onSubmit)}>
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
                    {JSON.stringify(error, null, 2)}
                  </Text>
                )}

                <Button type="submit" loading={isLoading} fullWidth mt="md">
                  Создать аккаунт
                </Button>
              </Stack>
            </form>

            <Text size="sm" ta="center">
              У меня уже есть аккаунт{' '}
              <Link to={routes.login} className="text-(--color-primary) hover:underline">
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
    </Container>
  );
};
