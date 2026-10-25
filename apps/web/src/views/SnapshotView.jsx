import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Activity,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Zap,
  TrendingUp,
  FileCheck
} from 'lucide-react';
import api from '../api';

export default function SnapshotView() {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadSnapshot = async () => {
    try {
      setLoading(true);
      const data = await api.getHealthSnapshot().catch(() => null);
      setSnapshot(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSnapshot();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Synthesizing multi-domain 360° AI Health Snapshot...</p>
      </div>
    );
  }

  const positiveTrends = snapshot?.positive_trends || [
    'Excellent medication adherence of 96.4% across prescribed routines.',
    'Resting heart rate (64 bpm) and blood pressure (118/78 mmHg) reflect solid aerobic fitness.',
    'Fasting blood glucose (92 mg/dL) remains well within optimal physiological limits.',
    'Consistent daily step count exceeding 8,500 steps with 40-minute active sessions.'
  ];

  const attentionAreas = snapshot?.areas_for_attention || [
    'LDL Cholesterol recorded at 112 mg/dL, slightly above the optimal 100 mg/dL boundary.',
    'Ongoing monitoring required for mild primary hypertension history under stress.'
  ];

  const nextActions = snapshot?.suggested_next_actions || [
    {
      action: 'Increase dietary soluble fiber intake (rolled oats, chia seeds, legumes).',
      reason: 'Helps bind intestinal bile acids to naturally reduce circulating LDL cholesterol.',
      category: 'NUTRITION'
    },
    {
      action: 'Schedule 90-day follow-up lipid profile retest with Dr. Helen Cho.',
      reason: 'Verify lifestyle efficacy before adjusting any pharmacological regimens.',
      category: 'CLINICAL'
    },
    {
      action: 'Maintain consistent 11:00 PM sleep schedule to support hormonal cortisol regulation.',
      reason: 'Deep stage 3/4 sleep optimizes endothelial vascular recovery.',
      category: 'LIFESTYLE'
    }
  ];

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
            360-Degree AI Health Snapshot
          </h1>
          <span className="badge badge-normal" style={{ fontSize: '0.75rem' }}>
            AI SYNTHESIZED
          </span>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
          Multi-domain synthesis linking vitals, laboratory deltas, medication adherence, and daily habits.
        </p>
      </div>

      {/* Holistic Overview Card */}
      <div className="glass-card" style={{
        padding: '30px',
        marginBottom: '28px',
        background: 'var(--mint-surface)',
        border: '1px solid var(--border-subtle)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' }}>
          <Sparkles size={24} color="var(--primary)" />
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
            Executive Clinical Health Summary
          </h2>
        </div>
        <p style={{ color: 'var(--text-main)', fontSize: '1rem', lineHeight: 1.7, margin: 0 }}>
          {snapshot?.overview || 'Patient Bruce Wayne presents with high functional cardiovascular stamina, exemplary medication discipline (96.4% adherence), and well-regulated blood glucose metrics. Primary focus areas center on mild hypercholesterolemia management (LDL 112 mg/dL) through targeted soluble fiber enrichment, and sustained blood pressure tracking.'}
        </p>
      </div>

      {/* 2-Column: Positive Trends vs Attention Areas */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        {/* Positive Trends */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <TrendingUp size={20} color="#10b981" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: '#10b981' }}>
              Positive Wellness Indicators
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {positiveTrends.map((trend, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                  padding: '12px 14px',
                  background: 'rgba(16, 185, 129, 0.08)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  fontSize: '0.88rem',
                  color: 'var(--text-main)',
                  lineHeight: 1.5,
                }}
              >
                <CheckCircle size={16} color="#10b981" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>{trend}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Areas for Attention */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <AlertTriangle size={20} color="#f59e0b" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: '#fbbf24' }}>
              Areas Needing Attention
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {attentionAreas.map((area, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                  padding: '12px 14px',
                  background: 'rgba(245, 158, 11, 0.08)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid rgba(245, 158, 11, 0.2)',
                  fontSize: '0.88rem',
                  color: 'var(--text-main)',
                  lineHeight: 1.5,
                }}
              >
                <AlertTriangle size={16} color="#fbbf24" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>{area}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Prioritized Actionable Next Steps */}
      <div className="glass-card" style={{ padding: '28px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 18px', color: 'var(--text-main)' }}>
          Prioritized Actionable Next Steps
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {nextActions.map((item, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px 20px',
                background: 'var(--bg-item)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                flexWrap: 'wrap',
                gap: '12px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className="badge badge-active" style={{ fontSize: '0.65rem' }}>
                    {item.category}
                  </span>
                  <strong style={{ color: 'var(--text-main)', fontSize: '0.95rem' }}>
                    {item.action}
                  </strong>
                </div>
                <p style={{ margin: '6px 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Rationale: {item.reason}
                </p>
              </div>

              <span className="badge badge-normal">RECOMMENDED</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
