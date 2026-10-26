'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function MedicinesPage(){
 const router=useRouter();const [items,setItems]=useState([]);const [form,setForm]=useState({name:'',dosage:'',form:'TABLET',frequency:'ONCE_DAILY',timing:'AFTER_MEAL'});const [message,setMessage]=useState('');
 async function load(){try{setItems(await api.request('/medicines'));}catch(e){setMessage(e.message);}}
 useEffect(()=>{const t=localStorage.getItem('wellnexa_token');if(!t){router.push('/');return;}api.setToken(t);load();},[router]);
 async function save(e){e.preventDefault();try{await api.request('/medicines',{method:'POST',body:JSON.stringify(form)});setForm({...form,name:'',dosage:''});setMessage('Medicine saved.');await load();}catch(e){setMessage(e.message);}}
 async function logDose(id){try{await api.request(`/medicines/${id}/log-dose`,{method:'POST',body:JSON.stringify({status:'TAKEN'})});setMessage('Dose logged.');await load();}catch(e){setMessage(e.message);}}
 return <main className="container"><nav className="nav"><a href="/dashboard">Dashboard</a></nav><h1>Medicines</h1><form className="card" onSubmit={save}><h2>Add medicine</h2><label className="label">Name<input className="input" required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label><label className="label">Dose<input className="input" required value={form.dosage} onChange={e=>setForm({...form,dosage:e.target.value})}/></label><label className="label">Form<select className="input" value={form.form} onChange={e=>setForm({...form,form:e.target.value})}>{['TABLET','CAPSULE','LIQUID','INJECTION','OTHER'].map(x=><option key={x}>{x}</option>)}</select></label><label className="label">Frequency<select className="input" value={form.frequency} onChange={e=>setForm({...form,frequency:e.target.value})}>{['ONCE_DAILY','TWICE_DAILY','THREE_TIMES_DAILY','AS_NEEDED','WEEKLY'].map(x=><option key={x}>{x}</option>)}</select></label><button className="btn">Save medicine</button></form>{message&&<p role="status">{message}</p>}<section className="row">{items.map(x=><article className="card col" key={x.id}><h2>{x.name}</h2><p>{x.dosage} · {x.frequency} · {x.timing}</p>{x.is_active&&<button className="btn" onClick={()=>logDose(x.id)}>Log dose taken</button>}</article>)}</section></main>;
}
