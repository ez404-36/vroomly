import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { TextInput, PasswordInput, Button, Flex, Text } from '@mantine/core';

import type { RegistrationDataForm } from '../../types/schemas';

const User = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<RegistrationDataForm>({
    defaultValues: {
      login: '',
      email: '',
      password: '',
      confirm_password: '',
    },
    mode: 'onChange', // проверка при каждом изменении
    reValidateMode: 'onChange', // повторная проверка при изменениях
  });

  const toggleMode = () => {
    setIsLogin((prev) => !prev);
    reset(); // очищаем поля при переключении
  };

  const onSubmit = (data) => {
    if (isLogin) {
      console.log('Авторизация:', {
        login: data.login,
        password: data.password,
      });
    } else {
      if (data.password !== data.confirm_password) {
        alert('Пароли не совпадают');
        return;
      }
      console.log('Регистрация:', {
        login: data.login,
        email: data.email,
        password: data.password,
      });
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: 20 }}>
      <h2>{isLogin ? 'Вход' : 'Регистрация'}</h2>
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Email Input */}
        {isLogin ? (
          <TextInput
            label="Логин или Email"
            placeholder="Введите логин или email"
            {...register('login', { required: 'Введите логин или email' })}
            error={errors.login?.message}
            mt="sm"
          />
        ) : (
          <>
            <TextInput
              label="Логин"
              placeholder="Введите логин"
              {...register('login', { required: 'Введите логин' })}
              error={errors.login?.message}
              mt="sm"
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
              mt="sm"
            />
          </>
        )}

        {/* Пароль */}
        <PasswordInput
          label="Пароль"
          placeholder="Введите пароль"
          {...register('password', {
            required: 'Введите пароль',
            minLength: { value: 6, message: 'Минимум 6 символов' },
          })}
          error={errors.password?.message}
          mt="sm"
        />

        {/* Подтверждение пароля — только при регистрации */}
        {!isLogin && (
          <PasswordInput
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
        )}

        <Flex direction="column" mt="sm" gap="sm">
          {/* Основная кнопка */}
          <Button type="submit" mt="sm">
            {isLogin ? 'Войти' : 'Зарегистрироваться'}
          </Button>

          <Text
            onClick={toggleMode}
            ta="center"
            c="blue"
            style={{ cursor: 'pointer' }}
          >
            {isLogin ? 'Пройти регистрацию' : 'У меня уже есть аккаунт'}
          </Text>

          {/* Кнопка назад */}
          <Button onClick={() => navigate(-1)}>Назад</Button>
        </Flex>
      </form>
    </div>
  );
};

export default User;
