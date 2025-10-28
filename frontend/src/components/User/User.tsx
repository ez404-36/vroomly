import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextInput, PasswordInput, Button } from '@mantine/core';

const User = () => {
  const navigate = useNavigate();

  // состояние для инпутов
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: 20 }}>
      <h2>User Здесь!</h2>

      {/* Email Input */}
      <TextInput
        label="Email"
        placeholder="Введите ваш email"
        value={email}
        onChange={(event) => setEmail(event.currentTarget.value)}
        mt="md"
      />

      {/* Password Input */}
      <PasswordInput
        label="Пароль"
        placeholder="Введите пароль"
        value={password}
        onChange={(event) => setPassword(event.currentTarget.value)}
        mt="md"
      />

      {/* Кнопка назад */}
      <Button onClick={() => navigate(-1)} mt="lg">
        Назад
      </Button>
    </div>
  );
};

export default User;
