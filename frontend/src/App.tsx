import { useEffect } from 'react';
import './App.css';

declare global {
  interface Window {
    Telegram?: {
      WebApp?: TelegramWebApp;
    };
  }
}

interface TelegramWebApp {
  backgroundColor: string;
  textColor: string;
  buttonColor: string;
  buttonTextColor: string;
  ready: () => void;
  expand: () => void;
  onEvent: (event: string, callback: () => void) => void;
  offEvent: (event: string, callback: () => void) => void;
  showAlert: (message: string) => void;
  sendData: (data: string) => void;
}

function App() {
  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;

    const updateTheme = () => {
      document.documentElement.style.setProperty('--tg-theme-bg-color', tg.backgroundColor);
    };

    tg.ready();
    tg.expand();
    updateTheme();

    tg.onEvent('themeChanged', updateTheme);
    return () => tg.offEvent('themeChanged', updateTheme);
  }, []);

  const showNotification = () => {
    const tg = window.Telegram?.WebApp;
    if (tg?.showAlert) {
      tg.showAlert('Соси');
      tg.sendData(JSON.stringify({ action: 'button_clicked' }))
    } else {
      alert('соснул');
    }
  };

  return (
    <div className="app">
      <h1>Моё приложение</h1>
      <button className="tg-button" onClick={showNotification}>
        Нажми меня
      </button>
    </div>
  );
}

export default App;