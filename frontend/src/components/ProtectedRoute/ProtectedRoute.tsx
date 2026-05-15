import { type ReactNode } from 'react';

import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';

import { type RootState } from '../../store/store';
import { routes } from '../../utils/routes';

interface ProtectedRouteProps {
	children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps): React.ReactElement => {
	const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

	if (!isAuthenticated) {
		return <Navigate to={routes.login} replace />;
	}

	return <>{children}</>;
};

export default ProtectedRoute;