import React, { useState, useEffect } from 'react';
import {
  User,
  Mail,
  Phone,
  Calendar,
  Shield,
  Activity,
  Heart,
  AlertCircle,
  CheckCircle,
  Save,
  LogOut,
  Lock,
  Stethoscope,
  Clock
} from 'lucide-react';
import api from '../api';

export default function ProfileView({ currentUser, currentRole, onLogout, onNavigate }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    date_of_birth: '',
    gender: 'MALE',
    blood_group: 'O_POSITIVE',
    emergency_contact_name: '',
    emergency_contact_phone: '',
  });

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await api.getProfile();
      if (data) {
        setProfile(data);
        setForm({
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          phone_number: data.phone_number || '',
          date_of_birth: data.date_of_birth || '1990-05-19',
          gender: data.gender || 'MALE',
          blood_group: data.blood_group || 'O_POSITIVE',
          emergency_contact_name: data.emergency_contact_name || '',
          emergency_contact_phone: data.emergency_contact_phone || '',
        });
      }
    } catch (err) {
      console.warn('Profile fetch fallback to current user:', err);
      if (currentUser) {
        setForm(prev => ({
          ...prev,
          first_name: currentUser.first_name || 'Bruce',
          last_name: currentUser.last_name || 'Wayne',
        }));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      setMessage(null);
      await api.updateProfile(form);
      setMessage({ type: 'success', text: 'Personal profile and health baseline updated successfully!' });
      setTimeout(() => setMessage(null), 4000);
      loadProfile();
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to update profile.' });
    } finally {
      setSaving(false);
    }
  };

  const displayName = `${form.first_name || currentUser?.first_name || 'Health'} ${form.last_name || currentUser?.last_name || 'User'}`;
  const displayEmail = currentUser?.email || (currentRole === 'DOCTOR' ? 'doctor@wellnexa.ai' : 'patient@wellnexa.ai');

  return (
    <div className="page-wrapper">
      {/* Toast Notification */}
      {message && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '14px 20px',
          borderRadius: 'var(--radius-md)',
          background: message.type === 'success' ? 'var(--mint-surface)' : 'rgba(239, 68, 68, 0.15)',
          border: `1px solid ${message.type === 'success' ? 'var(--primary)' : '#ef4444'}`,
          color: message.type === 'success' ? 'var(--primary-deep)' : '#ef4444',
          marginBottom: '20px',
          fontWeight: 600,
          fontSize: '0.9rem',
        }}>
          {message.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
            Personal Health Profile & Account
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Manage identity credentials, baseline biometrics, emergency contacts, and active authorizations.
          </p>
        </div>

        <button
          onClick={onLogout}
          className="btn-danger"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 18px', fontSize: '0.88rem' }}
        >
          <LogOut size={16} /> End Session & Sign Out
        </button>
      </div>

      {/* Profile Overview Card */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--aqua) 100%)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.75rem',
            fontWeight: 800,
            boxShadow: '0 4px 16px var(--primary-glow)',
          }}>
            {form.first_name ? form.first_name[0] : 'U'}
          </div>

          <div style={{ flex: 1, minWidth: '220px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
                {displayName}
              </h2>
              <span className="badge badge-normal" style={{ fontSize: '0.72rem' }}>
                {currentRole === 'DOCTOR' ? 'PHYSICIAN / PROVIDER' : 'VERIFIED PATIENT'}
              </span>
              <span className="badge badge-active" style={{ fontSize: '0.72rem' }}>
                ACTIVE SESSION
              </span>
            </div>
            <p style={{ margin: '4px 0 0', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              {displayEmail}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => onNavigate && onNavigate('privacy')}
              className="btn-secondary"
              style={{ fontSize: '0.82rem', padding: '8px 14px' }}
            >
              <Shield size={14} color="var(--primary)" /> Privacy & Consent
            </button>
          </div>
        </div>
      </div>

      {/* Main Form: Profile Details */}
      <div className="glass-card" style={{ padding: '32px' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 22px', color: 'var(--text-main)' }}>
          Edit Demographic & Emergency Details
        </h3>

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="grid-2" style={{ gap: '18px' }}>
            <div>
              <label className="input-label">First Name</label>
              <input
                type="text"
                required
                className="input-field"
                value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              />
            </div>
            <div>
              <label className="input-label">Last Name</label>
              <input
                type="text"
                required
                className="input-field"
                value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              />
            </div>
          </div>

          <div className="grid-3" style={{ gap: '18px' }}>
            <div>
              <label className="input-label">Date of Birth</label>
              <input
                type="date"
                className="input-field"
                value={form.date_of_birth}
                onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
              />
            </div>
            <div>
              <label className="input-label">Gender</label>
              <select
                className="input-field"
                value={form.gender}
                onChange={(e) => setForm({ ...form, gender: e.target.value })}
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other / Non-Binary</option>
              </select>
            </div>
            <div>
              <label className="input-label">Blood Group</label>
              <select
                className="input-field"
                value={form.blood_group}
                onChange={(e) => setForm({ ...form, blood_group: e.target.value })}
              >
                <option value="O_POSITIVE">O Positive (O+)</option>
                <option value="O_NEGATIVE">O Negative (O-)</option>
                <option value="A_POSITIVE">A Positive (A+)</option>
                <option value="A_NEGATIVE">A Negative (A-)</option>
                <option value="B_POSITIVE">B Positive (B+)</option>
                <option value="B_NEGATIVE">B Negative (B-)</option>
                <option value="AB_POSITIVE">AB Positive (AB+)</option>
                <option value="AB_NEGATIVE">AB Negative (AB-)</option>
              </select>
            </div>
          </div>

          <div className="grid-2" style={{ gap: '18px' }}>
            <div>
              <label className="input-label">Emergency Contact Name</label>
              <input
                type="text"
                placeholder="e.g. Alfred Pennyworth (Guardian)"
                className="input-field"
                value={form.emergency_contact_name}
                onChange={(e) => setForm({ ...form, emergency_contact_name: e.target.value })}
              />
            </div>
            <div>
              <label className="input-label">Emergency Contact Phone</label>
              <input
                type="tel"
                placeholder="e.g. +1-555-0199"
                className="input-field"
                value={form.emergency_contact_phone}
                onChange={(e) => setForm({ ...form, emergency_contact_phone: e.target.value })}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
            <button
              type="submit"
              disabled={saving}
              className="btn-primary"
              style={{ padding: '12px 28px', fontSize: '0.95rem' }}
            >
              <Save size={16} /> {saving ? 'Saving...' : 'Save Profile Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
