import { useForm } from 'react-hook-form';
import { Button, Flex, Text, TextInput, PasswordInput } from '../../ui';
import { useNavigate } from 'react-router-dom';
import { useLoginSubmit } from '../../hooks/useAuthSubmit';

interface LoginDataForm {
  username: string;
  password: string;
}

export const LoginForm = () => {
  const navigate = useNavigate();
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
    <form
      onSubmit={handleSubmit(submit)}
      style={{ maxWidth: 400, margin: '0 auto' }}
    >
      <TextInput
        label="Логин или Email"
        placeholder="Введите логин или email"
        {...register('username', {
          required: 'Введите логин или email',
        })}
        error={errors.username?.message}
        mt="8px"
      />

      <PasswordInput
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
        mt="8px"
      />

      {error && (
        <Text c="red" mt="xs">
          {error}
        </Text>
      )}

      <Flex direction="column" gap="sm" mt="8px">
        <Button type="submit" loading={isLoading}>
          Войти
        </Button>
        <Button onClick={() => navigate(-1)}>Назад</Button>
      </Flex>
    </form>
  );
};
