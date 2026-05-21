import { Route, Routes } from 'react-router-dom';
import AppLayout from './AppLayout/AppLayout';
import ProtectedRoute from './ProtectedRoute/ProtectedRoute';
import { routes } from '../utils/routes';
import SmartRedirect from './SmartRedirect/SmartRedirect';
import UserProfile from './User/UserProfile';
import { LoginPage } from '../pages/LoginPage';
import { RegistrationPage } from '../pages/RegistrationPage';
import { SettingsPage } from '../pages/SettingsPage';
import { AddVehiclePage } from '../pages/AddVehiclePage';
import GaragePage from '../pages/GaragePage';
import { AboutPage } from '../pages/AboutPage';

function App() {
  return (
    <Routes>
      <Route path={routes.login} element={<LoginPage />} />
      <Route path={routes.registration} element={<RegistrationPage />} />

      <Route
        path="*"
        element={
          <AppLayout>
            <Routes>
              <Route index element={<SmartRedirect />} />
              <Route
                path={routes.garage}
                element={
                  <ProtectedRoute>
                    <GaragePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.userprofile}
                element={
                  <ProtectedRoute>
                    <UserProfile />
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.settings}
                element={
                  <ProtectedRoute>
                    <SettingsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.addVehicle}
                element={
                  <ProtectedRoute>
                    <AddVehiclePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.about}
                element={
                  <ProtectedRoute>
                    <AboutPage />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </AppLayout>
        }
      />
    </Routes>
  );
}

export default App;
