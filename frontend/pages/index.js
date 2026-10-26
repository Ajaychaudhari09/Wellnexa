import { useState } from 'react';
import { useRouter } from 'next/router';
import api from '../lib/api';

export default function Home() {
  const router = useRouter();
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('patient');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setErr(''); setLoading(true);
    try {
      if (mode === 'login') {
        const data = await api.login(email, password);
        api.setToken(data.access_token);
        if (typeof window !== 'undefined') localStorage.setItem('wellnexa_role', data.role || role);
        router.push('/dashboard');
      } else {
        await api.register({ email, password, full_name: name, role });
        setMode('login');
      }
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  }

  return (
    <div className="container" style={{ maxWidth: 420, marginTop: '4rem' }}>
      <div className="card">
        <h1>WellNexa AI</h1>
        <p className="badge">AI-generated content is not medical advice</p>
        <div style={{ display: 'flex', gap: '.5rem', margin: '1rem 0' }}>
          <button className="btn" onClick={() => setMode('login')} disabled={mode === 'login'}>Login</button>
          <button className="btn" onClick={() => setMode('register')} disabled={mode === 'register'}>Register</button>
        </div>
        <form onSubmit={submit}>
          {mode === 'register' && (
            <>
              <label className="label">Full name</label>
              <input className="input" value={name} onChange={e => setName(e.target.value)} required />
              <label className="label">Role</label>
              <select className="input" value={role} onChange={e => setRole(e.target.value)}>
                <option value="patient">Patient</option>
                <option value="doctor">Doctor</option>
                <option value="admin">Admin</option>
              </select>
            </>
          )}
          <label className="label">Email</label>
          <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          <label className="label">Password</label>
          <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          {err && <p style={{ color: 'red' }}>{err}</p>}
          <button className="btn" type="submit" disabled={loading}>{loading ? '...' : (mode === 'login' ? 'Login' : 'Register')}</button>
        </form>
      </div>
    </div>
  );
}
