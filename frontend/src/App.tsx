import React from 'react';
import { AppRouter } from './core/router';
import { NotificationContainer } from './shared/components/NotificationContainer';
import './styles/globals.css';

function App() {
  return (
    <>
      <AppRouter />
      <NotificationContainer />
    </>
  );
}

export default App;