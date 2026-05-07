import {
  Button,
  Center,
  Flex,
  useMantineColorScheme,
  Burger,
  Container,
  Group,
  Title,
} from '@mantine/core';
import { useState } from 'react';
import { useDisclosure } from '@mantine/hooks';
import classes from '../../styles/pages/header.module.css';

const links = [
  { link: '/forum', label: 'Форум' },
  { link: '/pricing', label: 'Pricing??' },
  { link: '/learn', label: 'Learn??' },
  { link: '/community', label: 'Community??' },
];

const Header = () => {
  const { toggleColorScheme, colorScheme } = useMantineColorScheme();

  const [opened, { toggle }] = useDisclosure(false);
  const [active, setActive] = useState(links[0].link);

  const items = links.map((link) => (
    <a
      key={link.label}
      href={link.link}
      className={classes.link}
      data-active={active === link.link || undefined}
      onClick={(event) => {
        event.preventDefault();
        setActive(link.link);
      }}
    >
      {link.label}
    </a>
  ));

  return (
    <>
      <Flex direction="column">
        <Center>
          <Button variant="subtle"></Button>
        </Center>
      </Flex>

      <header className={classes.header}>
        <Container size="md" className={classes.inner}>
          <Title order={4}>Vroomly</Title>
          <Group gap={5} visibleFrom="xs">
            {items}
            <Button onClick={toggleColorScheme}>
              {colorScheme === 'dark' ? 'Light mode' : 'Dark mode'}
            </Button>
          </Group>

          <Burger
            opened={opened}
            onClick={toggle}
            hiddenFrom="xs"
            size="sm"
            aria-label="Toggle navigation"
          />
        </Container>
      </header>
    </>
  );
};

export default Header;
