import { useLocation } from 'react-router-dom';
import GaragePage from '../../pages/GaragePage';
import classes from '../../styles/pages/MainContent.module.css';

const MainContent = () => {
  const location = useLocation();

  if (location.pathname === '/garage') {
    return (
      <div className={classes.mainContent}>
        <GaragePage />
      </div>
    );
  }

  return (
    <div className={classes.mainContent}>
      <div>MainContent</div>
    </div>
  );
};

export default MainContent;
