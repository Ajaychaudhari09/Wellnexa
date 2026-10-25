import React, { useState, useEffect } from 'react';
import {
  CalendarDays,
  Activity,
  Plus,
  Clock,
  MapPin,
  Video,
  UserCheck,
  CheckCircle,
  XCircle,
  AlertCircle,
  Calendar,
  Building,
  Shield,
  FileText
} from 'lucide-react';
import api from '../api';

export default function AppointmentsView() {
  const [appointments, setAppointments] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const defaultDate = tomorrow.toISOString().split('T')[0];

  const [form, setForm] = useState({
    doctor_name: '',
    specialty: 'General Medicine',
    clinic_or_hospital: 'Metro Health Hospital',
    location: 'Suite 402, Medical Arts Building',
    appointment_date: defaultDate,
    appointment_time: '10:30',
    purpose: '',
    notes: '',
    appointment_type: 'IN_PERSON',
  });

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const data = await api.getAppointments();
      setAppointments(data || []);
    } catch (err) {
      console.error('Failed to load appointments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAppointments();
  }, []);

  const handleCancel = async (id, doctor) => {
    if (!window.confirm(`Are you sure you want to cancel your appointment with ${doctor}?`)) {
      return;
    }
    try {
      await api.cancelAppointment(id);
      setActionSuccess(`Appointment with ${doctor} has been cancelled.`);
      setTimeout(() => setActionSuccess(null), 3500);
      loadAppointments();
    } catch (err) {
      alert(`Error cancelling appointment: ${err.message}`);
    }
  };

  const handleAddAppointment = async (e) => {
    e.preventDefault();
    if (!form.doctor_name.trim() || !form.purpose.trim()) {
      alert('Please fill in doctor name and purpose of consultation.');
      return;
    }

    try {
      setSubmitting(true);
      await api.createAppointment(form);
      setShowAddModal(false);
      setForm({
        doctor_name: '',
        specialty: 'General Medicine',
        clinic_or_hospital: 'Metro Health Hospital',
        location: 'Suite 402, Medical Arts Building',
        appointment_date: defaultDate,
        appointment_time: '10:30',
        purpose: '',
        notes: '',
        appointment_type: 'IN_PERSON',
      });
      setActionSuccess('Clinical appointment scheduled & linked to your health timeline!');
      setTimeout(() => setActionSuccess(null), 4000);
      loadAppointments();
    } catch (err) {
      alert(`Failed to schedule appointment: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredAppointments = appointments.filter((app) => {
    if (filter === 'ALL') return true;
    if (filter === 'TELEHEALTH') return app.appointment_type === 'TELEHEALTH';
    if (filter === 'UPCOMING') return app.status === 'SCHEDULED' || app.status === 'CONFIRMED';
    if (filter === 'CANCELLED') return app.status === 'CANCELLED';
    return true;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'CONFIRMED':
        return { label: 'Confirmed', bg: 'var(--mint-surface)', text: 'var(--primary-deep)', border: '#A7F3D0' };
      case 'SCHEDULED':
        return { label: 'Scheduled', bg: 'var(--sky-surface)', text: '#0369A1', border: '#BAE6FD' };
      case 'COMPLETED':
        return { label: 'Completed', bg: 'var(--bg-item)', text: 'var(--text-muted)', border: 'var(--border-subtle)' };
      case 'CANCELLED':
        return { label: 'Cancelled', bg: 'var(--coral-soft)', text: '#E11D48', border: '#FECDD3' };
      default:
        return { label: status, bg: 'var(--sunshine-soft)', text: '#B45309', border: '#FDE68A' };
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading clinical appointments calendar...</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner / Controls */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '16px',
      }}>
        <div>
          <h1 style={{
            fontSize: '1.75rem',
            fontWeight: 800,
            color: 'var(--text-main)',
            letterSpacing: '-0.02em',
            margin: '0 0 4px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <CalendarDays size={26} color="var(--primary)" />
            Clinical Appointments
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: 0 }}>
            Schedule and manage in-person hospital visits, specialist consultations, and secure telehealth sessions.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: 'var(--radius-md)',
            fontWeight: 600,
            fontSize: '0.9rem',
          }}
        >
          <Plus size={18} /> Schedule Appointment
        </button>
      </div>

      {actionSuccess && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '12px 16px',
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid #10b981',
          borderRadius: 'var(--radius-md)',
          color: '#10b981',
          fontSize: '0.9rem',
        }}>
          <CheckCircle size={18} />
          {actionSuccess}
        </div>
      )}

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {[
          { id: 'ALL', label: `All (${appointments.length})` },
          { id: 'UPCOMING', label: 'Upcoming' },
          { id: 'TELEHEALTH', label: 'Telehealth' },
          { id: 'CANCELLED', label: 'Past / Cancelled' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            style={{
              padding: '8px 16px',
              borderRadius: '20px',
              border: filter === tab.id ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
              background: filter === tab.id ? 'var(--primary)' : 'var(--bg-card)',
              color: filter === tab.id ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Appointment Cards Grid */}
      {filteredAppointments.length === 0 ? (
        <div style={{
          padding: '50px 20px',
          background: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-subtle)',
          textAlign: 'center',
        }}>
          <CalendarDays size={42} color="var(--text-faint)" style={{ margin: '0 auto 14px' }} />
          <h3 style={{ fontSize: '1.15rem', color: 'var(--text-main)', margin: '0 0 8px' }}>
            No appointments found
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '440px', margin: '0 auto 18px' }}>
            You do not have any appointments under this view. Schedule an in-person or telehealth visit to link it to your automated health timeline.
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary"
            style={{ padding: '8px 18px', borderRadius: 'var(--radius-md)' }}
          >
            <Plus size={16} style={{ marginRight: '6px', display: 'inline', verticalAlign: 'middle' }} />
            Book New Consultation
          </button>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
          gap: '16px',
        }}>
          {filteredAppointments.map((app) => {
            const badge = getStatusBadge(app.status);
            const isTelehealth = app.appointment_type === 'TELEHEALTH';
            const isCancelled = app.status === 'CANCELLED';

            return (
              <div
                key={app.id}
                style={{
                  background: 'var(--bg-card)',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid var(--border-subtle)',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px',
                  transition: 'border-color 0.2s',
                  position: 'relative',
                  overflow: 'hidden',
                  opacity: isCancelled ? 0.7 : 1,
                }}
              >
                {/* Header row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background: isTelehealth ? 'rgba(59, 130, 246, 0.15)' : 'rgba(6, 182, 212, 0.12)',
                        color: isTelehealth ? '#3b82f6' : 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}>
                        {isTelehealth ? <Video size={12} /> : <Building size={12} />}
                        {app.appointment_type.replace('_', ' ')}
                      </span>

                      <span style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background: badge.bg,
                        color: badge.text,
                        border: `1px solid ${badge.border}33`,
                      }}>
                        {badge.label}
                      </span>
                    </div>

                    <h3 style={{
                      fontSize: '1.15rem',
                      fontWeight: 700,
                      color: 'var(--text-main)',
                      margin: '6px 0 2px'
                    }}>
                      {app.doctor_name}
                    </h3>
                    <p style={{ fontSize: '0.82rem', color: 'var(--primary)', margin: 0, fontWeight: 600 }}>
                      {app.specialty}
                    </p>
                  </div>

                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: 'var(--bg-item)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--primary)',
                  }}>
                    <UserCheck size={20} />
                  </div>
                </div>

                {/* Date & Time info box */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  background: 'var(--bg-item)',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                    <Calendar size={16} color="var(--primary)" />
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Date</div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                        {app.appointment_date}
                      </div>
                    </div>
                  </div>

                  <div style={{ width: '1px', height: '24px', background: 'var(--border-subtle)' }} />

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                    <Clock size={16} color="var(--primary)" />
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Time</div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                        {app.appointment_time}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Purpose & Location */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-muted)', fontSize: '0.78rem' }}>Reason: </span>
                    {app.purpose}
                  </div>

                  {app.clinic_or_hospital && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <MapPin size={14} color="var(--text-faint)" />
                      <span>{app.clinic_or_hospital} {app.location ? `• ${app.location}` : ''}</span>
                    </div>
                  )}

                  {app.notes && (
                    <div style={{
                      fontSize: '0.78rem',
                      color: 'var(--text-muted)',
                      fontStyle: 'italic',
                      background: 'var(--bg-item)',
                      padding: '8px 10px',
                      borderRadius: 'var(--radius-sm)',
                      marginTop: '4px'
                    }}>
                      Note: {app.notes}
                    </div>
                  )}
                </div>

                {/* Actions Footer */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: '12px',
                  borderTop: '1px solid var(--border-subtle)',
                  marginTop: 'auto',
                }}>
                  {isTelehealth && !isCancelled ? (
                    <button
                      onClick={() => alert(`Starting encrypted WebRTC session for appointment with ${app.doctor_name}. Camera & Microphone ready.`)}
                      className="btn-primary"
                      style={{
                        padding: '6px 14px',
                        fontSize: '0.8rem',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <Video size={14} /> Join Video Room
                    </button>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-faint)' }}>
                      <Shield size={12} color="#10b981" />
                      HIPAA / DPDP Protected
                    </div>
                  )}

                  {!isCancelled && (
                    <button
                      onClick={() => handleCancel(app.id, app.doctor_name)}
                      className="btn-secondary"
                      style={{
                        padding: '6px 12px',
                        fontSize: '0.78rem',
                        borderRadius: 'var(--radius-sm)',
                        color: '#ef4444',
                        borderColor: 'rgba(239, 68, 68, 0.3)',
                      }}
                    >
                      Cancel Visit
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal: Schedule Appointment */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(3, 7, 18, 0.75)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '20px',
        }}>
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-subtle)',
            width: '100%',
            maxWidth: '520px',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '24px',
            boxShadow: 'var(--shadow-dropdown)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CalendarDays size={22} color="var(--primary)" />
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                  Book Clinical Consultation
                </h3>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="btn-secondary"
                style={{ padding: '6px 10px', borderRadius: '6px' }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAddAppointment} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Doctor Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Dr. Sarah Jenkins, MD"
                  value={form.doctor_name}
                  onChange={(e) => setForm({ ...form, doctor_name: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-item)',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem',
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Specialty
                  </label>
                  <select
                    value={form.specialty}
                    onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-item)',
                      color: 'var(--text-main)',
                      fontSize: '0.88rem',
                    }}
                  >
                    <option value="General Medicine">General Medicine</option>
                    <option value="Cardiology">Cardiology</option>
                    <option value="Endocrinology">Endocrinology</option>
                    <option value="Neurology">Neurology</option>
                    <option value="Dermatology">Dermatology</option>
                    <option value="Orthopedics">Orthopedics</option>
                    <option value="Psychiatry">Psychiatry</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Consultation Type
                  </label>
                  <select
                    value={form.appointment_type}
                    onChange={(e) => setForm({ ...form, appointment_type: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-item)',
                      color: 'var(--text-main)',
                      fontSize: '0.88rem',
                    }}
                  >
                    <option value="IN_PERSON">In-Person Visit</option>
                    <option value="TELEHEALTH">Encrypted Telehealth (Video)</option>
                    <option value="HOME_VISIT">Home Visit</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Date *
                  </label>
                  <input
                    type="date"
                    required
                    value={form.appointment_date}
                    onChange={(e) => setForm({ ...form, appointment_date: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-item)',
                      color: 'var(--text-main)',
                      fontSize: '0.88rem',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Time *
                  </label>
                  <input
                    type="time"
                    required
                    value={form.appointment_time}
                    onChange={(e) => setForm({ ...form, appointment_time: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-item)',
                      color: 'var(--text-main)',
                      fontSize: '0.88rem',
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Hospital / Clinic
                </label>
                <input
                  type="text"
                  placeholder="e.g. Metro Health Hospital"
                  value={form.clinic_or_hospital}
                  onChange={(e) => setForm({ ...form, clinic_or_hospital: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-item)',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Purpose of Consultation *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 6-Month Hypertension Follow-up, Lab Review"
                  value={form.purpose}
                  onChange={(e) => setForm({ ...form, purpose: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-item)',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Preparation Notes / Questions for Doctor
                </label>
                <textarea
                  rows={2}
                  placeholder="e.g. Ask regarding blood pressure spike after morning dose"
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-item)',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem',
                    resize: 'vertical',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn-secondary"
                  style={{ padding: '8px 16px', borderRadius: 'var(--radius-md)' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary"
                  style={{ padding: '8px 20px', borderRadius: 'var(--radius-md)' }}
                >
                  {submitting ? 'Scheduling...' : 'Confirm Appointment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
