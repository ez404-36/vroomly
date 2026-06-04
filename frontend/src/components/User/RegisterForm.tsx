import { useForm } from 'react-hook-form';
import { Button, Flex, Text, TextInput, PasswordInput } from '../../ui';
import { useNavigate } from 'react-router-dom';
import { useRegisterSubmit } from '../../hooks/useAuthSubmit';

interface RegistrationDataForm {
  login: string;
  email: string;
  password: string;
  confirm_password: string;
}

export const RegisterForm = () => {
  const navigate = useNavigate();
  const { submit, isLoading, error } = useRegisterSubmit('/');

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
    <form onSubmit={handleSubmit(submit)}>
      <TextInput
        label="Логин"
        placeholder="Введите логин"
        {...register('login', { required: 'Введите логин' })}
        error={errors.login?.message}
        mt="8px"
      />
      <TextInput
        label="Email"
        placeholder="Введите ваш email"
        {...register('email', {
          required: 'Введите email',
          pattern: { value: /^\S+@\S+$/i, message: 'Некорректный email' },
        })}
        error={errors.email?.message}
        mt="8px"
      />
      <PasswordInput
        label="Пароль"
        placeholder="Введите пароль"
        {...register('password', {
          required: 'Введите пароль',
          minLength: { value: 6, message: 'Минимум 6 символов' },
        })}
        error={errors.password?.message}
        mt="8px"
      />
      <PasswordInput
        label="Подтверждение пароля"
        placeholder="Повторите пароль"
        {...register('confirm_password', {
          required: 'Подтвердите пароль',
          validate: (value) =>
            value === watch('password') || 'Пароли не совпадают',
        })}
        error={errors.confirm_password?.message}
        mt="8px"
      />
      <Flex mt="8px">
        <Button type="submit" loading={isLoading}>
          Зарегистрироваться
        </Button>
      </Flex>

      {error && (
        <Text c="red" mt="xs">
          {error}
        </Text>
      )}

      <Button mt="8px" onClick={() => navigate(-1)}>
        Назад
      </Button>
    </form>
  );
};
