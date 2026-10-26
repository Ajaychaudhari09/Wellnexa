'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function AppointmentsPage() {
  const router = useRouter();
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ doctor_name: '', specialty: 'General Medicine', appointment_date: '', appointment_time: '10:00', purpose: '', appointment_type: 'IN_PERSON' });
  const [message, setMessage] = useState('');
  async function load() { try { setItems(await api.request('/appointments')); } catch (e) { setMessage(e.message); } }
  useEffect(() => { const t = localStorage.getItem('wellnexa_token'); if (!t) { router.push('/'); return; } api.setToken(t); load(); }, [router]);
  async function create(e) { e.preventDefault(); setMessage(''); try { await api.request('/appointments', { method: 'POST', body: JSON.stringify(form) }); setMessage('Appointment saved.'); await load(); } catch (e) { setMessage(e.message); } }
  async function cancel(id) { try { await api.request(`/appointments/${id}`, { method: 'DELETE' }); await load(); } catch (e) { setMessage(e.message); } }
  return <main className="container"><nav className="nav"><a href="/dashboard">Dashboard</a><a href="/notifications">Notifications</a></nav><h1>Appointments</h1>
    <form className="card" onSubmit={create}><h2>Schedule an appointment</h2>
      <label className="label">Doctor or provider</label><input className="input" required value={form.doctor_name} onChange={e => setForm({ ...form, doctor_name: e.target.value })}/>
      <label className="label">Specialty</label><input className="input" value={form.specialty} onChange={e => setForm({ ...form, specialty: e.target.value })}/>
      <label className="label">Date</label><input className="input" type="date" required value={form.appointment_date} onChange={e => setForm({ ...form, appointment_date: e.target.value })}/>
      <label className="label">Time</label><input className="input" type="time" required value={form.appointment_time} onChange={e => setForm({ ...form, appointment_time: e.target.value })}/>
      <label className="label">Purpose</label><input className="input" required value={form.purpose} onChange={e => setForm({ ...form, purpose: e.target.value })}/>
      <button className="btn" type="submit">Save appointment</button>{message && <p role="status">{message}</p>}
    </form>
    <section className="row">{items.map(item => <article className="card col" key={item.id}><h2>{item.doctor_name}</h2><p>{item.appointment_date} at {item.appointment_time}</p><p>{item.purpose}</p><p>{item.status}</p>{item.status !== 'CANCELLED' && <button className="btn" onClick={() => cancel(item.id)}>Cancel</button>}</article>)}</section>
  </main>;
}
