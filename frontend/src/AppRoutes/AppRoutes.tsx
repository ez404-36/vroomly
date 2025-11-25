import React from 'react';

import { routes } from '../utils/routes';
import { Route, Routes } from 'react-router-dom';
import Home from '../components/Home/Home';
import UserProfile from '../components/User/UserProfile';
import { RegisterForm } from '../components/User/RegisterForm';
import { LoginForm } from '../components/User/LoginForm';

const AppRoutes = (): React.ReactElement => {
  return (
    <Routes>
      <Route index element={<Home />} />
      <Route path={routes.userprofile} element={<UserProfile />} />
      <Route path={routes.registration} element={<RegisterForm />} />
      <Route path={routes.login} element={<LoginForm />} />
    </Routes>
  );
};

export default AppRoutes;
