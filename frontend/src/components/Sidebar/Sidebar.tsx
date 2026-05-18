import { useSelector } from 'react-redux';
import { NavLink, Stack, Box } from '@mantine/core';
import { Link, useLocation } from 'react-router-dom';
import { routes } from '../../utils/routes';
import { type RootState } from '../../store/store';
import classes from '../../styles/pages/Sidebar.module.css';

const navItems = [
  { label: 'Мой гараж', path: routes.garage, icon: CarIcon },
  { label: 'Записи на сервис', path: '/service', icon: WrenchIcon },
  { label: 'Заправки', path: '/refuels', icon: FuelIcon },
  { label: 'Расходы', path: '/expenses', icon: WalletIcon },
];

const Sidebar = () => {
  const location = useLocation();
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated,
  );

  if (!isAuthenticated) {
    return null;
  }

  return (
    <Box className={classes.sidebar}>
      <Stack gap={4} p="md">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            component={Link}
            to={item.path}
            label={item.label}
            leftSection={<item.icon />}
            className={classes.navLink}
            activeClassName={classes.navLinkActive}
            data-active={location.pathname === item.path || undefined}
          />
        ))}
      </Stack>
    </Box>
  );
};

function CarIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1-.8-1.8-.8H5c-.6 0-1 .4-1 1v4c0 .6.4 1 1 1h2" />
      <circle cx="7" cy="17" r="2" />
      <circle cx="17" cy="17" r="2" />
    </svg>
  );
}

function WrenchIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
    </svg>
  );
}

function FuelIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 22h12" />
      <path d="M6 18v-6a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v6" />
      <path d="M6 9h4v9H6z" />
      <path d="M18 6h2v4h-2z" />
    </svg>
  );
}

function WalletIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
      <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
      <circle cx="18" cy="12" r="2" />
    </svg>
  );
}

export default Sidebar;
