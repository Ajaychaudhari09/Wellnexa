import React, { useState, useEffect } from 'react';
import {
  Flame,
  Activity,
  Plus,
  CheckCircle,
  Moon,
  Footprints,
  Clock,
  Dumbbell,
  Sparkles,
  Zap
} from 'lucide-react';
import api from '../api';

export default function FitnessView() {
  const [dailyActivity, setDailyActivity] = useState(null);
  const [workouts, setWorkouts] = useState([]);
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showWorkoutModal, setShowWorkoutModal] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  const [workoutForm, setWorkoutForm] = useState({
    activity_type: 'RUNNING',
    title: 'Evening Zone-2 Aerobic Run',
    duration_minutes: '35',
    calories_burned: '350',
    intensity: 'MEDIUM',
  });

  const loadFitnessData = async () => {
    try {
      setLoading(true);
      const [act, w, h] = await Promise.all([
        api.getDailyActivity().catch(() => null),
        api.getWorkouts().catch(() => []),
        api.getHabits().catch(() => []),
      ]);
      setDailyActivity(act);
      setWorkouts(w || []);
      setHabits(h || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFitnessData();
  }, []);

  const handleCheckInHabit = async (habitId, title) => {
    try {
      await api.checkInHabit(habitId);
      setActionSuccess(`Checked in habit: ${title}!`);
      setTimeout(() => setActionSuccess(null), 3000);
      loadFitnessData();
    } catch (err) {
      alert(`Error checking in habit: ${err.message}`);
    }
  };

  const handleSaveWorkout = async (e) => {
    e.preventDefault();
    try {
      await api.logWorkout({
        ...workoutForm,
        duration_minutes: parseInt(workoutForm.duration_minutes, 10),
        calories_burned: parseFloat(workoutForm.calories_burned),
      });
      setShowWorkoutModal(false);
      setActionSuccess('Workout logged successfully!');
      setTimeout(() => setActionSuccess(null), 3000);
      loadFitnessData();
    } catch (err) {
      alert(`Error logging workout: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading fitness and lifestyle activity engine...</p>
      </div>
    );
  }

  const steps = dailyActivity?.steps || 8750;
  const activeMinutes = dailyActivity?.active_minutes || 45;
  const sleepHours = dailyActivity?.sleep_hours || 7.8;
  const sleepQuality = dailyActivity?.sleep_quality || 5;

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
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
            Fitness & Daily Lifestyle
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Daily step counts, active minutes, sleep quality, workout logging, and habit streaks.
          </p>
        </div>

        <button onClick={() => setShowWorkoutModal(true)} className="btn-primary">
          <Plus size={16} /> Log Workout Session
        </button>
      </div>

      {/* 4-Stat Activity Cards */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        {/* Steps */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>DAILY STEPS</span>
            <Footprints size={18} color="var(--primary)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)', margin: '8px 0 4px' }}>
            {steps.toLocaleString()} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/ 10,000</span>
          </div>
          <div className="progress-bar-bg" style={{ marginTop: '8px' }}>
            <div className="progress-bar-fill" style={{ width: `${Math.min(100, (steps / 10000) * 100)}%`, background: 'var(--primary)' }} />
          </div>
        </div>

        {/* Active Minutes */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>ACTIVE TIME</span>
            <Zap size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10b981', margin: '8px 0 4px' }}>
            {activeMinutes} <span style={{ fontSize: '1rem', fontWeight: 500 }}>min</span>
          </div>
          <span className="badge badge-normal" style={{ fontSize: '0.72rem' }}>
            Goal Achieved (30+ min)
          </span>
        </div>

        {/* Sleep Hours & Quality */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>SLEEP DURATION</span>
            <Moon size={18} color="#8b5cf6" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#a78bfa', margin: '8px 0 4px' }}>
            {sleepHours} <span style={{ fontSize: '1rem', fontWeight: 500 }}>hrs</span>
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Quality: {'★'.repeat(sleepQuality)} ({sleepQuality}/5)
          </span>
        </div>

        {/* Active Calorie Burn */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>ACTIVE BURN</span>
            <Flame size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fbbf24', margin: '8px 0 4px' }}>
            410 <span style={{ fontSize: '1rem', fontWeight: 500 }}>kcal</span>
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            High Cardio Intensity
          </span>
        </div>
      </div>

      {/* 2-Column: Workouts & Habits */}
      <div className="grid-2">
        {/* Workouts History */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
              Logged Workout Sessions
            </h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {workouts.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No workouts recorded for today.</p>
            ) : (
              workouts.map((w) => (
                <div
                  key={w.id || w.title}
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
                      background: 'rgba(245, 158, 11, 0.15)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      <Dumbbell size={18} color="#f59e0b" />
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem' }}>
                        {w.title}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {w.duration_minutes} min • {w.calories_burned} kcal • {w.activity_type}
                      </div>
                    </div>
                  </div>

                  <span className="badge badge-normal">
                    {w.intensity}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Habits Streaks */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
              Daily Habit Check-In Streaks
            </h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { id: '1', title: 'Morning Hydration (500ml)', streak: 14, done: true },
              { id: '2', title: '10,000 Daily Steps Goal', streak: 9, done: false },
              { id: '3', title: 'Post-Workout Mobility & Stretch', streak: 6, done: false },
            ].map((habit) => (
              <div
                key={habit.id}
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
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem' }}>
                    {habit.title}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={12} /> {habit.streak} Day Active Streak
                  </div>
                </div>

                <div>
                  {habit.done ? (
                    <span className="badge badge-normal">
                      <CheckCircle size={12} /> Done Today
                    </span>
                  ) : (
                    <button
                      onClick={() => handleCheckInHabit(habit.id, habit.title)}
                      className="btn-primary"
                      style={{ fontSize: '0.8rem', padding: '6px 14px' }}
                    >
                      Check In
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal: Log Workout */}
      {showWorkoutModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-main)' }}>
              Log Workout Session
            </h2>
            <form onSubmit={handleSaveWorkout} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Workout Title</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={workoutForm.title}
                  onChange={(e) => setWorkoutForm({ ...workoutForm, title: e.target.value })}
                />
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Activity Type</label>
                  <select
                    className="input-field"
                    value={workoutForm.activity_type}
                    onChange={(e) => setWorkoutForm({ ...workoutForm, activity_type: e.target.value })}
                  >
                    <option value="RUNNING">RUNNING</option>
                    <option value="CYCLING">CYCLING</option>
                    <option value="WALKING">WALKING</option>
                    <option value="SWIMMING">SWIMMING</option>
                    <option value="GYM_STRENGTH">GYM_STRENGTH</option>
                    <option value="YOGA">YOGA</option>
                  </select>
                </div>
                <div>
                  <label className="input-label">Intensity</label>
                  <select
                    className="input-field"
                    value={workoutForm.intensity}
                    onChange={(e) => setWorkoutForm({ ...workoutForm, intensity: e.target.value })}
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                  </select>
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label className="input-label">Duration (Minutes)</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={workoutForm.duration_minutes}
                    onChange={(e) => setWorkoutForm({ ...workoutForm, duration_minutes: e.target.value })}
                  />
                </div>
                <div>
                  <label className="input-label">Estimated Calories Burned</label>
                  <input
                    type="number"
                    required
                    className="input-field"
                    value={workoutForm.calories_burned}
                    onChange={(e) => setWorkoutForm({ ...workoutForm, calories_burned: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowWorkoutModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Workout
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
