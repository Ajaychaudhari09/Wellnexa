const API_BASE = '/api/v1';
export const api = {
  token: null,
  setToken(t) { this.token = t; if (typeof window !== 'undefined') { if (t) localStorage.setItem('wellnexa_token', t); else localStorage.removeItem('wellnexa_token'); } },
  init() { if (typeof window !== 'undefined') this.token = localStorage.getItem('wellnexa_token'); },
  async request(endpoint, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    const json = await res.json().catch(() => null);
    if (!res.ok) throw new Error(json?.detail || json?.message || json?.errors?.join?.(', ') || res.statusText);
    return json?.data !== undefined ? json.data : json;
  },
  login(email, password) { return this.request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }); },
  register(payload) { return this.request('/auth/register', { method: 'POST', body: JSON.stringify(payload) }); },
  profile() { return this.request('/profile/me'); },
  saveProfile(p) { return this.request('/profile/me', { method: 'PUT', body: JSON.stringify(p) }); },
  assistant(q) { return this.request('/assistant/sessions', { method: 'POST', body: JSON.stringify({}) }).then(s => this.request(`/assistant/sessions/${s.id}/messages`, { method: 'POST', body: JSON.stringify({ message: q }) })); },
  reports() { return this.request('/reports').then(d => Array.isArray(d) ? d : d?.items || []); },
  async uploadDocument(file) {
    const fd = new FormData(); fd.append('file', file);
    const res = await fetch('/api/v1/documents/upload', { method: 'POST', headers: { Authorization: `Bearer ${this.token}` }, body: fd });
    const json = await res.json().catch(() => null);
    if (!res.ok) throw new Error(json?.detail || json?.message || res.statusText);
    return json?.data !== undefined ? json.data : json;
  },
  processReport(docId) { return this.request(`/reports/process-ocr/${docId}`, { method: 'POST' }); },
};
export default api;
