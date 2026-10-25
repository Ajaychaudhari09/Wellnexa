import React from 'react';
import { Activity, Shield, User, Stethoscope, Sparkles, LogOut, CheckCircle2 } from 'lucide-react';

export default function Header({ currentRole, onSwitchRole, currentUser, onOpenSnapshot, onOpenAssistant }) {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(7, 13, 25, 0.85)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)',
        }}>
          <Activity size={24} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
              WellNexa<span style={{ color: '#06b6d4' }}>.AI</span>
            </span>
            <span className="badge badge-active" style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
              API: 8000 LIVE
            </span>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
            One Platform. Your Complete Health Journey.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={onOpenSnapshot}
          className="btn-secondary"
          style={{ fontSize: '0.85rem', padding: '8px 14px' }}
          title="360° AI Health Synthesis"
        >
          <Sparkles size={16} color="#06b6d4" />
          <span>360° Snapshot</span>
        </button>

        <button
          onClick={onOpenAssistant}
          className="btn-primary"
          style={{ fontSize: '0.85rem', padding: '8px 16px' }}
        >
          <Sparkles size={16} />
          <span>AI Assistant</span>
        </button>

        {/* Role Switcher */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: 'rgba(15, 23, 42, 0.9)',
          padding: '4px',
          borderRadius: '12px',
          border: '1px solid var(--border-subtle)',
          marginLeft: '8px',
        }}>
          <button
            onClick={() => onSwitchRole('PATIENT')}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: 'none',
              background: currentRole === 'PATIENT' ? 'linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)' : 'transparent',
              color: currentRole === 'PATIENT' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.2s',
            }}
          >
            <User size={14} />
            Patient
          </button>
          <button
            onClick={() => onSwitchRole('DOCTOR')}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: 'none',
              background: currentRole === 'DOCTOR' ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' : 'transparent',
              color: currentRole === 'DOCTOR' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.2s',
            }}
          >
            <Stethoscope size={14} />
            Doctor
          </button>
        </div>

        {currentUser && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingLeft: '8px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: currentRole === 'DOCTOR' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(6, 182, 212, 0.2)',
              border: `1px solid ${currentRole === 'DOCTOR' ? '#8b5cf6' : '#06b6d4'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.85rem',
              color: '#f8fafc',
            }}>
              {currentRole === 'DOCTOR' ? 'HC' : 'BW'}
            </div>
            <div style={{ lineHeight: 1.2 }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                {currentRole === 'DOCTOR' ? 'Dr. Helen Cho' : `${currentUser.first_name || 'Bruce'} ${currentUser.last_name || 'Wayne'}`}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                {currentRole === 'DOCTOR' ? 'doctor@wellnexa.ai' : 'patient@wellnexa.ai'}
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
