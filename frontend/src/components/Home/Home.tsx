import { Title, Container } from '../../ui';
import Sidebar from '../Sidebar/Sidebar';
import MainContent from '../MainContent/MainContent';

const Home = () => {
  return (
    <>
      <Title order={1} ta="center">
        VR-90: Верстка страницы «Мой Гараж»
      </Title>

      <Container fluid style={{ marginTop: '16px', marginBottom: '16px', paddingInline: 0 }}>
        <div
          style={{
            width: '100%',
            paddingInline: '2.604%',
            boxSizing: 'border-box',
          }}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '21.978% 78.022%',
              width: '100%',
            }}
          >
            <Sidebar />
            <MainContent />
          </div>
        </div>
      </Container>
    </>
  );
};

export default Home;
