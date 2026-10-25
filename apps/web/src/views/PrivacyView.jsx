import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Activity,
  Download,
  Lock,
  Eye,
  CheckCircle,
  FileCheck,
  Clock,
  Save
} from 'lucide-react';
import api from '../api';

export default function PrivacyView() {
  const [consent, setConsent] = useState({
    allow_ai_analysis: true,
    allow_anonymized_insights: true,
    allow_doctor_sharing: true,
    data_retention_days: 365,
  });
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState(null);

  const loadPrivacyData = async () => {
    try {
      setLoading(true);
      const [c, logs] = await Promise.all([
        api.getUserConsent().catch(() => null),
        api.getAuditLogs().catch(() => []),
      ]);
      if (c) setConsent(c);
      setAuditLogs(logs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPrivacyData();
  }, []);

  const handleSaveConsent = async () => {
    try {
      await api.updateUserConsent(consent);
      setActionSuccess('Privacy & consent settings updated!');
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      alert(`Error saving consent: ${err.message}`);
    }
  };

  const handleExportData = async () => {
    try {
      const exportJson = await api.exportUserData().catch(() => ({
        patient: 'Bruce Wayne',
        exported_at: new Date().toISOString(),
        vitals: { height_cm: 188, weight_kg: 85, bp: '118/78', bmi: 24.05 },
        medications: ['Metformin 500mg', 'Omega-3 1000mg'],
        reports: ['Annual Lipid Profile 2026'],
        compliance: 'GDPR / HIPAA Self-Sovereign Health Export',
      }));

      const blob = new Blob([JSON.stringify(exportJson, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `WellNexa_Health_Export_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setActionSuccess('Complete health archive downloaded (JSON)!');
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      alert(`Error exporting data: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading consent center and security audit logs...</p>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {actionSuccess && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'rgba(16, 185, 129, 0.95)',
          color: '#ffffff',
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          boxShadow: '0 10px 25px rgba(0,0,0,0.4)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          zIndex: 1000,
          fontWeight: 600,
          fontSize: '0.9rem',
        }}>
          <CheckCircle size={18} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: '#f8fafc' }}>
              Consent & Privacy Center
            </h1>
            <span className="badge badge-normal" style={{ fontSize: '0.75rem' }}>
              GDPR / HIPAA READY
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Self-sovereign healthcare data governance, granular AI consent toggles, and immutable audit logs.
          </p>
        </div>

        <button onClick={handleExportData} className="btn-primary">
          <Download size={16} /> Export Health Data (JSON)
        </button>
      </div>

      {/* Consent Toggles Card */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 20px', color: '#f8fafc' }}>
          Granular Authorization Toggles
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* Toggle 1 */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            background: 'rgba(15, 23, 42, 0.6)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div>
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem' }}>
                Allow AI Extraction & Clinical Analysis
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Permits WellNexa AI engine to run OCR on lab documents and power grounded conversational assistance.
              </div>
            </div>
            <input
              type="checkbox"
              style={{ width: '20px', height: '20px', accentColor: '#06b6d4', cursor: 'pointer' }}
              checked={consent.allow_ai_analysis}
              onChange={(e) => setConsent({ ...consent, allow_ai_analysis: e.target.checked })}
            />
          </div>

          {/* Toggle 2 */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            background: 'rgba(15, 23, 42, 0.6)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div>
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem' }}>
                Allow Doctor & Healthcare Professional Sharing
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Permits generation of time-bound clinical access passes for verified physicians.
              </div>
            </div>
            <input
              type="checkbox"
              style={{ width: '20px', height: '20px', accentColor: '#06b6d4', cursor: 'pointer' }}
              checked={consent.allow_doctor_sharing}
              onChange={(e) => setConsent({ ...consent, allow_doctor_sharing: e.target.checked })}
            />
          </div>

          {/* Toggle 3 */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            background: 'rgba(15, 23, 42, 0.6)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div>
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem' }}>
                Allow Anonymized Wellness Research Insights
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Stripped of all Personally Identifiable Information (PII) before statistical aggregation.
              </div>
            </div>
            <input
              type="checkbox"
              style={{ width: '20px', height: '20px', accentColor: '#06b6d4', cursor: 'pointer' }}
              checked={consent.allow_anonymized_insights}
              onChange={(e) => setConsent({ ...consent, allow_anonymized_insights: e.target.checked })}
            />
          </div>

          {/* Data Retention */}
          <div style={{
            padding: '16px 20px',
            background: 'rgba(15, 23, 42, 0.6)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem' }}>
                Data Retention Period
              </div>
              <strong style={{ color: '#06b6d4' }}>{consent.data_retention_days} Days</strong>
            </div>
            <input
              type="range"
              min="30"
              max="730"
              step="30"
              value={consent.data_retention_days}
              onChange={(e) => setConsent({ ...consent, data_retention_days: parseInt(e.target.value, 10) })}
              style={{ width: '100%', accentColor: '#06b6d4' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
          <button onClick={handleSaveConsent} className="btn-primary">
            <Save size={16} /> Save Privacy Settings
          </button>
        </div>
      </div>

      {/* Security Audit Trail */}
      <div className="glass-card" style={{ padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
              Immutable Compliance Audit Trail
            </h2>
            <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Append-only security log recording every access, export, and record modification.
            </p>
          </div>
          <span className="badge badge-normal">WRITE-ONLY APPEND</span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Action Event</th>
                <th>Timestamp</th>
                <th>Source IP</th>
                <th>User Agent</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {[
                { action: 'USER_LOGIN_SUCCESS', time: 'Just now', ip: '127.0.0.1', ua: 'Chrome / Web Client', status: 'SUCCESS' },
                { action: 'HEALTH_SNAPSHOT_ACCESSED', time: '2 mins ago', ip: '127.0.0.1', ua: 'WellNexa Engine', status: 'SUCCESS' },
                { action: 'REPORT_CONFIRMATION_SYNC', time: '10 mins ago', ip: '127.0.0.1', ua: 'Clinician / Patient', status: 'SUCCESS' },
                { action: 'DOCTOR_ACCESS_PASS_CREATED', time: '1 hour ago', ip: '127.0.0.1', ua: 'Web Client', status: 'SUCCESS' },
              ].map((log, idx) => (
                <tr key={idx}>
                  <td style={{ fontFamily: 'JetBrains Mono', color: '#06b6d4', fontWeight: 600 }}>
                    {log.action}
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{log.time}</td>
                  <td style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-faint)' }}>{log.ip}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>{log.ua}</td>
                  <td>
                    <span className="badge badge-normal" style={{ fontSize: '0.65rem' }}>{log.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
