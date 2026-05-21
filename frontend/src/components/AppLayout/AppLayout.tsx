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
import {
  ChevronLeftIcon,
  SidebarIcon,
  SidebarRightIcon,
  SunIcon,
  MoonIcon,
  ChatIcon,
  BellIcon,
  GearIcon,
} from '../../svg';
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
              <Sidebar isCollapsed={!leftOpen} />
            </div>
          </aside>
          <Tooltip label={leftOpen ? 'Свернуть' : 'Развернуть'}>
            <button
              className={clsx(
                classes.leftEdgeToggle,
                !leftOpen && classes.leftEdgeToggleCollapsed,
              )}
              onClick={() => dispatch(toggleLeftSidebar())}
              aria-label={
                leftOpen ? 'Свернуть боковую панель' : 'Развернуть боковую панель'
              }
            >
              <ChevronLeftIcon flipped={!leftOpen} />
            </button>
          </Tooltip>
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
                    leftOpen
                      ? 'Скрыть боковую панель'
                      : 'Показать боковую панель'
                  }
                >
                  <span className={classes.headerIcon}>
                    <SidebarIcon />
                  </span>
                </button>
              )}
              <Title
                order={4}
                style={{
                  color: 'var(--color-primary-fg)',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
                onClick={() => navigate(isAuthenticated ? routes.garage : routes.about)}
              >
                Vroomly
              </Title>
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
                  <span className={classes.headerIcon}>
                    {colorScheme === 'dark' ? <SunIcon /> : <MoonIcon />}
                  </span>
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
                        <span className={classes.headerIcon}>
                          <ChatIcon />
                        </span>
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
                        <span className={classes.headerIcon}>
                          <BellIcon />
                        </span>
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
                        <span className={classes.headerIcon}>
                          <GearIcon />
                        </span>
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
                <span className={classes.headerIcon}>
                  <SidebarRightIcon />
                </span>
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

export default AppLayout;
