import { Link } from 'react-router-dom';
import { routes } from '../../utils/routes';
import { Box, Button, Center, Container, Title } from '@mantine/core';
import Sidebar from '../Sidebar/Sidebar';
import MainContent from '../MainContent/MainContent';
import classes from '../../styles/pages/Home.module.css';

const Home = () => {
  return (
    <>
      <Title order={1} ta="center">
        VR-90: Верстка страницы «Мой Гараж»
      </Title>
      <Center mt="xl">
        <Link to={routes.userprofile}>
          <Button>К странице регистрации (VR-24)</Button>
        </Link>
      </Center>

      <Container fluid my="md" px={0}>
        <Box
          style={{
            width: '100%',
            paddingInline: '2.604%',
            boxSizing: 'border-box',
          }}
        >
          <Box className={classes.homeLayout}>
            <Box className={classes.sidebarColumn}>
              <Sidebar />
            </Box>
            <MainContent />
          </Box>
        </Box>
      </Container>
    </>
  );
};

export default Home;
