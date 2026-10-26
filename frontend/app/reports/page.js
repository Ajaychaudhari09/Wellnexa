'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';

export default function Reports() {
  const router = useRouter();
  const [list, setList] = useState([]);
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  useEffect(() => {
    const t = localStorage.getItem('wellnexa_token'); if (!t) { router.push('/'); return; }
    api.token = t;
    api.reports().then(setList).catch(() => {});
  }, [router]);
  async function upload(e) {
    e.preventDefault();
    if (!file) return;
    try {
      const doc = await api.uploadDocument(file);
      const report = await api.processReport(doc.id);
      setText(report?.extractions?.map(x => `${x.test_name}: ${x.detected_value} ${x.unit || ''}`).join('\n') || 'OCR completed. Review the detected report fields in saved reports.');
      api.reports().then(setList).catch(() => {});
    } catch (err) { setText(err.message); }
  }
  return (
    <div>
      <div className="nav"><strong>WellNexa AI</strong><a href="/dashboard">Dashboard</a></div>
      <div className="container">
        <h1>Report Analyzer</h1>
        <div className="warn">AI-generated explanations are not medical advice.</div>
        <form className="card" onSubmit={upload}>
          <input type="file" accept=".pdf,image/*" onChange={e => setFile(e.target.files[0])} />
          <button className="btn" type="submit" style={{ marginLeft: '.5rem' }}>Upload & OCR</button>
        </form>
        {text && <div className="card"><h3>Extracted text</h3><pre style={{ whiteSpace: 'pre-wrap' }}>{text}</pre></div>}
        <div className="card"><h3>Saved reports</h3><ul>{list.map((r, i) => <li key={i}>{r.report_type} — {r.status} ({r.extractions?.length || 0} values)</li>)}</ul></div>
      </div>
    </div>
  );
}
