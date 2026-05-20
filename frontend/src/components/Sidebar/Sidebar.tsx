import { Avatar, Box, Button, Group, Stack, Text } from '@mantine/core';
import { Link } from 'react-router-dom';
import { routes } from '../../utils/routes';

const Sidebar = ({ name }: { name: string }) => {
  return (
    <>
      <Box>
        <Stack gap="lg">
          <Group align="center" wrap="nowrap">
            <Avatar src="/avatar.png" size={64} radius="xl" />
            <Box>
              <Text fw={700}>{name}</Text>
              <Text c="dimmed" size="sm">
                Пользователь
              </Text>
            </Box>
          </Group>
          <Stack gap="sm">
            <Button fw={700} fz="32px" lts="-0.02em" variant="light" fullWidth>
              Добавить ТС
            </Button>
            <Button fw={700} fz="32px" lts="-0.02em" variant="light" fullWidth>
              Мои заказы
            </Button>
            <Button fw={700} fz="32px" lts="-0.02em" variant="light" fullWidth>
              Мои настройки
            </Button>
            <Button fw={700} fz="32px" lts="-0.02em" variant="light" fullWidth>
              Мои профиль
            </Button>
          </Stack>
          <Stack gap="sm" mt={'xl'}>
            <Text
              component={Link}
              to={routes.support}
              c="dimmed"
              fw={300}
              fz="32px"
              lts="-0.02em"
              td="none"
            >
              Техническая поддержка
            </Text>
            <Text
              component={Link}
              to={routes.support}
              c="dimmed"
              fw={300}
              fz="32px"
              lts="-0.02em"
              td="none"
            >
              Контакты
            </Text>
            <Text
              component={Link}
              to={routes.support}
              c="dimmed"
              fw={300}
              fz="32px"
              lts="-0.02em"
              td="none"
            >
              О сервисе
            </Text>
          </Stack>
        </Stack>
      </Box>
    </>
  );
};

export default Sidebar;
