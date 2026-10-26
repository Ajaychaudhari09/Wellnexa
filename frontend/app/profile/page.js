'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function Profile() {
  const router = useRouter();
  const [form, setForm] = useState({ age: '', height_cm: '', weight_kg: '', blood_pressure: '', glucose: '', allergies: '', lifestyle: '', goals: '' });
  const [bmi, setBmi] = useState(null);
  const [msg, setMsg] = useState('');
  useEffect(() => {
    const t = localStorage.getItem('wellnexa_token'); if (!t) { router.push('/'); return; }
    api.token = t;
    api.profile().then(d => { if (d) setForm(f => ({ ...f, ...d })); }).catch(() => {});
  }, [router]);
  function calcBmi() {
    const h = parseFloat(form.height_cm) / 100; const w = parseFloat(form.weight_kg);
    if (h > 0 && w > 0) setBmi((w / (h * h)).toFixed(1));
  }
  async function save(e) {
    e.preventDefault(); calcBmi();
    try { await api.saveProfile({ ...form, bmi }); setMsg('Saved'); }
    catch (e) { setMsg(e.message); }
  }
  return (
    <div>
      <div className="nav"><strong>WellNexa AI</strong><a href="/dashboard">Dashboard</a></div>
      <div className="container">
        <h1>Personal Health Profile</h1>
        <form className="card" onSubmit={save}>
          <div className="row">
            <div className="col"><label className="label">Age</label><input className="input" type="number" value={form.age} onChange={e => setForm({ ...form, age: e.target.value })} /></div>
            <div className="col"><label className="label">Height (cm)</label><input className="input" type="number" value={form.height_cm} onChange={e => setForm({ ...form, height_cm: e.target.value })} onBlur={calcBmi} /></div>
            <div className="col"><label className="label">Weight (kg)</label><input className="input" type="number" value={form.weight_kg} onChange={e => setForm({ ...form, weight_kg: e.target.value })} onBlur={calcBmi} /></div>
          </div>
          <p>BMI: <strong>{bmi || form.bmi || '—'}</strong> <span className="badge">WHO adult categories</span></p>
          <label className="label">Blood pressure</label><input className="input" value={form.blood_pressure} onChange={e => setForm({ ...form, blood_pressure: e.target.value })} />
          <label className="label">Fasting glucose (mg/dL)</label><input className="input" value={form.glucose} onChange={e => setForm({ ...form, glucose: e.target.value })} />
          <label className="label">Allergies</label><input className="input" value={form.allergies} onChange={e => setForm({ ...form, allergies: e.target.value })} />
          <label className="label">Lifestyle</label><input className="input" value={form.lifestyle} onChange={e => setForm({ ...form, lifestyle: e.target.value })} />
          <label className="label">Goals</label><input className="input" value={form.goals} onChange={e => setForm({ ...form, goals: e.target.value })} />
          <button className="btn" type="submit">Save</button>
          {msg && <p>{msg}</p>}
        </form>
      </div>
    </div>
  );
}
