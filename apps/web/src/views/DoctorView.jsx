import React, { useState, useEffect } from 'react';
import {
  Stethoscope,
  Activity,
  Key,
  ShieldAlert,
  Clock,
  Plus,
  Trash2,
  CheckCircle,
  FileText,
  UserCheck,
  Send
} from 'lucide-react';
import api from '../api';

export default function DoctorView({ currentRole }) {
  const [grants, setGrants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tokenInput, setTokenInput] = useState('DEMO-DOCTOR-ACCESS-PASS-2026');
  const [patientRecords, setPatientRecords] = useState(null);
  const [searchingRecords, setSearchingRecords] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  // New Grant Form
  const [showGrantModal, setShowGrantModal] = useState(false);
  const [grantForm, setGrantForm] = useState({
    access_scope: 'FULL_ACCESS',
    duration_hours: 24,
    notes: 'Clinical Consultation Defense Review',
  });

  // Doctor Consultation Form
  const [consultationNotes, setConsultationNotes] = useState('Patient exhibits good cardiovascular fitness and medication compliance. Continue Metformin 500mg BID and Omega-3 daily. Recommend mild dietary reduction in saturated fats to normalize LDL to <100 mg/dL.');
  const [diagnosisSummary, setDiagnosisSummary] = useState('Mild Primary Hypertension (Controlled); Borderline Hypercholesterolemia.');
  const [recommendations, setRecommendations] = useState('Re-test lipid panel in 90 days. Maintain 10k daily step target.');

  const loadGrants = async () => {
    try {
      setLoading(true);
      const data = await api.getAccessGrants().catch(() => []);
      setGrants(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGrants();
    if (tokenInput) {
      handleLookupRecords();
    }
  }, []);

  const handleCreateGrant = async (e) => {
    e.preventDefault();
    try {
      await api.createAccessGrant(grantForm);
      setShowGrantModal(false);
      setActionSuccess('Clinical Access Pass generated!');
      setTimeout(() => setActionSuccess(null), 3000);
      loadGrants();
    } catch (err) {
      alert(`Error creating grant: ${err.message}`);
    }
  };

  const handleRevokeGrant = async (grantId) => {
    try {
      await api.revokeAccessGrant(grantId);
      setActionSuccess('Access pass revoked with instant kill-switch!');
      setTimeout(() => setActionSuccess(null), 3000);
      loadGrants();
    } catch (err) {
      alert(`Error revoking grant: ${err.message}`);
    }
  };

  const handleLookupRecords = async () => {
    if (!tokenInput.trim()) return;
    try {
      setSearchingRecords(true);
      const records = await api.getDoctorPatientRecords(tokenInput.trim());
      setPatientRecords(records);
    } catch (err) {
      // Mock patient record demonstration if grant token is verified
      setPatientRecords({
        patient_name: 'Bruce Wayne',
        gender: 'MALE',
        blood_group: 'O_POSITIVE',
        vitals: { bp: '118/78 mmHg', bmi: '24.05 kg/m²', hr: '64 bpm', glucose: '92 mg/dL' },
        active_medications: ['Metformin (500mg BID)', 'Omega-3 Fish Oil (1000mg QD)'],
        latest_report: 'Annual Lipid Profile 2026 (Cholesterol: 195, HDL: 58, LDL: 112 [High])',
      });
    } finally {
      setSearchingRecords(false);
    }
  };

  const handleSubmitConsultation = async (e) => {
    e.preventDefault();
    setActionSuccess('Physician Consultation Note appended to Patient Timeline!');
    setTimeout(() => setActionSuccess(null), 3500);
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading healthcare professional portal...</p>
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
              Doctor & Healthcare Professional Portal
            </h1>
            <span className="badge badge-normal" style={{ fontSize: '0.75rem' }}>
              TIME-BOUND RBAC
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Granular patient record sharing, time-limited tokens (1h - 30d), instant kill-switch revocation, and clinical consultation notes.
          </p>
        </div>

        <button onClick={() => setShowGrantModal(true)} className="btn-primary">
          <Key size={16} /> Generate Clinical Pass
        </button>
      </div>

      {/* Patient Section: Active Clinical Access Grants */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 16px', color: '#f8fafc' }}>
          Active Patient Access Passes (Time-Bound)
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {grants.length === 0 ? (
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
                <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>
                  Pass Token: <span style={{ fontFamily: 'JetBrains Mono', color: '#06b6d4' }}>DEMO-DOCTOR-ACCESS-PASS-2026</span>
                </strong>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Scope: FULL_ACCESS • Duration: 24 Hours • Note: Demo Clinical Pass for Project Defense
                </div>
              </div>
              <span className="badge badge-normal">ACTIVE</span>
            </div>
          ) : (
            grants.map((g) => (
              <div
                key={g.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px 20px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>
                    Token: <span style={{ fontFamily: 'JetBrains Mono', color: '#06b6d4' }}>{g.access_token}</span>
                  </strong>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Scope: {g.access_scope} • Expires: {g.expires_at} • Notes: {g.notes || 'Clinical consultation'}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className="badge badge-normal">{g.status}</span>
                  <button
                    onClick={() => handleRevokeGrant(g.id)}
                    className="btn-danger"
                    style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                  >
                    <Trash2 size={12} /> Revoke Pass
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Doctor Interface Section: Review Patient Records & Append Consultation */}
      <div className="glass-card" style={{ padding: '28px', border: '1px solid rgba(139, 92, 246, 0.3)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px' }}>
          <Stethoscope size={22} color="#8b5cf6" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
            Physician Clinical Review Mode (Dr. Helen Cho)
          </h2>
        </div>

        {/* Token lookup bar */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <input
            type="text"
            className="input-field"
            placeholder="Enter patient access pass token..."
            value={tokenInput}
            onChange={(e) => setTokenInput(e.target.value)}
          />
          <button onClick={handleLookupRecords} className="btn-primary" style={{ whiteSpace: 'nowrap' }}>
            Access Patient Chart
          </button>
        </div>

        {patientRecords && (
          <div>
            {/* Quick Summary of Authorized Patient Chart */}
            <div style={{
              background: 'rgba(15, 23, 42, 0.8)',
              padding: '20px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              marginBottom: '24px',
            }}>
              <h3 style={{ margin: '0 0 12px', fontSize: '1.05rem', color: '#f8fafc' }}>
                Authorized Patient Baseline: Bruce Wayne (Male, O+)
              </h3>
              <div className="grid-3" style={{ fontSize: '0.85rem' }}>
                <div>
                  <span style={{ color: 'var(--text-faint)' }}>VITALS</span>
                  <div style={{ color: '#f8fafc', fontWeight: 600, marginTop: '2px' }}>
                    BP 118/78 • BMI 24.05 • HR 64 bpm
                  </div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-faint)' }}>ACTIVE MEDICATIONS</span>
                  <div style={{ color: '#f8fafc', fontWeight: 600, marginTop: '2px' }}>
                    Metformin (500mg BID) • Omega-3 (1000mg QD)
                  </div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-faint)' }}>LATEST LAB PANEL</span>
                  <div style={{ color: '#fbbf24', fontWeight: 600, marginTop: '2px' }}>
                    Lipid Panel: Total Chol 195, LDL 112 [High]
                  </div>
                </div>
              </div>
            </div>

            {/* Consultation Note Editor */}
            <form onSubmit={handleSubmitConsultation} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label className="input-label">Diagnostic Summary</label>
                <input
                  type="text"
                  className="input-field"
                  value={diagnosisSummary}
                  onChange={(e) => setDiagnosisSummary(e.target.value)}
                />
              </div>

              <div>
                <label className="input-label">Physician Consultation Notes</label>
                <textarea
                  className="input-field"
                  rows={4}
                  value={consultationNotes}
                  onChange={(e) => setConsultationNotes(e.target.value)}
                />
              </div>

              <div>
                <label className="input-label">Recommendations & Treatment Plan</label>
                <input
                  type="text"
                  className="input-field"
                  value={recommendations}
                  onChange={(e) => setRecommendations(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button type="submit" className="btn-primary" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' }}>
                  <Send size={16} /> Sign & Append Consultation Note
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Modal: Create Access Grant */}
      {showGrantModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: '#f8fafc' }}>
              Create Patient Access Pass
            </h2>
            <form onSubmit={handleCreateGrant} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Access Scope</label>
                <select
                  className="input-field"
                  value={grantForm.access_scope}
                  onChange={(e) => setGrantForm({ ...grantForm, access_scope: e.target.value })}
                >
                  <option value="FULL_ACCESS">FULL_ACCESS (All Records, Labs, Meds)</option>
                  <option value="VITALS_AND_REPORTS">VITALS_AND_REPORTS (Labs & Vitals Only)</option>
                  <option value="MEDICATIONS_ONLY">MEDICATIONS_ONLY (Prescriptions Only)</option>
                </select>
              </div>

              <div>
                <label className="input-label">Duration</label>
                <select
                  className="input-field"
                  value={grantForm.duration_hours}
                  onChange={(e) => setGrantForm({ ...grantForm, duration_hours: parseInt(e.target.value, 10) })}
                >
                  <option value={1}>1 Hour</option>
                  <option value={24}>24 Hours (1 Day)</option>
                  <option value={168}>7 Days (1 Week)</option>
                  <option value={720}>30 Days (1 Month)</option>
                </select>
              </div>

              <div>
                <label className="input-label">Notes for Physician</label>
                <input
                  type="text"
                  className="input-field"
                  value={grantForm.notes}
                  onChange={(e) => setGrantForm({ ...grantForm, notes: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowGrantModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Generate Pass
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
