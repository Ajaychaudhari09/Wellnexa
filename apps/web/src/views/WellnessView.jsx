import React, { useState, useEffect } from 'react';
import {
  Smile,
  Activity,
  Heart,
  ShieldAlert,
  Sparkles,
  CheckCircle,
  PhoneCall,
  BookOpen,
  Send
} from 'lucide-react';
import api from '../api';

const EMOTIONS = ['ENERGETIC', 'CALM', 'HAPPY', 'FOCUSED', 'TIRED', 'STRESSED', 'ANXIOUS'];

export default function WellnessView() {
  const [moodLog, setMoodLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [moodScore, setMoodScore] = useState(5);
  const [emotion, setEmotion] = useState('ENERGETIC');
  const [journalText, setJournalText] = useState('Solid morning workout and clarity for today\'s health goals.');
  const [gratitudeNote, setGratitudeNote] = useState('Grateful for energy and good cardiovascular stamina.');
  const [actionSuccess, setActionSuccess] = useState(null);

  const loadWellness = async () => {
    try {
      setLoading(true);
      const data = await api.getTodayMood().catch(() => null);
      if (data) {
        setMoodLog(data);
        setMoodScore(data.mood_score);
        setEmotion(data.primary_emotion);
        setJournalText(data.journal_text || '');
        setGratitudeNote(data.gratitude_note || '');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWellness();
  }, []);

  const handleSaveMood = async (e) => {
    e.preventDefault();
    try {
      await api.logMood({
        mood_score: moodScore,
        primary_emotion: emotion,
        journal_text: journalText,
        gratitude_note: gratitudeNote,
      });
      setActionSuccess('Mental wellness check-in recorded!');
      setTimeout(() => setActionSuccess(null), 3000);
      loadWellness();
    } catch (err) {
      alert(`Error saving mood: ${err.message}`);
    }
  };

  const isLowMood = moodScore <= 2 || emotion === 'STRESSED' || emotion === 'ANXIOUS';

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
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
          Mental Wellness Journal & Crisis Guardrails
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
          Daily mood rating, reflective prompts, gratitude logging, and clinical safety guardrails.
        </p>
      </div>

      {/* AI Crisis Guardrails Banner */}
      <div className="glass-card" style={{
        padding: '24px 28px',
        marginBottom: '28px',
        background: isLowMood ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, var(--bg-item) 100%)' : 'var(--bg-item)',
        border: `1px solid ${isLowMood ? 'rgba(239, 68, 68, 0.4)' : 'var(--border-subtle)'}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(239, 68, 68, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <ShieldAlert size={22} color="#f87171" />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-main)' }}>
                AI Crisis Guardrails & 24/7 Verified Helplines
              </h3>
              <p style={{ margin: '4px 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                WellNexa AI is an educational and wellness management platform, not a substitute for clinical emergency care.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <a
              href="tel:14416"
              className="btn-danger"
              style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <PhoneCall size={14} /> Tele-MANAS (14416)
            </a>
            <a
              href="tel:18005990019"
              className="btn-secondary"
              style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <PhoneCall size={14} /> KIRAN (1800-599-0019)
            </a>
          </div>
        </div>
      </div>

      {/* Main Form: Daily Check-In */}
      <div className="glass-card" style={{ padding: '32px' }}>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 700, margin: '0 0 20px', color: 'var(--text-main)' }}>
          Daily Mood & Gratitude Check-In
        </h2>

        <form onSubmit={handleSaveMood} style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* 1-5 Mood Score */}
          <div>
            <label className="input-label">Mood Score (1: Low / Distress — 5: Peak Energy & Clarity)</label>
            <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
              {[1, 2, 3, 4, 5].map((val) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setMoodScore(val)}
                  style={{
                    flex: 1,
                    padding: '14px',
                    borderRadius: 'var(--radius-md)',
                    border: moodScore === val ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                    background: moodScore === val ? 'var(--mint-surface)' : 'var(--bg-item)',
                    color: moodScore === val ? 'var(--primary-deep)' : 'var(--text-main)',
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  {val === 1 && '😔 1'}
                  {val === 2 && '😕 2'}
                  {val === 3 && '😐 3'}
                  {val === 4 && '😊 4'}
                  {val === 5 && '🌟 5'}
                </button>
              ))}
            </div>
          </div>

          {/* Primary Emotion Selector */}
          <div>
            <label className="input-label">Primary Emotion</label>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
              {EMOTIONS.map((emo) => (
                <button
                  key={emo}
                  type="button"
                  onClick={() => setEmotion(emo)}
                  className="btn-secondary"
                  style={{
                    fontSize: '0.8rem',
                    padding: '8px 14px',
                    background: emotion === emo ? 'var(--primary)' : 'var(--bg-item)',
                    color: emotion === emo ? '#ffffff' : 'var(--text-main)',
                    borderColor: emotion === emo ? 'var(--primary)' : 'var(--border-subtle)',
                  }}
                >
                  {emo}
                </button>
              ))}
            </div>
          </div>

          {/* Gratitude Reflection */}
          <div>
            <label className="input-label">Gratitude Note</label>
            <input
              type="text"
              className="input-field"
              placeholder="What are 1-2 things you are grateful for today?"
              value={gratitudeNote}
              onChange={(e) => setGratitudeNote(e.target.value)}
            />
          </div>

          {/* Journal Reflection */}
          <div>
            <label className="input-label">Reflective Journal</label>
            <textarea
              className="input-field"
              rows={4}
              placeholder="Write any thoughts, stressors, or physical sensations..."
              value={journalText}
              onChange={(e) => setJournalText(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="btn-primary" style={{ padding: '10px 24px' }}>
              <Send size={16} /> Save Daily Check-In
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
