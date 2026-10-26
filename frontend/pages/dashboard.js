import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import api from '../lib/api';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  useEffect(() => {
    const t = typeof window !== 'undefined' ? localStorage.getItem('wellnexa_token') : null;
    if (!t) { router.push('/'); return; }
    api.token = t;
    setUser({ email: 'user' });
  }, [router]);
  function logout() { api.setToken(null); router.push('/'); }
  return (
    <div>
      <div className="nav">
        <strong>WellNexa AI</strong>
        <a href="/dashboard">Dashboard</a>
        <a href="/profile">Profile</a>
        <a href="/reports">Reports</a>
        <a href="/assistant">Assistant</a>
        <span style={{ marginLeft: 'auto' }}><button className="btn" onClick={logout}>Logout</button></span>
      </div>
      <div className="container">
        <h1>Health Dashboard</h1>
        <div className="warn">AI-generated content is not medical advice. Consult a qualified professional for medical decisions.</div>
        <div className="row" style={{ marginTop: '1rem' }}>
          <div className="col card"><h3>Medical</h3><p>Reports, timeline, trends.</p></div>
          <div className="col card"><h3>Nutrition</h3><p>Food logging and meal suggestions.</p></div>
          <div className="col card"><h3>Fitness</h3><p>Steps, sleep, water, weight.</p></div>
          <div className="col card"><h3>Wellness</h3><p>Mood journal and stress tracking.</p></div>
          <div className="col card"><h3>Medicines</h3><p>Schedules and refill alerts.</p></div>
          <div className="col card"><h3>Appointments</h3><p>Upcoming visits.</p></div>
        </div>
      </div>
    </div>
  );
}
