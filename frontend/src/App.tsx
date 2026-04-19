import { useEffect, useState, useCallback } from 'react';
import './App.css';
import {
  FiCalendar, FiFilter, FiPlusCircle, FiGrid, FiList,
  FiX, FiMapPin, FiUsers, FiClock, FiSearch, FiUser,
  FiTrash2, FiUserMinus, FiUserPlus, FiAlertTriangle
} from 'react-icons/fi';
import PolyLogo from '../assets/images/logo.png';

// ─── Конфигурация ─────────────────────────────────────────────────────────────
const BACKEND_URL = 'http://localhost:8000';
const API_BASE = `${BACKEND_URL}/api/v1`;

// ─── Типы ─────────────────────────────────────────────────────────────────────
declare global { interface Window { Telegram?: { WebApp?: TelegramWebApp }; } }
interface TelegramWebApp {
  backgroundColor: string; initData: string;
  ready: () => void; expand: () => void;
  onEvent: (e: string, cb: () => void) => void;
  offEvent: (e: string, cb: () => void) => void;
}
interface ThemeCreator { id: number; tg_id: number; username?: string; full_name?: string; }
interface Theme {
  id: number; title: string; description?: string;
  datetime: string; location: string; max_slots: number;
  creator: ThemeCreator; tags?: string[];
  slots_available?: number; requests_count?: number;
}
interface MyRequest { id: number; status: 'pending' | 'approved' | 'rejected'; theme: Theme; }
interface CreateFormData {
  title: string; description: string; datetime: string;
  location: string; max_slots: number; tags: string[];
}
type ViewMode = 'grid' | 'list';

// ─── Константы ────────────────────────────────────────────────────────────────
const METRO_STATIONS = [
  'Автово','Адмиралтейская','Академическая','Балтийская','Василеостровская',
  'Владимирская','Выборгская','Гостиный двор','Достоевская','Звенигородская',
  'Кировский завод','Купчино','Лесная','Московская','Нарвская',
  'Невский проспект','Парк Победы','Политехническая','Площадь Мужества',
  'Приморская','Пролетарская','Проспект Ветеранов','Садовая','Сенная площадь',
  'Спортивная','Удельная','Фрунзенская','Чёрная речка','Чкаловская'
];
const TOPICS = ['Концерт','Спорт','Выставка','Кино','Лекция','Игры','Прогулка','Другое'];

// ─── Mock данные ──────────────────────────────────────────────────────────────
const MOCK_ME: ThemeCreator = { id:1, tg_id:111, username:'ivan_poly', full_name:'Иван Петров' };

const MOCK_THEMES: Theme[] = [
  { id:1, title:'Лекция по нейросетям в Политехе',
    description:'ML-инженер Яндекса разбирает трансформеры с нуля. Подходит для всех уровней.',
    datetime:'2026-05-02T18:30:00', location:'ауд.305 СПбПУ, Политехническая',
    max_slots:8, slots_available:5, requests_count:3,
    creator:MOCK_ME, tags:['Лекция'] },
  { id:2, title:'Мини-футбол на Московской',
    description:'Ищем 4 человека для команды. Площадка забронирована.',
    datetime:'2026-04-27T16:00:00', location:'Стадион "Олимп", Московская',
    max_slots:4, slots_available:2, requests_count:2,
    creator:{id:2,tg_id:222,username:'kolya',full_name:'Николай Смирнов'}, tags:['Спорт'] },
  { id:3, title:'Выставка современного искусства',
    description:'Эрарта открыла новую экспозицию. Идём небольшой компанией, потом кофе.',
    datetime:'2026-05-10T14:00:00', location:'Музей Эрарта, Василеостровская',
    max_slots:6, slots_available:4, requests_count:2,
    creator:{id:3,tg_id:333,username:'masha',full_name:'Мария Козлова'}, tags:['Выставка'] },
  { id:4, title:'Настолки в антикафе',
    description:'Catan, D&D, Диксит — на выбор. Место оплачивает каждый сам.',
    datetime:'2026-04-30T19:00:00', location:'Антикафе "Время", Гостиный двор',
    max_slots:10, slots_available:7, requests_count:3,
    creator:{id:4,tg_id:444,username:'dima',full_name:'Дмитрий Орлов'}, tags:['Игры'] },
  { id:5, title:'Кино: Дюна 3 в IMAX',
    description:'Идём на премьеру. Билеты покупаем сами, но договорились о рядах рядом.',
    datetime:'2026-05-05T20:00:00', location:'КАРО 11 Октябрь, Невский проспект',
    max_slots:5, slots_available:3, requests_count:2,
    creator:{id:5,tg_id:555,username:'alena',full_name:'Алёна Новикова'}, tags:['Кино'] },
  { id:6, title:'Прогулка по Кронштадту',
    description:'Выбираемся на целый день — маяки, форты, морской собор.',
    datetime:'2026-05-09T10:00:00', location:'ст.м. Автово (отправление)',
    max_slots:12, slots_available:9, requests_count:3,
    creator:{id:6,tg_id:666,username:'petya',full_name:'Пётр Зайцев'}, tags:['Прогулка'] },
];

