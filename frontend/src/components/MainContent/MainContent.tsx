import React from 'react';
import { Box } from '@mantine/core';
import { useLocation } from 'react-router-dom';
import GaragePage from '../../pages/GaragePage';
import classes from '../../styles/pages/MainContent.module.css';

const MainContent = () => {
  const location = useLocation();

  if (location.pathname === '/garage') {
    return <GaragePage />;
  }

  return (
    <Box className={classes.mainContent}>
      <div>MainContent</div>
    </Box>
  );
};

export default MainContent;