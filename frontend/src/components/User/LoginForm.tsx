import { useForm } from 'react-hook-form';
import { Button, Flex, Text } from '../../ui';
import { TextInput as MantineTextInput, PasswordInput as MantinePasswordInput } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useLoginMutation } from '../../api/authApi';

// Интерфейс для формы логина
interface LoginDataForm {
  username: string;
  password: string;
}

export const LoginForm = () => {
  const navigate = useNavigate();
  const [loginUser, { isLoading, error }] = useLoginMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginDataForm>({
    defaultValues: { username: '', password: '' },
    mode: 'onChange',
  });

  const onSubmit = async (data: LoginDataForm) => {
    const payload = {
      username: data.username, // login или email
      password: data.password,
    };

    try {
      const res = await loginUser(payload).unwrap();
      console.log('LOGIN SUCCESS:', res);
      navigate('/');
    } catch (err) {
      console.error('Ошибка логина:', err);
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      style={{ maxWidth: 400, margin: '0 auto' }}
    >
      <MantineTextInput
        label="Логин или Email"
        placeholder="Введите логин или email"
        {...register('username', {
          required: 'Введите логин или email',
        })}
        error={errors.username?.message}
        mt="sm"
      />

      <MantinePasswordInput
        label="Пароль"
        placeholder="Введите пароль"
        {...register('password', {
          required: 'Введите пароль',
          minLength: {
            value: 6,
            message: 'Минимум 6 символов',
          },
        })}
        error={errors.password?.message}
        mt="sm"
      />

      {error && (
        <Text color="red" mt="xs">
          {JSON.stringify(error, null, 2)}
        </Text>
      )}

      <Flex direction="column" gap="sm" mt="sm">
        <Button type="submit" loading={isLoading}>
          Войти
        </Button>
        <Button onClick={() => navigate(-1)}>Назад</Button>
      </Flex>
    </form>
  );
};
