'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function WellnessPage(){
 const router=useRouter();const [mood,setMood]=useState({mood_score:3,primary_emotion:'CONTENT',gratitude_note:''});const [items,setItems]=useState([]);const [message,setMessage]=useState('');
 async function load(){try{setItems(await api.request('/wellness/mood'));}catch(e){setMessage(e.message);}}
 useEffect(()=>{const t=localStorage.getItem('wellnexa_token');if(!t){router.push('/');return;}api.setToken(t);load();},[router]);
 async function save(e){e.preventDefault();try{await api.request('/wellness/mood',{method:'POST',body:JSON.stringify({...mood,mood_score:Number(mood.mood_score)})});setMessage('Mood check-in saved.');await load();}catch(e){setMessage(e.message);}}
 return <main className="container"><nav className="nav"><a href="/dashboard">Dashboard</a></nav><h1>Mental wellness</h1><div className="warn">This journal is for reflection and is not a diagnosis or treatment service.</div><form className="card" onSubmit={save}><label className="label">Mood (1–5)<input className="input" type="number" min="1" max="5" value={mood.mood_score} onChange={e=>setMood({...mood,mood_score:e.target.value})}/></label><label className="label">Emotion<select className="input" value={mood.primary_emotion} onChange={e=>setMood({...mood,primary_emotion:e.target.value})}>{['CONTENT','CALM','HAPPY','FOCUSED','ENERGETIC','ANXIOUS','SAD','STRESSED','ANGRY','TIRED'].map(x=><option key={x}>{x}</option>)}</select></label><label className="label">Gratitude note<textarea className="input" value={mood.gratitude_note} onChange={e=>setMood({...mood,gratitude_note:e.target.value})}/></label><button className="btn">Save check-in</button></form>{message&&<p role="status">{message}</p>}<section className="card"><h2>Recent check-ins</h2>{items.map(x=><p key={x.id}>{x.logged_date}: mood {x.mood_score}/5 · {x.primary_emotion}</p>)}</section></main>;
}
