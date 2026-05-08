import {
  Button,
  Container,
  Group,
  Title,
  ActionIcon,
  Indicator,
  Tooltip,
} from '@mantine/core';
import { Link } from 'react-router-dom';
import { useMantineColorScheme } from '@mantine/core';
import { routes } from '../../utils/routes';
import classes from '../../styles/pages/Header.module.css';
import { useSelector } from 'react-redux';
import { type RootState } from '../../store/store';

const links = [
  { link: '/forum', label: 'Форум' },
  { link: '/pricing', label: 'Pricing??' },
  { link: '/learn', label: 'Learn??' },
  { link: '/community', label: 'Community??' },
];

const Header = () => {
  const { toggleColorScheme, colorScheme } = useMantineColorScheme();
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated,
  );

  const items = links.map((link) => (
    <a
      key={link.label}
      href={link.link}
      className={classes.link}
    >
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
                  <ActionIcon
                    variant="subtle"
                    size="lg"
                    aria-label="Сообщения"
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
                    <circle cx="12" cy="12" r="3" />
                    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
                  </svg>
                </ActionIcon>
              </Tooltip>
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
