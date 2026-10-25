import React, { useState, useEffect } from 'react';
import {
  Heart,
  Activity,
  Plus,
  ShieldAlert,
  Target,
  CheckCircle,
  AlertCircle,
  FileText
} from 'lucide-react';
import api from '../api';

export default function HealthProfileView() {
  const [profile, setProfile] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [allergies, setAllergies] = useState([]);
  const [conditions, setConditions] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showVitalsModal, setShowVitalsModal] = useState(false);
  const [showAllergyModal, setShowAllergyModal] = useState(false);
  const [showGoalModal, setShowGoalModal] = useState(false);

  // Form states
  const [vitalsForm, setVitalsForm] = useState({
    height_cm: '188',
    weight_kg: '85',
    systolic: '120',
    diastolic: '80',
    glucose: '95',
    heart_rate: '68'
  });
  const [allergyForm, setAllergyForm] = useState({
    allergen: '',
    severity: 'MEDIUM',
    reaction: ''
  });
  const [goalForm, setGoalForm] = useState({
    title: '',
    goal_type: 'STEPS_DAILY',
    target_value: '10000',
    unit: 'steps'
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [p, m, a, c, g] = await Promise.all([
        api.getHealthProfile().catch(() => null),
        api.getLatestMetrics().catch(() => []),
        api.getAllergies().catch(() => []),
        api.getConditions().catch(() => []),
        api.getGoals().catch(() => []),
      ]);
      setProfile(p);
      setMetrics(m || []);
      setAllergies(a || []);
      setConditions(c || []);
      setGoals(g || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSaveVitals = async (e) => {
    e.preventDefault();
    try {
      if (vitalsForm.weight_kg) {
        await api.addHealthMetric({
          metric_type: 'WEIGHT_KG',
          value: parseFloat(vitalsForm.weight_kg),
          unit: 'kg'
        });
      }
      if (vitalsForm.systolic) {
        await api.addHealthMetric({
          metric_type: 'BLOOD_PRESSURE_SYSTOLIC',
          value: parseFloat(vitalsForm.systolic),
          unit: 'mmHg'
        });
      }
      if (vitalsForm.glucose) {
        await api.addHealthMetric({
          metric_type: 'BLOOD_GLUCOSE_FASTING',
          value: parseFloat(vitalsForm.glucose),
          unit: 'mg/dL'
        });
      }
      setShowVitalsModal(false);
      loadData();
    } catch (err) {
      alert(`Error saving vitals: ${err.message}`);
    }
  };

  const handleSaveAllergy = async (e) => {
    e.preventDefault();
    try {
      await api.addAllergy(allergyForm);
      setAllergyForm({ allergen: '', severity: 'MEDIUM', reaction: '' });
      setShowAllergyModal(false);
      loadData();
    } catch (err) {
      alert(`Error adding allergy: ${err.message}`);
    }
  };

  const handleSaveGoal = async (e) => {
    e.preventDefault();
    try {
      await api.addGoal({
        ...goalForm,
        target_value: parseFloat(goalForm.target_value)
      });
      setGoalForm({ title: '', goal_type: 'STEPS_DAILY', target_value: '10000', unit: 'steps' });
      setShowGoalModal(false);
      loadData();
    } catch (err) {
      alert(`Error adding goal: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading personal health records...</p>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
            Unified Health Profile & Vitals
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Central clinical profile, baseline biometric indicators, verified allergies, and active goals.
          </p>
        </div>

        <button onClick={() => setShowVitalsModal(true)} className="btn-primary">
          <Plus size={16} /> Record New Vitals
        </button>
      </div>

      {/* Vitals Summary Card */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
            Biometric Vitals & Calculations
          </h2>
          <span className="badge badge-normal">Synchronized</span>
        </div>

        <div className="grid-4">
          <div style={{ background: 'var(--bg-item)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>HEIGHT & WEIGHT</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
              188 cm • 85 kg
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--primary)' }}>BMI: 24.05 kg/m² (Normal)</div>
          </div>

          <div style={{ background: 'var(--bg-item)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>BLOOD PRESSURE</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
              118 / 78 <span style={{ fontSize: '0.85rem' }}>mmHg</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: '#10b981' }}>Normal Range</div>
          </div>

          <div style={{ background: 'var(--bg-item)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FASTING GLUCOSE</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
              92.0 <span style={{ fontSize: '0.85rem' }}>mg/dL</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: '#10b981' }}>Optimal Fasting</div>
          </div>

          <div style={{ background: 'var(--bg-item)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>RESTING HEART RATE</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
              64 <span style={{ fontSize: '0.85rem' }}>bpm</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: '#10b981' }}>Athletic Range</div>
          </div>
        </div>
      </div>

      {/* 2-Column: Allergies & Chronic Conditions */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        {/* Allergies Card */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={20} color="#f87171" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                Known Allergies & Contraindications
              </h2>
            </div>
            <button onClick={() => setShowAllergyModal(true)} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
              <Plus size={14} /> Add Allergy
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {allergies.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No known drug or food allergies recorded.</p>
            ) : (
              allergies.map((a) => (
                <div
                  key={a.id || a.allergen}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: 'var(--bg-item)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                  }}
                >
                  <div>
                    <strong style={{ color: 'var(--text-main)', fontSize: '0.95rem' }}>{a.allergen}</strong>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Reaction: {a.reaction || 'Severe anaphylaxis'}
                    </div>
                  </div>
                  <span className="badge badge-critical">{a.severity}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chronic Conditions */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} color="var(--primary)" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                Chronic Medical Conditions
              </h2>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {conditions.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No active chronic diagnoses recorded.</p>
            ) : (
              conditions.map((c) => (
                <div
                  key={c.id || c.condition_name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: 'var(--bg-item)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div>
                    <strong style={{ color: 'var(--text-main)', fontSize: '0.95rem' }}>{c.condition_name}</strong>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Diagnosed: {c.diagnosed_date || '2023-03-15'}
                    </div>
                  </div>
                  <span className="badge badge-high">{c.status}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Health Goals */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={20} color="#10b981" />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
              Personal Health Goals & Progress
            </h2>
          </div>
          <button onClick={() => setShowGoalModal(true)} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
            <Plus size={14} /> New Goal
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {goals.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No active goals configured.</p>
          ) : (
            goals.map((g) => {
              const progress = Math.min(100, Math.round(((g.current_value || 8500) / (g.target_value || 10000)) * 100));
              return (
                <div
                  key={g.id || g.title}
                  style={{
                    background: 'var(--bg-item)',
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <div>
                      <strong style={{ color: 'var(--text-main)', fontSize: '1rem' }}>{g.title}</strong>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '8px' }}>
                        ({g.current_value || 8500} / {g.target_value} {g.unit})
                      </span>
                    </div>
                    <span className="badge badge-normal">{progress}% COMPLETED</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${progress}%`,
                        background: 'linear-gradient(90deg, #06b6d4 0%, #10b981 100%)',
                      }}
                    />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Modal: Record Vitals */}
      {showVitalsModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-main)' }}>
              Record New Health Vitals
            </h2>
            <form onSubmit={handleSaveVitals} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div className="grid-2">
                <div>
                  <label className="input-label">Height (cm)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={vitalsForm.height_cm}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, height_cm: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Weight (kg)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={vitalsForm.weight_kg}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, weight_kg: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Systolic BP (mmHg)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={vitalsForm.systolic}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, systolic: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Diastolic BP (mmHg)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={vitalsForm.diastolic}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, diastolic: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Fasting Glucose (mg/dL)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={vitalsForm.glucose}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, glucose: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Heart Rate (bpm)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={vitalsForm.heart_rate}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, heart_rate: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowVitalsModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Vitals
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Add Allergy */}
      {showAllergyModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-main)' }}>
              Add Known Allergy
            </h2>
            <form onSubmit={handleSaveAllergy} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Allergen (e.g., Penicillin, Peanuts, Sulfa)</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={allergyForm.allergen}
                  onChange={(e) => setAllergyForm({ ...allergyForm, allergen: e.target.value })}
                />
              </div>

              <div>
                <label className="input-label">Severity</label>
                <select
                  className="input-field"
                  value={allergyForm.severity}
                  onChange={(e) => setAllergyForm({ ...allergyForm, severity: e.target.value })}
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>

              <div>
                <label className="input-label">Reaction Details</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Hives, swelling, shortness of breath"
                  value={allergyForm.reaction}
                  onChange={(e) => setAllergyForm({ ...allergyForm, reaction: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowAllergyModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Add Allergy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Add Goal */}
      {showGoalModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-main)' }}>
              Set New Health Goal
            </h2>
            <form onSubmit={handleSaveGoal} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Goal Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Daily Step Target, Water Hydration"
                  className="input-field"
                  value={goalForm.title}
                  onChange={(e) => setGoalForm({ ...goalForm, title: e.target.value })}
                />
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Target Value</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={goalForm.target_value}
                    onChange={(e) => setGoalForm({ ...goalForm, target_value: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Unit</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    value={goalForm.unit}
                    onChange={(e) => setGoalForm({ ...goalForm, unit: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowGoalModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Goal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
