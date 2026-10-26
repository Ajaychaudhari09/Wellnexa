'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function Assistant() {
  const router = useRouter();
  const [q, setQ] = useState('');
  const [msgs, setMsgs] = useState([]);
  useEffect(() => {
    const t = localStorage.getItem('wellnexa_token'); if (!t) { router.push('/'); return; }
    api.token = t;
  }, [router]);
  async function send(e) {
    e.preventDefault();
    const question = q; setQ('');
    setMsgs(m => [...m, { role: 'user', text: question }]);
    try {
      const sess = await api.request('/assistant/sessions', { method: 'POST', body: JSON.stringify({}) });
      const data = await api.request(`/assistant/sessions/${sess.id}/messages`, { method: 'POST', body: JSON.stringify({ message: question }) });
      const answer = data?.content || data?.response || JSON.stringify(data);
      setMsgs(m => [...m, { role: 'ai', text: answer + '\n\nAI-generated, not medical advice.' }]);
    } catch (e) { setMsgs(m => [...m, { role: 'ai', text: e.message }]); }
  }
  return (
    <div>
      <div className="nav"><strong>WellNexa AI</strong><a href="/dashboard">Dashboard</a></div>
      <div className="container">
        <h1>AI Health Assistant</h1>
        <div className="warn">AI-generated, not medical advice. Consult a qualified professional.</div>
        <div className="card" style={{ minHeight: 300 }}>
          {msgs.map((m, i) => <p key={i}><strong>{m.role === 'user' ? 'You' : 'AI'}:</strong> {m.text}</p>)}
        </div>
        <form onSubmit={send} className="row">
          <input className="input" style={{ flex: 1 }} value={q} onChange={e => setQ(e.target.value)} placeholder="Ask a general health question..." />
          <button className="btn" type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}
