import React, { useState, useEffect } from 'react';
import {
  Pill,
  Activity,
  Plus,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  RotateCcw,
  Sparkles,
  Package
} from 'lucide-react';
import api from '../api';

export default function MedicinesView() {
  const [medicines, setMedicines] = useState([]);
  const [adherence, setAdherence] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  const [form, setForm] = useState({
    name: '',
    dosage: '500 mg',
    form: 'TABLET',
    frequency: 'ONCE_DAILY',
    timing: 'AFTER_MEAL',
    current_stock: '30',
    refill_threshold: '7',
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [meds, adh] = await Promise.all([
        api.getMedicines().catch(() => []),
        api.getAdherenceScore().catch(() => null),
      ]);
      setMedicines(meds || []);
      setAdherence(adh);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleLogDose = async (medId, medName, status) => {
    try {
      await api.logDose(medId, status);
      setActionSuccess(`Logged ${status.toLowerCase()} dose for ${medName}!`);
      setTimeout(() => setActionSuccess(null), 3000);
      loadData();
    } catch (err) {
      alert(`Error logging dose: ${err.message}`);
    }
  };

  const handleAddMedicine = async (e) => {
    e.preventDefault();
    try {
      await api.addMedicine({
        ...form,
        current_stock: parseInt(form.current_stock, 10),
        refill_threshold: parseInt(form.refill_threshold, 10),
      });
      setShowAddModal(false);
      setForm({
        name: '',
        dosage: '500 mg',
        form: 'TABLET',
        frequency: 'ONCE_DAILY',
        timing: 'AFTER_MEAL',
        current_stock: '30',
        refill_threshold: '7',
      });
      setActionSuccess('Added new prescription!');
      setTimeout(() => setActionSuccess(null), 3000);
      loadData();
    } catch (err) {
      alert(`Error adding medication: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading prescriptions and adherence calculations...</p>
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
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: '#f8fafc' }}>
            Prescriptions & Medicine Manager
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Inventory stock tracking, dose adherence scores, and refill warning thresholds.
          </p>
        </div>

        <button onClick={() => setShowAddModal(true)} className="btn-primary">
          <Plus size={16} /> Add Medication
        </button>
      </div>

      {/* Adherence Score Card */}
      {adherence && (
        <div className="glass-card" style={{
          padding: '24px 32px',
          marginBottom: '28px',
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.8) 100%)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '20px',
        }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700 }}>
              DYNAMIC CLINICAL ADHERENCE
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', margin: '6px 0' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#10b981' }}>
                {adherence.adherence_percentage}%
              </div>
              <span className="badge badge-normal" style={{ fontSize: '0.8rem' }}>
                {adherence.tier}
              </span>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
              {adherence.taken_doses} of {adherence.total_doses} prescribed doses verified on-time.
            </p>
          </div>

          <div style={{ maxWidth: '300px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-faint)' }}>MONTHLY COMPLETION PROGRESS</span>
            <div className="progress-bar-bg" style={{ marginTop: '8px', height: '10px' }}>
              <div
                className="progress-bar-fill"
                style={{
                  width: `${adherence.adherence_percentage}%`,
                  background: 'linear-gradient(90deg, #10b981 0%, #06b6d4 100%)',
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Medications Grid */}
      <div className="grid-3">
        {medicines.map((med) => {
          const isLowStock = med.current_stock <= med.refill_threshold;
          return (
            <div
              key={med.id}
              className="glass-card"
              style={{
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderColor: isLowStock ? 'rgba(245, 158, 11, 0.4)' : 'var(--border-subtle)',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: '10px',
                    background: 'rgba(6, 182, 212, 0.15)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <Pill size={22} color="#06b6d4" />
                  </div>
                  <span className="badge badge-active" style={{ fontSize: '0.7rem' }}>
                    {med.form}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 4px', color: '#f8fafc' }}>
                  {med.name}
                </h3>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                  {med.dosage} • {med.frequency?.replace('_', ' ')} • {med.timing?.replace('_', ' ')}
                </div>

                {/* Stock Bar */}
                <div style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '18px',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Stock Remaining</span>
                    <strong style={{ color: isLowStock ? '#fbbf24' : '#f8fafc' }}>
                      {med.current_stock} units
                    </strong>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${Math.min(100, (med.current_stock / 60) * 100)}%`,
                        background: isLowStock ? '#f59e0b' : '#06b6d4',
                      }}
                    />
                  </div>
                  {isLowStock && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fbbf24', fontSize: '0.75rem', marginTop: '6px' }}>
                      <AlertTriangle size={12} /> Refill Needed (Threshold: {med.refill_threshold})
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => handleLogDose(med.id, med.name, 'TAKEN')}
                  className="btn-primary"
                  style={{ flex: 1, fontSize: '0.82rem', padding: '8px' }}
                >
                  <CheckCircle size={14} /> Taken
                </button>
                <button
                  onClick={() => handleLogDose(med.id, med.name, 'MISSED')}
                  className="btn-secondary"
                  style={{ fontSize: '0.82rem', padding: '8px 12px' }}
                  title="Mark as Missed"
                >
                  <XCircle size={14} color="#f87171" />
                </button>
                <button
                  onClick={() => handleLogDose(med.id, med.name, 'SKIPPED')}
                  className="btn-secondary"
                  style={{ fontSize: '0.82rem', padding: '8px 12px' }}
                  title="Mark as Skipped"
                >
                  <RotateCcw size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal: Add Medication */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: '#f8fafc' }}>
              Add Prescribed Medication
            </h2>
            <form onSubmit={handleAddMedicine} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Medication Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Atorvastatin, Metformin"
                  className="input-field"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Dosage (e.g. 10mg, 500mg)</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    value={form.dosage}
                    onChange={(e) => setForm({ ...form, dosage: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Form</label>
                  <select
                    className="input-field"
                    value={form.form}
                    onChange={(e) => setForm({ ...form, form: e.target.value })}
                  >
                    <option value="TABLET">TABLET</option>
                    <option value="CAPSULE">CAPSULE</option>
                    <option value="SYRUP">SYRUP</option>
                    <option value="INJECTION">INJECTION</option>
                  </select>
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Frequency</label>
                  <select
                    className="input-field"
                    value={form.frequency}
                    onChange={(e) => setForm({ ...form, frequency: e.target.value })}
                  >
                    <option value="ONCE_DAILY">ONCE_DAILY</option>
                    <option value="TWICE_DAILY">TWICE_DAILY</option>
                    <option value="THRICE_DAILY">THRICE_DAILY</option>
                    <option value="AS_NEEDED">AS_NEEDED</option>
                  </select>
                </div>
                <div>
                  <label className="input-label">Timing</label>
                  <select
                    className="input-field"
                    value={form.timing}
                    onChange={(e) => setForm({ ...form, timing: e.target.value })}
                  >
                    <option value="AFTER_MEAL">AFTER_MEAL</option>
                    <option value="BEFORE_MEAL">BEFORE_MEAL</option>
                    <option value="WITH_MEAL">WITH_MEAL</option>
                    <option value="EMPTY_STOMACH">EMPTY_STOMACH</option>
                  </select>
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Initial Stock Count</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={form.current_stock}
                    onChange={(e) => setForm({ ...form, current_stock: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Refill Warning Threshold</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={form.refill_threshold}
                    onChange={(e) => setForm({ ...form, refill_threshold: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Medication
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
