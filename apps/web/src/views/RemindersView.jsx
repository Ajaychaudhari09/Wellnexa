import React, { useState, useEffect } from 'react';
import {
  BellRing,
  Activity,
  Plus,
  CheckCircle,
  Clock,
  Calendar,
  Droplets,
  Pill,
  Stethoscope
} from 'lucide-react';
import api from '../api';

export default function RemindersView() {
  const [reminders, setReminders] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  const [form, setForm] = useState({
    title: '',
    reminder_type: 'MEDICINE',
    due_time: '09:00',
    recurrence: 'DAILY',
  });

  const loadReminders = async () => {
    try {
      setLoading(true);
      const data = await api.getReminders();
      setReminders(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReminders();
  }, []);

  const handleComplete = async (id, title) => {
    try {
      await api.completeReminder(id);
      setActionSuccess(`Completed: ${title}!`);
      setTimeout(() => setActionSuccess(null), 3000);
      loadReminders();
    } catch (err) {
      alert(`Error completing reminder: ${err.message}`);
    }
  };

  const handleAddReminder = async (e) => {
    e.preventDefault();
    try {
      await api.addReminder(form);
      setShowAddModal(false);
      setForm({
        title: '',
        reminder_type: 'MEDICINE',
        due_time: '09:00',
        recurrence: 'DAILY',
      });
      setActionSuccess('Reminder created successfully!');
      setTimeout(() => setActionSuccess(null), 3000);
      loadReminders();
    } catch (err) {
      alert(`Error creating reminder: ${err.message}`);
    }
  };

  const filteredReminders = reminders.filter((r) => {
    if (filter === 'ALL') return true;
    return r.reminder_type === filter;
  });

  const getTypeIcon = (type) => {
    switch (type) {
      case 'MEDICINE':
        return <Pill size={16} color="#06b6d4" />;
      case 'WATER':
        return <Droplets size={16} color="#3b82f6" />;
      case 'APPOINTMENT':
        return <Calendar size={16} color="#8b5cf6" />;
      default:
        return <BellRing size={16} color="#f59e0b" />;
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading smart reminders engine...</p>
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
            Central Smart Reminder Engine
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Multi-category health schedules with user quiet-hours and automatic recurrence.
          </p>
        </div>

        <button onClick={() => setShowAddModal(true)} className="btn-primary">
          <Plus size={16} /> New Smart Reminder
        </button>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
        {['ALL', 'MEDICINE', 'WATER', 'APPOINTMENT', 'CHECKUP'].map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className="btn-secondary"
            style={{
              fontSize: '0.82rem',
              padding: '6px 14px',
              background: filter === cat ? 'linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)' : 'rgba(30, 41, 59, 0.6)',
              color: filter === cat ? '#ffffff' : 'var(--text-muted)',
              borderColor: filter === cat ? '#06b6d4' : 'var(--border-subtle)',
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Reminders List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredReminders.length === 0 ? (
          <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No reminders found in this category.
          </div>
        ) : (
          filteredReminders.map((rem) => (
            <div
              key={rem.id}
              className="glass-card"
              style={{
                padding: '18px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: rem.is_completed ? 'rgba(16, 185, 129, 0.15)' : 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  {getTypeIcon(rem.reminder_type)}
                </div>

                <div>
                  <div style={{
                    fontSize: '1rem',
                    fontWeight: 600,
                    color: rem.is_completed ? 'var(--text-muted)' : '#f8fafc',
                    textDecoration: rem.is_completed ? 'line-through' : 'none',
                  }}>
                    {rem.title}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px', marginTop: '3px' }}>
                    <Clock size={12} /> Due: <strong>{rem.due_time}</strong> • Recurrence: <strong>{rem.recurrence}</strong>
                    <span className="badge badge-active" style={{ fontSize: '0.65rem' }}>
                      {rem.reminder_type}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                {rem.is_completed ? (
                  <span className="badge badge-normal">
                    <CheckCircle size={12} /> Completed
                  </span>
                ) : (
                  <button
                    onClick={() => handleComplete(rem.id, rem.title)}
                    className="btn-secondary"
                    style={{ fontSize: '0.82rem', padding: '6px 14px' }}
                  >
                    <CheckCircle size={14} color="#10b981" /> Complete
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal: Add Reminder */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: '#f8fafc' }}>
              Create Smart Health Reminder
            </h2>
            <form onSubmit={handleAddReminder} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Reminder Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Morning Vitals Check, Hydration Break"
                  className="input-field"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                />
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Category</label>
                  <select
                    className="input-field"
                    value={form.reminder_type}
                    onChange={(e) => setForm({ ...form, reminder_type: e.target.value })}
                  >
                    <option value="MEDICINE">MEDICINE</option>
                    <option value="WATER">WATER</option>
                    <option value="APPOINTMENT">APPOINTMENT</option>
                    <option value="CHECKUP">CHECKUP</option>
                    <option value="GENERAL">GENERAL</option>
                  </select>
                </div>
                <div>
                  <label className="input-label">Due Time</label>
                  <input
                    type="time"
                    required
                    className="input-field"
                    value={form.due_time}
                    onChange={(e) => setForm({ ...form, due_time: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="input-label">Recurrence</label>
                <select
                  className="input-field"
                  value={form.recurrence}
                  onChange={(e) => setForm({ ...form, recurrence: e.target.value })}
                >
                  <option value="DAILY">DAILY</option>
                  <option value="WEEKDAYS">WEEKDAYS</option>
                  <option value="WEEKLY">WEEKLY</option>
                  <option value="ONCE">ONCE</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Reminder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
