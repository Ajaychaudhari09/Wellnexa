'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function Dashboard() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const t = typeof window !== 'undefined' ? localStorage.getItem('wellnexa_token') : null;
    if (!t) { router.push('/'); return; }
    api.setToken(t);
    api.request('/dashboard/home').then(setDashboard).catch(e => setError(e.message));
  }, [router]);
  function logout() { api.setToken(null); router.push('/'); }
  return (
    <div>
      <div className="nav"><strong>WellNexa AI</strong><a href="/dashboard">Dashboard</a><a href="/profile">Profile</a><a href="/reports">Reports</a><a href="/assistant">Assistant</a><a href="/notifications">Notifications</a><span style={{ marginLeft: 'auto' }}><button className="btn" onClick={logout}>Logout</button></span></div>
      <div className="container">
        <h1>Health Dashboard</h1>
        <div className="warn">AI-generated content is not medical advice. Consult a qualified professional for medical decisions.</div>
        {error && <p role="alert">Dashboard could not load: {error}</p>}
        {dashboard && <>
          <h2>{dashboard.greeting}</h2>
          <div className="row" style={{ marginTop: '1rem' }}>
            <div className="col card"><h3>BMI</h3><p>{dashboard.vitals?.bmi ?? '—'} {dashboard.vitals?.bmi_category || ''}</p></div>
            <div className="col card"><h3>Nutrition today</h3><p>{dashboard.nutrition?.calories_consumed ?? 0} / {dashboard.nutrition?.calorie_target ?? 0} kcal</p></div>
            <div className="col card"><h3>Today's mood</h3><p>{dashboard.mood?.mood_score ?? 'Not logged'}</p></div>
            <div className="col card"><h3>Medicine doses</h3><p>{dashboard.medicines?.taken_count ?? 0} taken / {dashboard.medicines?.total_scheduled ?? 0}</p></div>
          </div>
        </>}
        <div className="row" style={{ marginTop: '1rem' }}>
          {[
            ['Medical', dashboard?.latest_report?.has_reports ? `${dashboard.latest_report.flagged_count || 0} flagged values in latest report` : 'No reports yet'],
            ['Nutrition', `${dashboard?.nutrition?.calories_consumed ?? 0} kcal logged today`],
            ['Reminders', `${dashboard?.reminders?.total_due ?? 0} due today`],
            ['Fitness', 'Track steps, workouts, sleep and water'],
            ['Wellness', dashboard?.mood?.is_logged_today ? `Mood logged: ${dashboard.mood.mood_score}/5` : 'No mood check-in today'],
            ['Medicines', `${dashboard?.medicines?.pending_count ?? 0} doses pending`],
            ['Appointments', 'View and manage appointments in your health records'],
          ].map(([x, summary]) => (
            <article key={x} className="col card"><h3>{x}</h3><p>{summary}</p>
              {x === 'Appointments' && <a href="/appointments">Manage appointments</a>}
              {x === 'Nutrition' && <a href="/nutrition">Log meals</a>}
              {x === 'Reminders' && <a href="/reminders">Manage reminders</a>}
              {x === 'Fitness' && <a href="/fitness">Activity details</a>}
              {x === 'Wellness' && <a href="/wellness">Mood history</a>}
              {x === 'Medicines' && <a href="/medicines">Manage medicines</a>}
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
