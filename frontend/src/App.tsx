import { useEffect, useState } from 'react';
import './App.css';
import { FiCalendar, FiFilter, FiPlusCircle, FiGrid, FiList } from 'react-icons/fi';
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
  showPopup?: (params: any) => void;
  showAlert: (message: string) => void;
  sendData: (data: string) => void;
}

type ViewMode = 'grid' | 'list';

// Списки для фильтров
const metroStations = [
  'Автово', 'Адмиралтейская', 'Академическая', 'Балтийская', 'Василеостровская',
  'Владимирская', 'Выборгская', 'Гостиный двор', 'Достоевская', 'Звенигородская'
];
const topics = ['Концерт', 'Спорт', 'Выставка', 'Кино', 'Лекция'];

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [peopleCount, setPeopleCount] = useState<number>(1);
  const [date, setDate] = useState<string>('');
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [metroStation, setMetroStation] = useState<string>(metroStations[0]);

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

  useEffect(() => {
  if (showFilters) {
    document.body.classList.add('body-filters-open');
  } else {
    document.body.classList.remove('body-filters-open');
  }
  }, [showFilters]);

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

  const toggleViewMode = () => {
    setViewMode(prev => prev === 'grid' ? 'list' : 'grid');
  };

  const handleSearch = () => {
    const tg = window.Telegram?.WebApp;
    const filterInfo = `
      Фильтры:
      • Людей: ${peopleCount}
      • Дата: ${date || 'не выбрана'}
      • Тематика: ${selectedTopics.length ? selectedTopics.join(', ') : 'все'}
      • Метро: ${metroStation}
    `;
    if (tg?.showPopup) {
      tg.showPopup({
        title: 'Выбранные фильтры',
        message: filterInfo,
        buttons: [{ type: 'ok' }]
      });
    } else if (tg?.showAlert) {
      tg.showAlert(filterInfo);
    } else {
      alert(filterInfo);
    }
    setShowFilters(false);
  };

  const items = [1, 2, 3, 4, 5, 6, 7, 8];

  return (
    <div className="app">
      <header className="top-panel">
        <div className="top-row">
          <div className="logo-area">
            <img src={PolyLogo} alt="logo" width={35} height={35} />
            <span className="app-title">PolyGang</span>
          </div>
          <button className="events-top-button" onClick={handleEvents}>
            <FiCalendar size={24} />
          </button>
        </div>
        <div className="search-row">
          <input type="text" placeholder="Поиск..." className="search-input" />
          <button
            className={`filter-button ${showFilters ? 'active' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            <FiFilter /> Фильтры
          </button>
        </div>
      <div className={`filters-panel ${showFilters ? 'open' : ''}`}>
        <div className="filter-group">
          <label>Количество людей:</label>
          <input
            type="number"
            min="1"
            value={peopleCount}
            onChange={(e) => setPeopleCount(parseInt(e.target.value) || 1)}
          />
        </div>
        <div className="filter-group">
          <label>Дата:</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
        <div className="filter-group">
          <label>Тематика:</label>
          <div className="topics-list">
            {topics.map(topic => (
              <label key={topic} className="topic-checkbox">
                <input
                  type="radio"
                  name="topic"
                  checked={selectedTopics.includes(topic)}
                  onChange={() => setSelectedTopics([topic])}
                />
                {topic}
              </label>
            ))}
          </div>
        </div>
        <div className="filter-group">
          <label>Станция метро:</label>
          <div className="metro-select">
            {metroStations.map(station => (
              <div
                key={station}
                className={`metro-option ${metroStation === station ? 'selected' : ''}`}
                onClick={() => setMetroStation(station)}
              >
                {station}
              </div>
            ))}
          </div>
        </div>
        <button className="search-button" onClick={handleSearch}>Поиск</button>
      </div>
      </header>

      <main className={`content ${showFilters ? 'no-scroll' : ''}`}>
        <div className="view-mode-toggle">
          <button className="mode-toggle-btn" onClick={toggleViewMode}>
            {viewMode === 'grid' ? <FiList size={24} /> : <FiGrid size={24} />}
          </button>
        </div>

        {viewMode === 'grid' && (
          <div className="grid-container">
            {items.map(item => (
              <div key={item} className="grid-item"></div>
            ))}
          </div>
        )}

        {viewMode === 'list' && (
          <div className="list-container">
            {items.map(item => (
              <div key={item} className="list-item"></div>
            ))}
          </div>
        )}
      </main>

      <footer className="bottom-panel">
        <button className="create-button" onClick={handleCreate}>
          <FiPlusCircle /> Создать
        </button>
      </footer>
    </div>
  );
}

export default App;