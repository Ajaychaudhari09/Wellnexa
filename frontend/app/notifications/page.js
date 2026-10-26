'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function NotificationsPage() {
  const router = useRouter();
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState('');

  const load = useCallback(async () => {
    try {
      const rows = await api.request('/notifications');
      setItems(Array.isArray(rows) ? rows : []);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('wellnexa_token');
    if (!token) { router.push('/'); return; }
    api.setToken(token);
    load();
  }, [load, router]);

  async function markRead(id) {
    setBusy(id);
    try {
      await api.request(`/notifications/${id}/read`, { method: 'POST' });
      setItems(current => current.map(item => item.id === id ? { ...item, is_read: true, read_at: new Date().toISOString() } : item));
    } catch (e) { setError(e.message); }
    finally { setBusy(''); }
  }

  async function markAllRead() {
    setBusy('all');
    try {
      await api.request('/notifications/mark-all-read', { method: 'POST' });
      setItems(current => current.map(item => ({ ...item, is_read: true, read_at: new Date().toISOString() })));
    } catch (e) { setError(e.message); }
    finally { setBusy(''); }
  }

  const unreadCount = items.filter(item => !item.is_read).length;
  return (
    <main className="container">
      <nav className="nav"><strong>WellNexa AI</strong><a href="/dashboard">Dashboard</a><a href="/nutrition">Nutrition</a><a href="/appointments">Appointments</a><a href="/reminders">Reminders</a><a href="/fitness">Fitness</a><a href="/wellness">Wellness</a></nav>
      <header className="row" style={{ alignItems: 'center', justifyContent: 'space-between' }}>
        <div><h1>Notifications</h1><p>{unreadCount} unread</p></div>
        <button className="btn" onClick={markAllRead} disabled={!unreadCount || busy !== ''}>Mark all as read</button>
      </header>
      {error && <p role="alert">Could not update notifications: {error}</p>}
      {items.length === 0 && !error && <section className="card"><p>You have no notifications.</p></section>}
      <section aria-label="Notifications" className="row">
        {items.map(item => (
          <article className="card col" key={item.id} style={{ opacity: item.is_read ? 0.72 : 1 }}>
            <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>{item.title}</h2><span className="badge">{item.is_read ? 'Read' : 'Unread'}</span>
            </div>
            <p>{item.body}</p>
            <small>{new Date(item.created_at).toLocaleString()}</small>
            <div style={{ marginTop: '.75rem' }}>
              {!item.is_read && <button className="btn" onClick={() => markRead(item.id)} disabled={busy !== ''}>{busy === item.id ? 'Saving…' : 'Mark as read'}</button>}
              {item.action_url && <a className="btn" style={{ marginLeft: '.5rem' }} href={item.action_url}>Open</a>}
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
