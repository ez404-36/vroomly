import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import AppRoutes from '../AppRoutes/AppRoutes';
import Header from './Header/Header';
import { setAuthenticated } from '../store/authSlice';
import { useGetCurrentUserQuery } from '../api/authApi';

function App() {
  const dispatch = useDispatch();
  useGetCurrentUserQuery();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      dispatch(setAuthenticated(true));
    }
  }, [dispatch]);

  return (
    <>
      <Header />
      <AppRoutes />
    </>
  );
}

export default App;
