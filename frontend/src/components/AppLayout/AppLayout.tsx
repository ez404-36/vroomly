import type { ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { clsx } from 'clsx';
import { Button, Flex, Title, ActionIcon, Indicator, Tooltip } from '../../ui';
import { useColorScheme } from '../../hooks/useColorScheme';
import { routes } from '../../utils/routes';
import { type RootState } from '../../store/store';
import { logout as logoutAction } from '../../store/authSlice';
import {
  toggleLeftSidebar,
  toggleRightSidebar,
  setLeftSidebar,
} from '../../store/layoutSlice';
import { useLogoutMutation } from '../../api/authApi';
import Sidebar from '../Sidebar/Sidebar';
import classes from '../../styles/pages/AppLayout.module.css';

const headerLinks = [
  { link: '/forum', label: 'Форум' },
  { link: '/pricing', label: 'Pricing??' },
  { link: '/learn', label: 'Learn??' },
  { link: '/community', label: 'Community??' },
];

interface AppLayoutProps {
  children: ReactNode;
  rightSidebar?: ReactNode;
}

const AppLayout = ({ children, rightSidebar }: AppLayoutProps) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { toggleColorScheme, colorScheme } = useColorScheme();

  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated,
  );
  const leftOpen = useSelector(
    (state: RootState) => state.layout.leftSidebarOpen,
  );
  const rightOpen = useSelector(
    (state: RootState) => state.layout.rightSidebarOpen,
  );

  const [logoutApi] = useLogoutMutation();

  const handleLogout = async () => {
    try {
      await logoutApi().unwrap();
    } finally {
      dispatch(logoutAction());
      navigate(routes.home);
    }
  };

  const isMobile = typeof window !== 'undefined' && window.innerWidth <= 768;

  return (
    <div className={classes.layout}>
      {/* Left Sidebar */}
      {isAuthenticated && (
        <div className={classes.leftSidebarWrapper}>
          <aside
            className={clsx(
              classes.leftSidebar,
              !leftOpen && classes.leftSidebarCollapsed,
            )}
          >
            <div className={classes.leftSidebarInner}>
              <Sidebar />
            </div>
          </aside>
          <button
            className={clsx(
              classes.leftEdgeToggle,
              !leftOpen && classes.leftEdgeToggleCollapsed,
            )}
            onClick={() => dispatch(toggleLeftSidebar())}
            aria-label={
              leftOpen ? 'Скрыть боковую панель' : 'Показать боковую панель'
            }
          >
            <ChevronLeftIcon flipped={!leftOpen} />
          </button>
        </div>
      )}

      {/* Mobile overlay */}
      {isAuthenticated && isMobile && leftOpen && (
        <div
          className={classes.overlay}
          onClick={() => dispatch(setLeftSidebar(false))}
          role="presentation"
        />
      )}

      {/* Right column: header + content area */}
      <div className={classes.rightColumn}>
        {/* Header */}
        <header className={classes.header}>
          <div className={classes.headerInner}>
            <Flex gap="sm" align="center">
              {isAuthenticated && (
                <button
                  className={classes.sidebarToggle}
                  onClick={() => dispatch(toggleLeftSidebar())}
                  aria-label={
                    leftOpen ? 'Скрыть боковую панель' : 'Показать боковую панель'
                  }
                >
                  <SidebarIcon />
                </button>
              )}
              <Link to={routes.home} style={{ textDecoration: 'none' }}>
                <Title order={4} style={{ color: 'var(--color-primary-fg)' }}>
                  Vroomly
                </Title>
              </Link>
            </Flex>

            <Flex gap="xs" align="center">
              {headerLinks.map((link) => (
                <a
                  key={link.label}
                  href={link.link}
                  className={classes.headerLink}
                >
                  {link.label}
                </a>
              ))}

              <Tooltip
                label={colorScheme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}
              >
                <ActionIcon
                  variant="subtleInverse"
                  size="lg"
                  onClick={toggleColorScheme}
                  aria-label="Сменить тему"
                >
                  {colorScheme === 'dark' ? <SunIcon /> : <MoonIcon />}
                </ActionIcon>
              </Tooltip>

              {isAuthenticated ? (
                <>
                  <Tooltip label="Сообщения">
                    <Indicator color="red" size={8} offset={4} processing>
                      <ActionIcon
                        variant="subtleInverse"
                        size="lg"
                        aria-label="Сообщения"
                      >
                        <ChatIcon />
                      </ActionIcon>
                    </Indicator>
                  </Tooltip>

                  <Tooltip label="Уведомления">
                    <Indicator color="red" size={8} offset={4} processing>
                      <ActionIcon
                        variant="subtleInverse"
                        size="lg"
                        aria-label="Уведомления"
                      >
                        <BellIcon />
                      </ActionIcon>
                    </Indicator>
                  </Tooltip>

                  <Tooltip label="Настройки">
                    <Link
                      to={routes.settings}
                      style={{ textDecoration: 'none' }}
                    >
                      <ActionIcon
                        variant="subtleInverse"
                        size="lg"
                        aria-label="Настройки"
                      >
                        <GearIcon />
                      </ActionIcon>
                    </Link>
                  </Tooltip>

                  <Button variant="subtleInverse" onClick={handleLogout}>
                    Выйти
                  </Button>
                </>
              ) : (
                <>
                  <Link to={routes.login} style={{ textDecoration: 'none' }}>
                    <Button variant="subtleInverse">Войти</Button>
                  </Link>
                  <Link
                    to={routes.registration}
                    style={{ textDecoration: 'none' }}
                  >
                    <Button variant="filled">Регистрация</Button>
                  </Link>
                </>
              )}
            </Flex>
          </div>
        </header>

        {/* Content area: main + optional right sidebar */}
        <div className={classes.contentArea}>
          <main className={classes.main}>{children}</main>

          {isAuthenticated && rightSidebar !== undefined && (
            <>
              <button
                className={clsx(classes.sidebarToggle, classes.rightToggle)}
                onClick={() => dispatch(toggleRightSidebar())}
                aria-label={
                  rightOpen ? 'Скрыть правую панель' : 'Показать правую панель'
                }
                style={{ alignSelf: 'flex-start', margin: '8px 4px' }}
              >
                <SidebarRightIcon />
              </button>
              <aside
                className={clsx(
                  classes.rightSidebar,
                  !rightOpen && classes.rightSidebarCollapsed,
                )}
              >
                <div className={classes.rightSidebarInner}>{rightSidebar}</div>
              </aside>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

/* ── SVG icons ─────────────────────────────────────────────────── */

function ChevronLeftIcon({ flipped }: { flipped: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="currentColor"
      stroke="none"
      style={{
        transition: 'transform 0.25s ease',
        transform: flipped ? 'rotate(180deg)' : undefined,
      }}
    >
      <path d="M15 19l-7-7 7-7z" />
    </svg>
  );
}

function SidebarIcon() {
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
      <rect width="18" height="18" x="3" y="3" rx="2" />
      <path d="M9 3v18" />
    </svg>
  );
}

function SidebarRightIcon() {
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
      <rect width="18" height="18" x="3" y="3" rx="2" />
      <path d="M15 3v18" />
    </svg>
  );
}

function SunIcon() {
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
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
    </svg>
  );
}

function MoonIcon() {
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
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

function ChatIcon() {
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
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

function BellIcon() {
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
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}

function GearIcon() {
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
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

export default AppLayout;
