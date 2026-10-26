'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function Profile() {
  const router = useRouter();
  const [form, setForm] = useState({ first_name: '', last_name: '', phone_number: '', gender: 'PREFER_NOT_TO_SAY', blood_group: 'UNKNOWN' });
  const [msg, setMsg] = useState('');
  useEffect(() => {
    const t = localStorage.getItem('wellnexa_token'); if (!t) { router.push('/'); return; }
    api.token = t;
    api.profile().then(d => { if (d) setForm(f => ({ ...f, ...d })); }).catch(() => {});
  }, [router]);
  async function save(e) {
    e.preventDefault();
    try { await api.saveProfile(form); setMsg('Saved'); }
    catch (e) { setMsg(e.message); }
  }
  return (
    <div>
      <div className="nav"><strong>WellNexa AI</strong><a href="/dashboard">Dashboard</a></div>
      <div className="container">
        <h1>Personal Health Profile</h1>
        <form className="card" onSubmit={save}>
          <label className="label">First name</label><input className="input" value={form.first_name || ''} onChange={e => setForm({ ...form, first_name: e.target.value })} required />
          <label className="label">Last name</label><input className="input" value={form.last_name || ''} onChange={e => setForm({ ...form, last_name: e.target.value })} required />
          <label className="label">Phone number</label><input className="input" type="tel" value={form.phone_number || ''} onChange={e => setForm({ ...form, phone_number: e.target.value })} />
          <label className="label">Gender</label><select className="input" value={form.gender || 'PREFER_NOT_TO_SAY'} onChange={e => setForm({ ...form, gender: e.target.value })}>{['MALE','FEMALE','OTHER','PREFER_NOT_TO_SAY'].map(v => <option key={v} value={v}>{v.replaceAll('_',' ')}</option>)}</select>
          <label className="label">Blood group</label><select className="input" value={form.blood_group || 'UNKNOWN'} onChange={e => setForm({ ...form, blood_group: e.target.value })}>{['A_POSITIVE','A_NEGATIVE','B_POSITIVE','B_NEGATIVE','AB_POSITIVE','AB_NEGATIVE','O_POSITIVE','O_NEGATIVE','UNKNOWN'].map(v => <option key={v} value={v}>{v.replaceAll('_',' ')}</option>)}</select>
          <button className="btn" type="submit">Save</button>
          {msg && <p>{msg}</p>}
        </form>
      </div>
    </div>
  );
}
