import React from 'react';

import { Route, Routes } from 'react-router-dom';

import ProtectedRoute from '../components/ProtectedRoute/ProtectedRoute';
import { routes } from '../utils/routes';
import Home from '../components/Home/Home';
import UserProfile from '../components/User/UserProfile';
import { AddVehiclePage } from '../pages/AddVehiclePage';
import { RegistrationPage } from '../pages/RegistrationPage';
import { LoginPage } from '../pages/LoginPage';
import { SettingsPage } from '../pages/SettingsPage';
import GaragePage from '../pages/GaragePage';

const AppRoutes = (): React.ReactElement => {
  return (
    <Routes>
      <Route
        index
        element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
        }
      />
      <Route path={routes.garage} element={<GaragePage />} />
      <Route path={routes.userprofile} element={<UserProfile />} />
      <Route path={routes.registration} element={<RegistrationPage />} />
      <Route path={routes.login} element={<LoginPage />} />
      <Route path={routes.settings} element={<SettingsPage />} />
      <Route path={routes.addVehicle} element={<AddVehiclePage />} />
    </Routes>
  );
};

export default AppRoutes;
