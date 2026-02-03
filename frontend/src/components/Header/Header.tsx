import { Button, Center, Flex, useMantineColorScheme } from '@mantine/core';

const Header = () => {
  const { toggleColorScheme, colorScheme } = useMantineColorScheme();

  return (
    <>
      <Flex direction="column">
        <Center>Header</Center>

        <Center>
          <Button onClick={toggleColorScheme}>
            {colorScheme === 'dark' ? 'Light mode' : 'Dark mode'}
          </Button>
        </Center>
      </Flex>
    </>
  );
};

export default Header;
