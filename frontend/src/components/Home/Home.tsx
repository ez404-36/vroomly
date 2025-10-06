import { Link } from 'react-router-dom';
import { routes } from '../../utils/routes';

const Home = () => {
  return (
    <>
      <h1>VR-24: Страница регистрации и авторизации</h1>
      <Link to={routes.profile}>
        <button>К странице регистрации</button>
      </Link>
    </>
  );
};

export default Home;
