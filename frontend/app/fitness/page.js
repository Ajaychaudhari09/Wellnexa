'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function FitnessPage() {
  const router = useRouter();
  const [activity, setActivity] = useState({ steps: '', active_minutes: '', water_ml: '', sleep_hours: '' });
  const [trends, setTrends] = useState([]);
  const [workouts, setWorkouts] = useState([]);
  const [workout, setWorkout] = useState({ title: '', activity_type: 'WALKING', duration_minutes: 30, calories_burned: 0 });
  const [message, setMessage] = useState('');
  async function load() { try { const [a,t,w] = await Promise.all([api.request('/fitness/daily-activity'),api.request('/fitness/trends'),api.request('/fitness/workouts')]); setActivity({steps:a.steps,active_minutes:a.active_minutes,water_ml:a.water_ml,sleep_hours:a.sleep_hours}); setTrends(t.trends || []); setWorkouts(w || []); } catch(e) { setMessage(e.message); } }
  useEffect(() => { const t=localStorage.getItem('wellnexa_token'); if(!t){router.push('/');return;} api.setToken(t); load(); },[router]);
  async function saveActivity(e){e.preventDefault();try{await api.request('/fitness/daily-activity',{method:'POST',body:JSON.stringify(Object.fromEntries(Object.entries(activity).map(([k,v])=>[k,v===''?null:Number(v)])))});setMessage('Activity saved.');await load();}catch(e){setMessage(e.message);}}
  async function saveWorkout(e){e.preventDefault();try{await api.request('/fitness/workouts',{method:'POST',body:JSON.stringify({...workout,duration_minutes:Number(workout.duration_minutes),calories_burned:Number(workout.calories_burned)})});setMessage('Workout logged.');setWorkout({...workout,title:''});await load();}catch(e){setMessage(e.message);}}
  return <main className="container"><nav className="nav"><a href="/dashboard">Dashboard</a></nav><h1>Fitness and Activity</h1>
    <form className="card" onSubmit={saveActivity}><h2>Daily activity</h2>{[['steps','Steps'],['active_minutes','Active minutes'],['water_ml','Water (ml)'],['sleep_hours','Sleep (hours)']].map(([k,l])=><label className="label" key={k}>{l}<input className="input" type="number" min="0" step={k==='sleep_hours'?'0.1':'1'} value={activity[k]??''} onChange={e=>setActivity({...activity,[k]:e.target.value})}/></label>)}<button className="btn">Save activity</button></form>
    <form className="card" onSubmit={saveWorkout}><h2>Log workout</h2><label className="label">Activity<input className="input" required value={workout.title} onChange={e=>setWorkout({...workout,title:e.target.value})}/></label><label className="label">Type<select className="input" value={workout.activity_type} onChange={e=>setWorkout({...workout,activity_type:e.target.value})}>{['WALKING','RUNNING','CYCLING','SWIMMING','STRENGTH_TRAINING','YOGA','CUSTOM'].map(x=><option key={x}>{x}</option>)}</select></label><label className="label">Minutes<input className="input" type="number" min="1" required value={workout.duration_minutes} onChange={e=>setWorkout({...workout,duration_minutes:e.target.value})}/></label><label className="label">Calories burned (optional)<input className="input" type="number" min="0" value={workout.calories_burned} onChange={e=>setWorkout({...workout,calories_burned:e.target.value})}/></label><button className="btn">Log workout</button></form>
    {message&&<p role="status">{message}</p>}<section className="card"><h2>Recent activity</h2>{trends.map(d=><p key={d.date}>{d.date}: {d.steps} steps · {d.sleep_hours} h sleep · {d.water_ml} ml water</p>)}{workouts.map(w=><p key={w.id}>{w.logged_date}: {w.title} · {w.duration_minutes} min</p>)}</section>
  </main>;
}
