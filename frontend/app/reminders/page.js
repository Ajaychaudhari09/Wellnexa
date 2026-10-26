'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function RemindersPage() {
  const router = useRouter();
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ title: '', reminder_type: 'CUSTOM', recurrence: 'ONCE', due_date: '', due_time: '09:00' });
  const [message, setMessage] = useState('');
  async function load() { try { setItems(await api.request('/reminders')); } catch (e) { setMessage(e.message); } }
  useEffect(() => { const t = localStorage.getItem('wellnexa_token'); if (!t) { router.push('/'); return; } api.setToken(t); load(); }, [router]);
  async function create(e) { e.preventDefault(); const body = { ...form, due_date: form.due_date || null }; try { await api.request('/reminders', { method: 'POST', body: JSON.stringify(body) }); setMessage('Reminder saved.'); setForm({ ...form, title: '' }); await load(); } catch (e) { setMessage(e.message); } }
  async function complete(id) { try { await api.request(`/reminders/${id}/action`, { method: 'POST', body: JSON.stringify({ status: 'COMPLETED' }) }); await load(); } catch (e) { setMessage(e.message); } }
  async function remove(id) { try { await api.request(`/reminders/${id}`, { method: 'DELETE' }); await load(); } catch (e) { setMessage(e.message); } }
  return <main className="container"><nav className="nav"><a href="/dashboard">Dashboard</a><a href="/notifications">Notifications</a></nav><h1>Reminders</h1>
    <form className="card" onSubmit={create}><h2>Create reminder</h2><label className="label">Title</label><input className="input" required value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}/>
      <label className="label">Type</label><select className="input" value={form.reminder_type} onChange={e => setForm({ ...form, reminder_type: e.target.value })}>{['CUSTOM','MEDICINE','APPOINTMENT','LAB_TEST','CHECKUP','REFILL','VACCINATION','WATER','EXERCISE','WELLNESS'].map(v => <option key={v}>{v}</option>)}</select>
      <label className="label">Recurrence</label><select className="input" value={form.recurrence} onChange={e => setForm({ ...form, recurrence: e.target.value })}>{['ONCE','DAILY','WEEKLY','MONTHLY'].map(v => <option key={v}>{v}</option>)}</select>
      {form.recurrence === 'ONCE' && <><label className="label">Date</label><input className="input" type="date" required value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })}/></>}
      <label className="label">Time</label><input className="input" type="time" required value={form.due_time} onChange={e => setForm({ ...form, due_time: e.target.value })}/><button className="btn" type="submit">Save reminder</button>{message && <p role="status">{message}</p>}</form>
    <section className="row">{items.map(item => <article className="card col" key={item.id}><h2>{item.title}</h2><p>{item.reminder_type} · {item.recurrence} · {item.due_time}</p>{item.due_date && <p>{item.due_date}</p>}<button className="btn" onClick={() => complete(item.id)}>Done</button><button className="btn" style={{ marginLeft: '.5rem' }} onClick={() => remove(item.id)}>Delete</button></article>)}</section>
  </main>;
}
