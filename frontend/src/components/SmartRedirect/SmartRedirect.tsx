import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { type RootState } from '../../store/store';
import { routes } from '../../utils/routes';

const SmartRedirect = () => {
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated,
  );

  return (
    <Navigate
      to={isAuthenticated ? routes.garage : routes.about}
      replace
    />
  );
};

export default SmartRedirect;