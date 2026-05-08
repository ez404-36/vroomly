import { Box, Container, Title } from '@mantine/core';
import Sidebar from '../Sidebar/Sidebar';
import MainContent from '../MainContent/MainContent';

const Home = () => {

  return (
    <>
      <Title order={1} ta="center">
        VR-90: Верстка страницы «Мой Гараж»
      </Title>

      <Container fluid my="md" px={0}>
        <Box
          style={{
            width: '100%',
            paddingInline: '2.604%',
            boxSizing: 'border-box',
          }}
        >
          <Box
            style={{
              display: 'grid',
              gridTemplateColumns: '21.978% 78.022%',
              width: '100%',
            }}
          >
            <Sidebar />
            <MainContent />
          </Box>
        </Box>
      </Container>
    </>
  );
};

export default Home;