const MOCK_MY_REQUESTS: MyRequest[] = [
  { id:10, status:'approved', theme: MOCK_THEMES[1] },
  { id:11, status:'pending',  theme: MOCK_THEMES[4] },
];

// ─── Утилиты ──────────────────────────────────────────────────────────────────
function extractTags(d?: string): string[] {
  if (!d) return [];
  const m = d.match(/^(#\S+\s*)+/);
  return m ? m[0].trim().split(/\s+/).map(t=>t.replace('#','')) : [];
}
function fmtDate(s: string) {
  return new Date(s).toLocaleDateString('ru-RU',{day:'2-digit',month:'2-digit'});
}
function fmtTime(s: string) {
  return new Date(s).toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'});
}
function fmtDateFull(s: string) {
  return new Date(s).toLocaleDateString('ru-RU',{
    day:'2-digit', month:'long', year:'numeric', weekday:'long'
  });
}
// Сколько людей уже подалось
function requestsCount(t: Theme): number {
  return t.requests_count ?? (t.max_slots - (t.slots_available ?? t.max_slots));
}
function slotsAvail(t: Theme): number {
  if (t.slots_available !== undefined) return t.slots_available;
  return t.max_slots - (t.requests_count ?? 0);
}
function slotWord(n: number) {
  const m10=n%10, m100=n%100;
  if (m10===1&&m100!==11) return 'слот';
  if ([2,3,4].includes(m10)&&![12,13,14].includes(m100)) return 'слота';
  return 'слотов';
}
function initials(name?: string): string {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  return parts.length >= 2
    ? (parts[0][0]+parts[1][0]).toUpperCase()
    : name.slice(0,2).toUpperCase();
}
function authHeaders(): Record<string,string> {
  const h: Record<string,string> = { 'Content-Type':'application/json' };
  const tg = window.Telegram?.WebApp;
  if (tg?.initData) h['Authorization'] = `tma ${tg.initData}`;
  return h;
}

// ─── Confirm Dialog ───────────────────────────────────────────────────────────
interface ConfirmProps {
  title: string;
  text: string;
  okLabel: string;
  danger?: boolean;
  onOk: () => void;
  onCancel: () => void;
}
function ConfirmDialog({ title, text, okLabel, danger, onOk, onCancel }: ConfirmProps) {
  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-dialog" onClick={e=>e.stopPropagation()}>
        <p className="confirm-title">
          {danger && <FiAlertTriangle size={16} style={{marginRight:6,verticalAlign:'middle',color:'#ff453a'}}/>}
          {title}
        </p>
        <p className="confirm-text">{text}</p>
        <div className="confirm-actions">
          <button className="confirm-cancel" onClick={onCancel}>Отмена</button>
          <button className={`confirm-ok ${danger?'confirm-ok--danger':'confirm-ok--primary'}`} onClick={onOk}>
            {okLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── GridCard ─────────────────────────────────────────────────────────────────
function GridCard({ theme, onClick }: { theme: Theme; onClick: ()=>void }) {
  const tags = theme.tags ?? extractTags(theme.description);
  const count = requestsCount(theme);
  const full = slotsAvail(theme) <= 0;
  return (
    <div className={`grid-item${full?' grid-item--full':''}`} onClick={onClick}>
      <div className="card-tags">
        {tags.length>0 ? tags.map(t=><span key={t} className="tag">#{t}</span>)
          : <span className="tag tag--empty">#событие</span>}
      </div>
      <div className="card-title">{theme.title}</div>
      <div className="card-meta">
        <span className="card-meta-row">
          <FiClock size={10} style={{flexShrink:0}}/>
          <span className="card-meta-text">{fmtDate(theme.datetime)} · {fmtTime(theme.datetime)}</span>
        </span>
        <span className="card-meta-row">
          <FiMapPin size={10} style={{flexShrink:0}}/>
          <span className="card-meta-text">{theme.location}</span>
        </span>
      </div>
      <div className={`card-slots${full?' card-slots--full':''}`}>
        <FiUsers size={12}/> {count} / {theme.max_slots} участников
      </div>
    </div>
  );
}

// ─── ListCard ─────────────────────────────────────────────────────────────────
function ListCard({ theme, onClick }: { theme: Theme; onClick: ()=>void }) {
  const tags = theme.tags ?? extractTags(theme.description);
  const count = requestsCount(theme);
  const full = slotsAvail(theme) <= 0;
  return (
    <div className={`list-item${full?' list-item--full':''}`} onClick={onClick}>
      <div className="list-left">
        <div className="card-tags">
          {tags.length>0 ? tags.map(t=><span key={t} className="tag">#{t}</span>)
            : <span className="tag tag--empty">#событие</span>}
        </div>
        <div className="list-title">{theme.title}</div>
      </div>
      <div className="list-right">
        <span className="card-meta-row"><FiClock size={10}/> {fmtDate(theme.datetime)} · {fmtTime(theme.datetime)}</span>
        <span className="card-meta-row"><FiMapPin size={10}/> {theme.location}</span>
        <span className={`card-slots${full?' card-slots--full':''}`}>
          <FiUsers size={11}/> {count} / {theme.max_slots}
        </span>
      </div>
    </div>
  );
}

// ─── DetailModal ──────────────────────────────────────────────────────────────
type UserRole = 'owner' | 'member' | 'pending' | 'none';

interface DetailModalProps {
  theme: Theme;
  myRequests: MyRequest[];
  onClose: () => void;
  onThemeDeleted: (id: number) => void;
  onRequestChanged: (themeId: number, action: 'join'|'cancel') => void;
}

function DetailModal({ theme, myRequests, onClose, onThemeDeleted, onRequestChanged }: DetailModalProps) {
  const tags = theme.tags ?? extractTags(theme.description);
  const count = requestsCount(theme);
  const avail = slotsAvail(theme);
  const full = avail <= 0;
  const fillPct = Math.min(100, Math.round((count / theme.max_slots) * 100));

  // Очищаем описание от хэштегов в начале
  const cleanDesc = theme.description
    ? theme.description.replace(/^(#\S+\s*)+\n?/, '').trim()
    : '';

  // Определяем роль пользователя
  const isOwner = theme.creator.id === MOCK_ME.id;
  const myReq = myRequests.find(r => r.theme.id === theme.id);
  const role: UserRole = isOwner ? 'owner' : myReq ? (myReq.status === 'pending' ? 'pending' : 'member') : 'none';

  const [confirm, setConfirm] = useState<null|'join'|'cancel'|'delete'>(null);
  const [loading, setLoading] = useState(false);

  const doAction = async (action: 'join'|'cancel'|'delete') => {
    setConfirm(null);
    setLoading(true);
    try {
      if (action === 'join') {
        await fetch(`${API_BASE}/themes/${theme.id}/requests/`, {
          method:'POST', headers: authHeaders()
        });
        onRequestChanged(theme.id, 'join');
      } else if (action === 'cancel') {
        if (myReq) {
          await fetch(`${API_BASE}/themes/${theme.id}/requests/${myReq.id}`, {
            method:'DELETE', headers: authHeaders()
          });
        }
        onRequestChanged(theme.id, 'cancel');
      } else {
        await fetch(`${API_BASE}/themes/${theme.id}`, {
          method:'DELETE', headers: authHeaders()
        });
        onThemeDeleted(theme.id);
        onClose();
      }
    } catch {
      // API недоступен — применяем локально
      if (action === 'join') onRequestChanged(theme.id, 'join');
      else if (action === 'cancel') onRequestChanged(theme.id, 'cancel');
      else { onThemeDeleted(theme.id); onClose(); }
    } finally { setLoading(false); }
  };

  const confirmConfig = {
    join: {
      title: 'Подать заявку',
      text: `Вы хотите участвовать в «${theme.title}»? Организатор рассмотрит вашу заявку.`,
      okLabel: 'Подать заявку', danger: false,
    },
    cancel: {
      title: 'Отменить заявку',
      text: 'Вы уверены? Заявка будет отозвана, и место освободится для других.',
      okLabel: 'Отменить заявку', danger: true,
    },
    delete: {
      title: 'Удалить мероприятие',
      text: `Удалить «${theme.title}»? Все заявки будут отменены. Это действие нельзя отменить.`,
      okLabel: 'Удалить', danger: true,
    },
  };

  return (
    <>
      {confirm && (
        <ConfirmDialog
          {...confirmConfig[confirm]}
          onOk={() => doAction(confirm)}
          onCancel={() => setConfirm(null)}
        />
      )}
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal" onClick={e=>e.stopPropagation()}>
          <div className="modal-header">
            <h2 className="modal-title">Мероприятие</h2>
            <button className="modal-close" onClick={onClose}><FiX size={20}/></button>
          </div>

          <div className="modal-body">
            {/* Теги */}
            {tags.length > 0 && (
              <div className="detail-tags">
                {tags.map(t=><span key={t} className="detail-tag">#{t}</span>)}
              </div>
            )}

            {/* Заголовок */}
            <div className="detail-title">{theme.title}</div>

            {/* Прогресс-бар участников */}
            <div className="detail-slots-bar">
              <FiUsers size={14} style={{flexShrink:0, color:'var(--tg-theme-hint-color, #888)'}}/>
              <div className="slots-progress-wrap">
                <div
                  className={`slots-progress-fill${full?' slots-progress-fill--full':''}`}
                  style={{width:`${fillPct}%`}}
                />
              </div>
              <span className={`slots-progress-text${full?' slots-progress-text--full':''}`}>
                {count} / {theme.max_slots}
              </span>
            </div>

            {/* Информационный блок */}
            <div className="detail-info-block">
              <div className="detail-row">
                <FiClock size={16} className="detail-row-icon"/>
                <div>
                  <span className="detail-row-label">Дата и время</span>
                  <span className="detail-row-value">{fmtDateFull(theme.datetime)}, {fmtTime(theme.datetime)}</span>
                </div>
              </div>
              <div className="detail-row">
                <FiMapPin size={16} className="detail-row-icon"/>
                <div>
                  <span className="detail-row-label">Место</span>
                  <span className="detail-row-value">{theme.location}</span>
                </div>
              </div>
              <div className="detail-row">
                <FiUsers size={16} className="detail-row-icon"/>
                <div>
                  <span className="detail-row-label">Участники</span>
                  <span className="detail-row-value">
                    {count} из {theme.max_slots} · {full ? 'мест нет' : `осталось ${avail}`}
                  </span>
                </div>
              </div>
            </div>

            {/* Описание */}
            {cleanDesc && (
              <div className="detail-description">{cleanDesc}</div>
            )}

            {/* Организатор */}
            <div className="detail-creator">
              <div className="detail-creator-avatar">{initials(theme.creator.full_name)}</div>
              <div className="detail-creator-info">
                <div className="detail-creator-name">{theme.creator.full_name ?? theme.creator.username}</div>
                <div className="detail-creator-sub">
                  {isOwner ? '👑 Вы организатор' : `@${theme.creator.username ?? 'организатор'}`}
                </div>
              </div>
            </div>
          </div>

          {/* Кнопки действий */}
          <div className="modal-footer">
            {role === 'none' && !full && (
              <button className="btn-join" onClick={()=>setConfirm('join')} disabled={loading}>
                <FiUserPlus size={16}/> Присоединиться
              </button>
            )}
            {role === 'none' && full && (
              <button className="btn-join" disabled>
                <FiUsers size={16}/> Мест нет
              </button>
            )}
            {(role === 'member' || role === 'pending') && (
              <>
                <span style={{
                  flex:1, display:'flex', alignItems:'center', justifyContent:'center',
                  fontSize:'0.8rem', color:'var(--tg-theme-hint-color,#888)'
                }}>
                  {role === 'pending' ? '⏳ Заявка на рассмотрении' : '✓ Вы участвуете'}
                </span>
                <button className="btn-danger" onClick={()=>setConfirm('cancel')} disabled={loading}>
                  <FiUserMinus size={15}/> Отменить заявку
                </button>
              </>
            )}
            {role === 'owner' && (
              <button className="btn-danger" style={{flex:1}} onClick={()=>setConfirm('delete')} disabled={loading}>
                <FiTrash2 size={15}/> Удалить мероприятие
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

// ─── MyEventsModal ────────────────────────────────────────────────────────────
function MyEventsModal({ onClose, myThemes, myRequests }:
  { onClose:()=>void; myThemes: Theme[]; myRequests: MyRequest[] }) {
  const [tab, setTab] = useState<'created'|'joined'>('created');
  const statusLabel = { pending:'Ожидает', approved:'Принята', rejected:'Отклонена' };
  const statusClass = { pending:'event-status--pending', approved:'event-status--approved', rejected:'' };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e=>e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Мои события</h2>
          <button className="modal-close" onClick={onClose}><FiX size={20}/></button>
        </div>
        <div className="events-tabs">
          <button className={`events-tab${tab==='created'?' active':''}`} onClick={()=>setTab('created')}>
            Я создал ({myThemes.length})
          </button>
          <button className={`events-tab${tab==='joined'?' active':''}`} onClick={()=>setTab('joined')}>
            Я участвую ({myRequests.length})
          </button>
        </div>
        <div className="modal-body">
          {tab==='created' && (myThemes.length===0
            ? <div className="events-empty">Вы ещё не создавали событий</div>
            : myThemes.map(t=>(
              <div key={t.id} className="event-card">
                <div className="card-tags">{(t.tags??[]).map(tg=><span key={tg} className="tag">#{tg}</span>)}</div>
                <div className="event-card-title">{t.title}</div>
                <div className="event-card-meta">
                  <span className="event-card-row"><FiClock size={11}/> {fmtDate(t.datetime)} · {fmtTime(t.datetime)}</span>
                  <span className="event-card-row"><FiMapPin size={11}/> {t.location}</span>
                  <span className="event-card-row"><FiUsers size={11}/> {requestsCount(t)} / {t.max_slots} участников</span>
                </div>
                <span className="event-status event-status--creator">👑 Организатор</span>
              </div>
            ))
          )}
          {tab==='joined' && (myRequests.length===0
            ? <div className="events-empty">Вы ещё не подавали заявок</div>
            : myRequests.map(r=>(
              <div key={r.id} className="event-card">
                <div className="card-tags">{(r.theme.tags??[]).map(tg=><span key={tg} className="tag">#{tg}</span>)}</div>
                <div className="event-card-title">{r.theme.title}</div>
                <div className="event-card-meta">
                  <span className="event-card-row"><FiClock size={11}/> {fmtDate(r.theme.datetime)} · {fmtTime(r.theme.datetime)}</span>
                  <span className="event-card-row"><FiMapPin size={11}/> {r.theme.location}</span>
                </div>
                <span className={`event-status ${statusClass[r.status]??''}`}>
                  {r.status==='approved'?'✓ ':r.status==='pending'?'⏳ ':'✗ '}{statusLabel[r.status]}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ─── CreateModal ──────────────────────────────────────────────────────────────
function CreateModal({ onClose, onCreated }:
  { onClose:()=>void; onCreated:(t:Theme)=>void }) {
  const [form, setForm] = useState<CreateFormData>(
    { title:'', description:'', datetime:'', location:'', max_slots:10, tags:[] }
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggleTag = (tag: string) =>
    setForm(f=>({...f, tags:f.tags.includes(tag)?f.tags.filter(t=>t!==tag):[...f.tags,tag]}));

  const handleSubmit = async () => {
    if (!form.title.trim()) { setError('Введите название'); return; }
    if (!form.datetime) { setError('Выберите дату и время'); return; }
    if (!form.location.trim()) { setError('Укажите место'); return; }

    const prefix = form.tags.map(t=>`#${t}`).join(' ');
    const desc = prefix ? `${prefix}\n${form.description}`.trim() : form.description.trim();
    const payload = {
      title:form.title.trim(), description:desc||undefined,
      datetime:new Date(form.datetime).toISOString(),
      location:form.location.trim(), max_slots:form.max_slots,
    };

    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/themes/`, {
        method:'POST', headers:authHeaders(), body:JSON.stringify(payload)
      });
      if (!res.ok) { const d=await res.json().catch(()=>({})); throw new Error(d.detail??`Ошибка ${res.status}`); }
      const created:Theme = await res.json();
      created.tags=form.tags; created.slots_available=created.max_slots; created.requests_count=0;
      onCreated(created); onClose();
    } catch(e:any) {
      if (e instanceof TypeError) {
        onCreated({ id:Date.now(), title:form.title.trim(), description:desc,
          datetime:new Date(form.datetime).toISOString(), location:form.location.trim(),
          max_slots:form.max_slots, slots_available:form.max_slots, requests_count:0,
          creator:MOCK_ME, tags:form.tags });
        onClose();
      } else { setError(e.message||'Ошибка'); }
    } finally { setLoading(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e=>e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Создать слот</h2>
          <button className="modal-close" onClick={onClose}><FiX size={20}/></button>
        </div>
        <div className="modal-body">
          {error && <div className="modal-error">{error}</div>}
          <div className="form-group">
            <label className="form-label">Название *</label>
            <input className="form-input" placeholder="Напр.: Поход на лекцию по ИИ"
              value={form.title} maxLength={255}
              onChange={e=>setForm(f=>({...f,title:e.target.value}))}/>
          </div>
          <div className="form-group">
            <label className="form-label">Тематика</label>
            <div className="tags-selector">
              {TOPICS.map(t=>(
                <button key={t} type="button"
                  className={`tag-btn${form.tags.includes(t)?' tag-btn--active':''}`}
                  onClick={()=>toggleTag(t)}>#{t}</button>
              ))}
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Описание</label>
            <textarea className="form-input form-textarea" placeholder="Подробнее о встрече…"
              value={form.description} maxLength={1000} rows={3}
              onChange={e=>setForm(f=>({...f,description:e.target.value}))}/>
          </div>
          <div className="form-row">
            <div className="form-group form-group--half">
              <label className="form-label">Дата и время *</label>
              <input className="form-input" type="datetime-local" value={form.datetime}
                onChange={e=>setForm(f=>({...f,datetime:e.target.value}))}/>
            </div>
            <div className="form-group form-group--half">
              <label className="form-label">Макс. мест</label>
              <input className="form-input" type="number" min={1} max={100} value={form.max_slots}
                onChange={e=>setForm(f=>({...f,max_slots:parseInt(e.target.value)||1}))}/>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Место встречи *</label>
            <input className="form-input" placeholder="Напр.: ауд.305 СПбПУ, Политехническая"
              value={form.location} maxLength={255}
              onChange={e=>setForm(f=>({...f,location:e.target.value}))}/>
            <div className="form-hint">Адрес или станция метро</div>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose}>Отмена</button>
          <button className="btn-submit" onClick={handleSubmit} disabled={loading}>
            {loading?'Создаём…':'Создать слот'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMyEvents, setShowMyEvents] = useState(false);
  const [selectedTheme, setSelectedTheme] = useState<Theme|null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDate, setFilterDate] = useState('');
  const [filterTopics, setFilterTopics] = useState<string[]>([]);
  const [filterMetro, setFilterMetro] = useState('');
  const [filterMinSlots, setFilterMinSlots] = useState(1);
  const [themes, setThemes] = useState<Theme[]>(MOCK_THEMES);
  const [myRequests, setMyRequests] = useState<MyRequest[]>(MOCK_MY_REQUESTS);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;
    tg.ready(); tg.expand();
    const upd = () => document.documentElement.style.setProperty('--tg-theme-bg-color', tg.backgroundColor);
    upd(); tg.onEvent('themeChanged', upd);
    return () => tg.offEvent('themeChanged', upd);
  }, []);

  useEffect(() => { document.body.classList.toggle('body-filters-open', showFilters); }, [showFilters]);

  const fetchThemes = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/themes/?limit=50&future_only=true`,
        { signal:AbortSignal.timeout(4000) });
      if (!res.ok) throw new Error();
      const data = await res.json();
      const list:Theme[] = Array.isArray(data)?data:(data.themes??[]);
      list.forEach(t=>{t.tags=extractTags(t.description);});
      if (list.length>0) setThemes(list);
    } catch { /* остаёмся на mock */ }
    finally { setLoading(false); }
  }, []);

  useEffect(()=>{ fetchThemes(); },[fetchThemes]);

  // Обработка действий с заявками (для DetailModal)
  const handleRequestChanged = (themeId: number, action: 'join'|'cancel') => {
    setThemes(prev=>prev.map(t=>{
      if (t.id!==themeId) return t;
      const delta = action==='join' ? 1 : -1;
      return {
        ...t,
        requests_count: (t.requests_count??0) + delta,
        slots_available: (t.slots_available??t.max_slots) - delta,
      };
    }));
    if (action==='join') {
      const theme = themes.find(t=>t.id===themeId);
      if (theme) setMyRequests(prev=>[...prev, { id:Date.now(), status:'pending', theme }]);
    } else {
      setMyRequests(prev=>prev.filter(r=>r.theme.id!==themeId));
    }
    // Обновляем selectedTheme чтобы кнопки сменились
    setSelectedTheme(prev=>{
      if (!prev||prev.id!==themeId) return prev;
      const delta = action==='join'?1:-1;
      return { ...prev,
        requests_count:(prev.requests_count??0)+delta,
        slots_available:(prev.slots_available??prev.max_slots)-delta };
    });
  };

  const myThemes = themes.filter(t=>t.creator.id===MOCK_ME.id);

  const filtered = themes.filter(t=>{
    if (searchQuery) {
      const q=searchQuery.toLowerCase();
      if (!t.title.toLowerCase().includes(q)&&
          !(t.description?.toLowerCase().includes(q))&&
          !(t.location.toLowerCase().includes(q))) return false;
    }
    if (filterDate && t.datetime.slice(0,10)!==filterDate) return false;
    if (filterTopics.length>0) {
      const tags=t.tags??extractTags(t.description);
      if (!filterTopics.some(tp=>tags.includes(tp))) return false;
    }
    if (filterMetro&&!t.location.toLowerCase().includes(filterMetro.toLowerCase())) return false;
    if (filterMinSlots>1&&slotsAvail(t)<filterMinSlots) return false;
    return true;
  });

  const activeFiltersCount=[filterDate,filterTopics.length>0,filterMetro,filterMinSlots>1].filter(Boolean).length;

  return (
    <div className="app">
      {showCreateModal && (
        <CreateModal onClose={()=>setShowCreateModal(false)} onCreated={t=>setThemes(p=>[t,...p])}/>
      )}
      {showMyEvents && (
        <MyEventsModal onClose={()=>setShowMyEvents(false)} myThemes={myThemes} myRequests={myRequests}/>
      )}
      {selectedTheme && (
        <DetailModal
          theme={selectedTheme}
          myRequests={myRequests}
          onClose={()=>setSelectedTheme(null)}
          onThemeDeleted={id=>{ setThemes(p=>p.filter(t=>t.id!==id)); setSelectedTheme(null); }}
          onRequestChanged={handleRequestChanged}
        />
      )}

      <header className="top-panel">
        <div className="top-row">
          <div className="logo-area">
            <img src={PolyLogo} alt="logo" width={33} height={33}/>
            <span className="app-title">PolyGang</span>
          </div>
          <button className="events-top-button" onClick={()=>setShowMyEvents(true)}>
            <FiCalendar size={22}/>
          </button>
        </div>
        <div className="search-row">
          <div className="search-input-wrap">
            <FiSearch size={13} className="search-icon"/>
            <input type="text" placeholder="Поиск…" className="search-input"
              value={searchQuery} onChange={e=>setSearchQuery(e.target.value)}/>
          </div>
          <button className={`filter-button${showFilters?' active':''}`}
            onClick={()=>setShowFilters(v=>!v)}>
            <FiFilter size={13}/> Фильтры
            {activeFiltersCount>0 && <span className="filter-badge">{activeFiltersCount}</span>}
          </button>
        </div>
        <div className={`filters-panel${showFilters?' open':''}`}>
          <div className="filter-group">
            <label>Дата:</label>
            <input type="date" value={filterDate} onChange={e=>setFilterDate(e.target.value)}/>
          </div>
          <div className="filter-group">
            <label>Свободных мест не менее:</label>
            <input type="number" min={1} value={filterMinSlots}
              onChange={e=>setFilterMinSlots(parseInt(e.target.value)||1)}/>
          </div>
          <div className="filter-group">
            <label>Тематика:</label>
            <div className="topics-list">
              {TOPICS.map(topic=>(
                <label key={topic} className="topic-checkbox">
                  <input type="checkbox" checked={filterTopics.includes(topic)}
                    onChange={()=>setFilterTopics(p=>
                      p.includes(topic)?p.filter(t=>t!==topic):[...p,topic])}/>
                  {topic}
                </label>
              ))}
            </div>
          </div>
          <div className="filter-group">
            <label>Станция метро:</label>
            <div className="metro-select">
              <div className={`metro-option${filterMetro===''?' selected':''}`}
                onClick={()=>setFilterMetro('')}>Все</div>
              {METRO_STATIONS.map(s=>(
                <div key={s} className={`metro-option${filterMetro===s?' selected':''}`}
                  onClick={()=>setFilterMetro(s)}>{s}</div>
              ))}
            </div>
          </div>
          <div className="filter-actions">
            <button className="reset-button" onClick={()=>{
              setFilterDate('');setFilterTopics([]);setFilterMetro('');setFilterMinSlots(1);
            }}>Сбросить</button>
            <button className="search-button" onClick={()=>setShowFilters(false)}>
              <FiSearch size={13}/> Найти
            </button>
          </div>
        </div>
      </header>

      <main className={`content${showFilters?' no-scroll':''}`}>
        <div className="content-toolbar">
          <span className="results-count">
            {loading?'Загрузка…':`${filtered.length} ${slotWord(filtered.length)}`}
          </span>
          <button className="mode-toggle-btn"
            onClick={()=>setViewMode(v=>v==='grid'?'list':'grid')}>
            {viewMode==='grid'?<FiList size={20}/>:<FiGrid size={20}/>}
          </button>
        </div>

        {filtered.length===0&&!loading&&(
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <div className="empty-text">Слоты не найдены</div>
            <div className="empty-hint">Измените фильтры или создайте новый слот</div>
          </div>
        )}

        {viewMode==='grid'&&(
          <div className="grid-container">
            {filtered.map(t=><GridCard key={t.id} theme={t} onClick={()=>setSelectedTheme(t)}/>)}
          </div>
        )}
        {viewMode==='list'&&(
          <div className="list-container">
            {filtered.map(t=><ListCard key={t.id} theme={t} onClick={()=>setSelectedTheme(t)}/>)}
          </div>
        )}
      </main>

      <footer className="bottom-panel">
        <button className="create-button" onClick={()=>setShowCreateModal(true)}>
          <FiPlusCircle size={17}/> Создать
        </button>
      </footer>
    </div>
  );
}

export default App;
