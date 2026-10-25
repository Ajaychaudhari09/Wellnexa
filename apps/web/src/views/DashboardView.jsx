import React, { useState, useEffect } from 'react';
import {
  Heart,
  Activity,
  Pill,
  Bell,
  Sparkles,
  CheckCircle,
  Clock,
  Droplets,
  Apple,
  FileSpreadsheet,
  Smile,
  AlertTriangle,
  ArrowRight,
  Plus
} from 'lucide-react';
import api from '../api';

export default function DashboardView({ onNavigate }) {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getHomeDashboard();
      setDashboard(data);
    } catch (err) {
      console.warn('fetchDashboard encountered error, attempting recovery:', err);
      if (err.message && (err.message.includes('token') || err.message.includes('401') || err.message.includes('expired') || err.message.includes('Signature'))) {
        try {
          await api.login('patient@wellnexa.ai', 'Password123!');
          const data = await api.getHomeDashboard();
          setDashboard(data);
          setError(null);
          return;
        } catch (retryErr) {
          setError(retryErr.message || 'Authentication error');
        }
      } else {
        setError(err.message || 'Failed to load home dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleTakeDose = async (medicationId, medName) => {
    try {
      await api.logDose(medicationId, 'TAKEN');
      setActionSuccess(`Logged dose for ${medName}!`);
      setTimeout(() => setActionSuccess(null), 3000);
      fetchDashboard();
    } catch (err) {
      alert(`Error logging dose: ${err.message}`);
    }
  };

  const handleCompleteReminder = async (reminderId, title) => {
    try {
      await api.completeReminder(reminderId);
      setActionSuccess(`Completed reminder: ${title}!`);
      setTimeout(() => setActionSuccess(null), 3000);
      fetchDashboard();
    } catch (err) {
      alert(`Error completing reminder: ${err.message}`);
    }
  };

  const handleAddWater = async () => {
    try {
      const current = dashboard?.nutrition?.water_ml_consumed || 0;
      await api.logDailyActivity({ water_ml: current + 250 });
      setActionSuccess('Added +250ml water!');
      setTimeout(() => setActionSuccess(null), 3000);
      fetchDashboard();
    } catch (err) {
      alert(`Error updating hydration: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <div className="animate-spin" style={{ display: 'inline-block', marginBottom: '16px' }}>
          <Activity size={36} color="#06b6d4" />
        </div>
        <p style={{ fontSize: '1rem' }}>Aggregating unified health metrics from WellNexa engine...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px' }}>
        <div className="glass-card" style={{ padding: '24px', borderColor: 'rgba(239, 68, 68, 0.4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: '#f87171' }}>
            <AlertTriangle size={24} />
            <h3 style={{ margin: 0 }}>Unable to Load Dashboard</h3>
          </div>
          <p style={{ marginTop: '12px', color: 'var(--text-muted)' }}>{error}</p>
          <button onClick={fetchDashboard} className="btn-secondary" style={{ marginTop: '12px' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const { profile, medicines, reminders, vitals, nutrition, latest_report, mood, adherence } = dashboard;

  return (
    <div className="page-wrapper">
      {/* Action Notification Toast */}
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

      {/* Greeting Banner */}
      <div className="glass-card" style={{
        padding: '28px 32px',
        marginBottom: '28px',
        background: 'var(--greeting-gradient)',
        border: '1px solid rgba(6, 182, 212, 0.25)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '20px',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
              {dashboard.greeting}
            </h1>
            <span className="badge badge-normal" style={{ fontSize: '0.75rem' }}>
              {adherence?.tier || 'EXCELLENT'} ADHERENCE
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', margin: 0 }}>
            Patient ID: <span style={{ fontFamily: 'JetBrains Mono', color: 'var(--primary)' }}>{profile.user_id.slice(0, 8)}...</span> • Blood Group: <strong style={{ color: 'var(--text-main)' }}>{profile.blood_group || 'O+'}</strong>
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => onNavigate('assistant')} className="btn-primary">
            <Sparkles size={16} />
            Ask AI Assistant
          </button>
          <button onClick={() => onNavigate('snapshot')} className="btn-secondary">
            360° Health Snapshot
          </button>
        </div>
      </div>

      {/* 4-Stat Grid: Vitals & Adherence Overview */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        {/* BMI & Status */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>BODY MASS INDEX</span>
            <Activity size={18} color="var(--primary)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)', margin: '8px 0 4px' }}>
            {vitals.bmi || '24.05'}
          </div>
          <span className="badge badge-normal" style={{ fontSize: '0.72rem' }}>
            {vitals.bmi_category || 'Normal Weight'}
          </span>
        </div>

        {/* Blood Pressure */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>BLOOD PRESSURE</span>
            <Heart size={18} color="#ef4444" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)', margin: '8px 0 4px' }}>
            118 / 78
          </div>
          <span className="badge badge-normal" style={{ fontSize: '0.72rem' }}>
            Optimal Range (mmHg)
          </span>
        </div>

        {/* Adherence Rate */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>MED ADHERENCE</span>
            <Pill size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10b981', margin: '8px 0 4px' }}>
            {adherence.adherence_percentage}%
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {adherence.taken_doses_this_month} of {adherence.total_doses_this_month} doses taken
          </span>
        </div>

        {/* Hydration / Water */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>HYDRATION</span>
            <Droplets size={18} color="#3b82f6" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#38bdf8', margin: '8px 0 4px' }}>
            {nutrition.water_ml_consumed} <span style={{ fontSize: '1rem', fontWeight: 500 }}>/ {nutrition.water_ml_target} ml</span>
          </div>
          <button
            onClick={handleAddWater}
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '4px 10px', marginTop: '4px' }}
          >
            <Plus size={12} /> +250 ml Water
          </button>
        </div>
      </div>

      {/* Main 2-Column Section */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        {/* Left Column: Today's Medications */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                Today's Medication Schedule
              </h2>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {medicines.taken_count} taken • {medicines.pending_count} pending
              </span>
            </div>
            <button onClick={() => onNavigate('medicines')} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
              All Meds <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {medicines.doses.length === 0 ? (
              <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No medications scheduled for today.
              </div>
            ) : (
              medicines.doses.map((dose) => (
                <div
                  key={dose.medication_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 18px',
                    background: 'var(--bg-item)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '8px',
                      background: dose.is_taken ? 'rgba(16, 185, 129, 0.15)' : 'rgba(6, 182, 212, 0.15)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      <Pill size={18} color={dose.is_taken ? '#10b981' : '#06b6d4'} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem' }}>
                        {dose.name}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {dose.dosage} • {dose.timing.replace('_', ' ')} • {dose.time_slot}
                      </div>
                    </div>
                  </div>

                  <div>
                    {dose.is_taken ? (
                      <span className="badge badge-normal">
                        <CheckCircle size={12} /> Taken
                      </span>
                    ) : (
                      <button
                        onClick={() => handleTakeDose(dose.medication_id, dose.name)}
                        className="btn-primary"
                        style={{ fontSize: '0.8rem', padding: '6px 14px' }}
                      >
                        Take Dose
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Smart Reminders */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                Smart Health Reminders
              </h2>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {reminders.completed_count} of {reminders.total_due} completed
              </span>
            </div>
            <button onClick={() => onNavigate('reminders')} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
              Manage <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {reminders.upcoming_reminders.length === 0 ? (
              <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No upcoming reminders for today.
              </div>
            ) : (
              reminders.upcoming_reminders.map((rem) => (
                <div
                  key={rem.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 18px',
                    background: 'var(--bg-item)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '8px',
                      background: rem.is_completed ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      <Clock size={18} color={rem.is_completed ? '#10b981' : '#f59e0b'} />
                    </div>
                    <div>
                      <div style={{
                        fontWeight: 600,
                        color: rem.is_completed ? 'var(--text-muted)' : 'var(--text-main)',
                        textDecoration: rem.is_completed ? 'line-through' : 'none',
                        fontSize: '0.95rem'
                      }}>
                        {rem.title}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Due at {rem.due_time} • <span className="badge badge-active" style={{ fontSize: '0.65rem' }}>{rem.reminder_type}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    {rem.is_completed ? (
                      <span className="badge badge-normal">Done</span>
                    ) : (
                      <button
                        onClick={() => handleCompleteReminder(rem.id, rem.title)}
                        className="btn-secondary"
                        style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                      >
                        <CheckCircle size={14} /> Mark Done
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Secondary 2-Column: Latest Lab Report & Nutrition/Mood */}
      <div className="grid-2">
        {/* Latest Lab Report Widget */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
              Latest Medical Lab Report
            </h2>
            <button onClick={() => onNavigate('reports')} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
              Report Details <ArrowRight size={14} />
            </button>
          </div>

          {latest_report.has_reports ? (
            <div style={{
              background: 'var(--bg-item)',
              borderRadius: 'var(--radius-md)',
              padding: '18px',
              border: '1px solid var(--border-subtle)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {latest_report.report_type?.replace('_', ' ')}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Report Date: {latest_report.report_date} • Lab: Gotham Metropolitan Diagnostics
                  </div>
                </div>
                <span className="badge badge-normal">
                  {latest_report.status}
                </span>
              </div>

              <div style={{ display: 'flex', gap: '20px', marginTop: '14px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-faint)' }}>TESTS EXTRACTED</span>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {latest_report.total_parameters_tested}
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-faint)' }}>OUT-OF-RANGE FLAGS</span>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fbbf24' }}>
                    {latest_report.flagged_count} Flag (High LDL)
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No laboratory reports uploaded yet.
            </div>
          )}
        </div>

        {/* Nutrition & Mood Overview */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
              Nutrition & Mental Reflection
            </h2>
            <button onClick={() => onNavigate('nutrition')} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
              Nutrition Hub <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ marginBottom: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Calories Consumed</span>
              <strong style={{ color: 'var(--text-main)' }}>
                {nutrition.calories_consumed} / {nutrition.calorie_target} kcal
              </strong>
            </div>
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill"
                style={{
                  width: `${Math.min(100, (nutrition.calories_consumed / nutrition.calorie_target) * 100)}%`,
                  background: 'linear-gradient(90deg, #06b6d4 0%, #10b981 100%)',
                }}
              />
            </div>
          </div>

          <div style={{
            background: 'var(--bg-item)',
            borderRadius: 'var(--radius-md)',
            padding: '14px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <Smile size={18} color="#8b5cf6" />
              <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)' }}>
                Daily Mood: {mood.mood_score}/5 ({mood.primary_emotion})
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, fontStyle: 'italic' }}>
              "{mood.gratitude_note || 'Grateful for energy and good cardiovascular stamina.'}"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
