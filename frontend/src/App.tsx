import { useEffect } from 'react';
import './App.css';

declare global {
  interface Window {
    Telegram?: {
      WebApp?: TelegramWebApp;
    };
  }
}

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
}

interface TelegramWebApp {
  backgroundColor: string;
  textColor: string;
  buttonColor: string;
  buttonTextColor: string;
  initDataUnsafe: { user?: TelegramUser };
  ready: () => void;
  expand: () => void;
  onEvent: (event: string, callback: () => void) => void;
  offEvent: (event: string, callback: () => void) => void;
  showAlert: (message: string) => void;
  sendData: (data: string) => void;
}

const BACKEND_URL = 'https://f408bea7e74bb7.lhr.life';

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

    // АВТОРЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ ПРИ ЗАПУСКЕ ПРИЛОЖЕНИЯ
    const user = tg.initDataUnsafe?.user;
    if (user) {
      fetch(`${BACKEND_URL}/api/v1/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tg_id: user.id,
          username: user.username ?? null,
          full_name: `${user.first_name} ${user.last_name ?? ''}`.trim(),
        }),
      });
    }

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