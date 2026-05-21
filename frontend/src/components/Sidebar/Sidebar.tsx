import { useSelector } from 'react-redux';
import { Link, useLocation } from 'react-router-dom';
import { routes } from '../../utils/routes';
import { type RootState } from '../../store/store';
import { useGetCurrentUserQuery } from '../../api/authApi';
import { Tooltip } from '../../ui';
import {
  CarIcon,
  WrenchIcon,
  FuelIcon,
  WalletIcon,
  SupportIcon,
  ContactsIcon,
  InfoIcon,
} from '../../svg';
import classes from '../../styles/pages/Sidebar.module.css';
import { clsx } from 'clsx';

interface SidebarProps {
  isCollapsed?: boolean;
}

const navItems = [
  { label: 'Мой гараж', path: routes.garage, icon: CarIcon },
  { label: 'Записи на сервис', path: '/service', icon: WrenchIcon },
  { label: 'Заправки', path: '/refuels', icon: FuelIcon },
  { label: 'Расходы', path: '/expenses', icon: WalletIcon },
];

const footerLinks = [
  { label: 'Техническая поддержка', path: routes.home, icon: SupportIcon },
  { label: 'Контакты', path: routes.home, icon: ContactsIcon },
  { label: 'О сервисе', path: routes.about, icon: InfoIcon },
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

const Sidebar = ({ isCollapsed = false }: SidebarProps) => {
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
        <div className={clsx(classes.profile, isCollapsed && classes.profileCollapsed)}>
          {isCollapsed ? (
            <Tooltip label={user.login}>
              <div className={clsx(classes.avatar, isCollapsed && classes.avatarCollapsed)}>
                {initials}
              </div>
            </Tooltip>
          ) : (
            <div className={clsx(classes.avatar, isCollapsed && classes.avatarCollapsed)}>
              {initials}
            </div>
          )}
          <span className={clsx(classes.login, isCollapsed && classes.loginHidden)}>
            {user.login}
          </span>
        </div>
      )}

      <nav className={clsx(classes.nav, isCollapsed && classes.navCollapsed)}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const linkContent = (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                classes.navLink,
                isCollapsed && classes.navLinkCollapsed,
                isActive && classes.navLinkActive,
              )}
            >
              <span className={classes.navIcon}>
                <item.icon />
              </span>
              <span className={clsx(classes.navLabel, isCollapsed && classes.navLabelHidden)}>
                {item.label}
              </span>
            </Link>
          );
          return isCollapsed ? (
            <Tooltip key={item.path} label={item.label}>
              {linkContent}
            </Tooltip>
          ) : (
            linkContent
          );
        })}
      </nav>

      <div className={clsx(classes.footer, isCollapsed && classes.footerCollapsed)}>
        {footerLinks.map((item) => {
          const linkContent = (
            <Link
              key={item.label}
              to={item.path}
              className={clsx(classes.footerLink, isCollapsed && classes.footerLinkCollapsed)}
            >
              <span className={classes.footerIcon}>
                <item.icon />
              </span>
              <span className={clsx(classes.footerLabel, isCollapsed && classes.footerLabelHidden)}>
                {item.label}
              </span>
            </Link>
          );
          return isCollapsed ? (
            <Tooltip key={item.label} label={item.label}>
              {linkContent}
            </Tooltip>
          ) : (
            linkContent
          );
        })}
      </div>
    </div>
  );
};

export default Sidebar;
