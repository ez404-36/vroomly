import { useState } from 'react';
import { Button, Flex } from '../../ui';

import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

const UserProfile = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: 20 }}>
      <h2>{isLogin ? 'Вход' : 'Регистрация'}</h2>

      {/* Показываем нужную форму */}
      {isLogin ? <LoginForm /> : <RegisterForm />}

      {/* Переключение */}
      <Flex justify="center" mt="md">
        <Button variant="subtle" onClick={() => setIsLogin((prev) => !prev)}>
          {isLogin
            ? 'Нет аккаунта? Зарегистрироваться'
            : 'Уже есть аккаунт? Войти'}
        </Button>
      </Flex>
    </div>
  );
};

export default UserProfile;
