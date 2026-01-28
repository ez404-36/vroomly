import { Link } from 'react-router-dom';
import { routes } from '../../utils/routes';
import { Button, Center, Title } from '@mantine/core';

const Home = () => {
  return (
    <>
      <Title order={1} ta="center">
        VR-90: Верстка страницы "Мой Гараж"
      </Title>
      <Center mt="xl">
        <Link to={routes.userprofile}>
          <Button>К странице регистрации (VR-24)</Button>
        </Link>
      </Center>
    </>
  );
};

export default Home;
