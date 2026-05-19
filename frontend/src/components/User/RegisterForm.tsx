import { useForm } from 'react-hook-form';
import { Button, Flex, Text } from '../../ui';
import { TextInput as MantineTextInput, PasswordInput as MantinePasswordInput } from '@mantine/core';
import { useRegisterMutation } from '../../api/authApi';
import { useNavigate } from 'react-router-dom';

interface RegistrationDataForm {
  login: string;
  email: string;
  password: string;
  confirm_password: string;
}

export const RegisterForm = () => {
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
      navigate('/');
    } catch (err) {
      console.error('Ошибка регистрации:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <MantineTextInput
        label="Логин"
        placeholder="Введите логин"
        {...register('login', { required: 'Введите логин' })}
        error={errors.login?.message}
        mt="sm"
      />
      <MantineTextInput
        label="Email"
        placeholder="Введите ваш email"
        {...register('email', {
          required: 'Введите email',
          pattern: { value: /^\S+@\S+$/i, message: 'Некорректный email' },
        })}
        error={errors.email?.message}
        mt="sm"
      />
      <MantinePasswordInput
        label="Пароль"
        placeholder="Введите пароль"
        {...register('password', {
          required: 'Введите пароль',
          minLength: { value: 6, message: 'Минимум 6 символов' },
        })}
        error={errors.password?.message}
        mt="sm"
      />
      <MantinePasswordInput
        label="Подтверждение пароля"
        placeholder="Повторите пароль"
        {...register('confirm_password', {
          required: 'Подтвердите пароль',
          validate: (value) =>
            value === watch('password') || 'Пароли не совпадают',
        })}
        error={errors.confirm_password?.message}
        mt="sm"
      />
      <Flex mt="sm">
        <Button type="submit" loading={isLoading}>
          Зарегистрироваться
        </Button>
      </Flex>

      {error && (
        <Text color="red" mt="xs">
          {JSON.stringify(error, null, 2)}
        </Text>
      )}

      <Button mt="sm" onClick={() => navigate(-1)}>
        Назад
      </Button>
    </form>
  );
};
