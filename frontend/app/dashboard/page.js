'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const router = useRouter();
  useEffect(() => {
    const t = typeof window !== 'undefined' ? localStorage.getItem('wellnexa_token') : null;
    if (!t) router.push('/');
  }, [router]);
  function logout() { localStorage.removeItem('wellnexa_token'); router.push('/'); }
  return (
    <div>
      <div className="nav"><strong>WellNexa AI</strong><a href="/dashboard">Dashboard</a><a href="/profile">Profile</a><a href="/reports">Reports</a><a href="/assistant">Assistant</a><span style={{ marginLeft: 'auto' }}><button className="btn" onClick={logout}>Logout</button></span></div>
      <div className="container">
        <h1>Health Dashboard</h1>
        <div className="warn">AI-generated content is not medical advice. Consult a qualified professional for medical decisions.</div>
        <div className="row" style={{ marginTop: '1rem' }}>
          {['Medical','Nutrition','Fitness','Wellness','Medicines','Appointments'].map(x => (
            <div key={x} className="col card"><h3>{x}</h3><p>Module summary from API.</p></div>
          ))}
        </div>
      </div>
    </div>
  );
}
