import {
  Button,
  Container,
  Group,
  Title,
  ActionIcon,
  Indicator,
  Tooltip,
} from '@mantine/core';
import { Link, useNavigate } from 'react-router-dom';
import { useMantineColorScheme } from '@mantine/core';
import { routes } from '../../utils/routes';
import classes from '../../styles/pages/Header.module.css';
import { useSelector, useDispatch } from 'react-redux';
import { type RootState } from '../../store/store';
import { logout as logoutAction } from '../../store/authSlice';
import { useLogoutMutation } from '../../api/authApi';

const links = [
  { link: '/forum', label: 'Форум' },
  { link: '/pricing', label: 'Pricing??' },
  { link: '/learn', label: 'Learn??' },
  { link: '/community', label: 'Community??' },
];

const Header = () => {
  const { toggleColorScheme, colorScheme } = useMantineColorScheme();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated,
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

  const items = links.map((link) => (
    <a key={link.label} href={link.link} className={classes.link}>
      {link.label}
    </a>
  ));

  return (
    <header className={classes.header}>
      <Container size="md" className={classes.inner}>
        <Link to={routes.home} style={{ textDecoration: 'none' }}>
          <Title order={4}>Vroomly</Title>
        </Link>
        <Group gap={5} visibleFrom="xs">
          {items}
          <Button variant="subtle" onClick={toggleColorScheme}>
            {colorScheme === 'dark' ? 'Light mode' : 'Dark mode'}
          </Button>

          {isAuthenticated ? (
            <>
              <Tooltip label="Сообщения">
                <Indicator color="red" size={8} offset={4} processing>
                  <ActionIcon variant="subtle" size="lg" aria-label="Сообщения">
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
                  </ActionIcon>
                </Indicator>
              </Tooltip>

              <Tooltip label="Уведомления">
                <Indicator color="red" size={8} offset={4} processing>
                  <ActionIcon
                    variant="subtle"
                    size="lg"
                    aria-label="Уведомления"
                  >
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
                  </ActionIcon>
                </Indicator>
              </Tooltip>

              <Tooltip label="Настройки">
                <ActionIcon
                  component={Link}
                  to={routes.settings}
                  variant="subtle"
                  size="lg"
                  aria-label="Настройки"
                >
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
                </ActionIcon>
              </Tooltip>

              <Button variant="subtle" onClick={handleLogout}>
                Выйти
              </Button>
            </>
          ) : (
            <>
              <Button component={Link} to={routes.login} variant="subtle">
                Войти
              </Button>
              <Button component={Link} to={routes.registration}>
                Регистрация
              </Button>
            </>
          )}
        </Group>
      </Container>
    </header>
  );
};

export default Header;
