import { useEffect } from 'react';
import './App.css';
import { FaUserCircle } from 'react-icons/fa';
import { FiCalendar, FiFilter, FiPlusCircle } from 'react-icons/fi';
import PolyLogo from '../assets/images/logo.png';

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

  const handleCreate = () => {
    const tg = window.Telegram?.WebApp;
    if (tg?.showAlert) {
      tg.showAlert('Создаём новое событие');
      tg.sendData(JSON.stringify({ action: 'create' }));
    } else {
      alert('Создаём новое событие (резервный режим)');
    }
  };

    const handleEvents = () => {
    const tg = window.Telegram?.WebApp;
    if (tg?.showAlert) {
      tg.showAlert('Переход к моим событиям');
      tg.sendData(JSON.stringify({ action: 'my_events' }));
    } else {
      alert('Мои события (резервный режим)');
    }
  };

  return (
    <div className="app">
      <header className="top-panel">
        <div className="top-row">
          <img src={PolyLogo} alt="calendar" width={35} height={35}/>
          <span className="app-title">PolyGang</span>
          <button className="profile-button">
            <FaUserCircle size={24} />
          </button>
        </div>
        <div className="search-row">
          <input type="text" placeholder="Поиск..." className="search-input" />
          <button className="filter-button">
            <FiFilter /> Фильтры
          </button>
        </div>
      </header>

      <main className="content">
        <div className="grid-container">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((item) => (
            <div key={item} className="grid-item"></div>
          ))}
        </div>
      </main>

      <footer className="bottom-panel">
        <button className="create-button" onClick={handleCreate}>
          <FiPlusCircle /> Создать
        </button>
        <button className="events-button" onClick={handleEvents}>
          <FiCalendar /> Мои события
        </button>
      </footer>
    </div>
  );
}

export default App;