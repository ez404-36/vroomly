import { useSelector } from 'react-redux';
import { Link, useLocation } from 'react-router-dom';
import { routes } from '../../utils/routes';
import { type RootState } from '../../store/store';
import { useGetCurrentUserQuery } from '../../api/authApi';
import classes from '../../styles/pages/Sidebar.module.css';
import { clsx } from 'clsx';

const navItems = [
  { label: 'Мой гараж', path: routes.garage, icon: CarIcon },
  { label: 'Записи на сервис', path: '/service', icon: WrenchIcon },
  { label: 'Заправки', path: '/refuels', icon: FuelIcon },
  { label: 'Расходы', path: '/expenses', icon: WalletIcon },
];

const footerLinks = [
  { label: 'Техническая поддержка', path: routes.home, icon: SupportIcon },
  { label: 'Контакты', path: routes.home, icon: ContactsIcon },
  { label: 'О сервисе', path: routes.home, icon: InfoIcon },
];

function getInitials(
  login: string,
  name: string | null | undefined,
  surname: string | null | undefined,
): string {
  if (name && surname) {
    return (name[0] + surname[0]).toUpperCase();
  }
  if (name) {
    return name.slice(0, 2).toUpperCase();
  }
  if (surname) {
    return surname.slice(0, 2).toUpperCase();
  }
  const letters = login.replace(/[^a-zA-Zа-яА-ЯёЁ0-9]/g, '');
  return (letters.slice(0, 2) || login.slice(0, 2)).toUpperCase();
}

const Sidebar = () => {
  const location = useLocation();
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated,
  );
  const { data: user } = useGetCurrentUserQuery(undefined, {
    skip: !isAuthenticated,
  });

  if (!isAuthenticated) {
    return null;
  }

  const initials = user ? getInitials(user.login, user.name, user.surname) : '';

  return (
    <div className={classes.container}>
      {user && (
        <div className={classes.profile}>
          <div className={classes.avatar}>{initials}</div>
          <span className={classes.login}>{user.login}</span>
        </div>
      )}

      <nav className={classes.nav}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                classes.navLink,
                isActive && classes.navLinkActive,
              )}
            >
              <item.icon />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className={classes.footer}>
        {footerLinks.map((item) => (
          <Link key={item.label} to={item.path} className={classes.footerLink}>
            <item.icon />
            {item.label}
          </Link>
        ))}
      </div>
    </div>
  );
};

/* ── Nav icons ─────────────────────────────────────────────────── */

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

/* ── Footer icons ──────────────────────────────────────────────── */

function SupportIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
      <path d="M12 17h.01" />
    </svg>
  );
}

function ContactsIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M12 16v-4" />
      <path d="M12 8h.01" />
    </svg>
  );
}

export default Sidebar;
