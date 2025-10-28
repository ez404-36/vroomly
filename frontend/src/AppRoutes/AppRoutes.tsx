import React from 'react';

import { routes } from '../utils/routes';
import { Route, Routes } from 'react-router-dom';
import Home from '../components/Home/Home';
import Profile from '../components/User/User';

const AppRoutes = (): React.ReactElement => {
  return (
    <Routes>
      <Route index element={<Home />} />
      <Route path={routes.profile} element={<Profile />} />
    </Routes>
  );
};

export default AppRoutes;
