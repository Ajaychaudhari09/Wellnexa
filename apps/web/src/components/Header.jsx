import React, { useState } from 'react';
import {
  Activity,
  User,
  Stethoscope,
  Sparkles,
  Sun,
  Moon,
  Menu,
  X,
  Bell,
  CheckCircle2,
  Clock,
  ShieldCheck
} from 'lucide-react';

export default function Header({
  currentRole,
  onSwitchRole,
  currentUser,
  theme,
  onToggleTheme,
  mobileSidebarOpen,
  onToggleMobileSidebar,
  onOpenSnapshot,
  onOpenAssistant
}) {
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, title: 'Medication Due', desc: 'Take Metformin (500mg) at 08:30 AM', time: '10m ago', icon: Clock },
    { id: 2, title: 'Lab Results Verified', desc: 'Annual Lipid Profile 2026 is confirmed', time: '1h ago', icon: CheckCircle2 },
    { id: 3, title: 'Doctor Clinical Pass', desc: '24-hour pass active for Dr. Helen Cho', time: '3h ago', icon: ShieldCheck },
  ];

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 24px',
      borderBottom: '1px solid var(--border-subtle)',
      background: 'var(--bg-header)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: 'var(--shadow-card)',
    }}>
      {/* Left: Mobile Menu Toggle + Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Mobile Hamburger (visible on screens <= 1024px) */}
        <button
          onClick={onToggleMobileSidebar}
          className="btn-secondary mobile-menu-btn"
          style={{ padding: '8px', borderRadius: '8px' }}
          aria-label="Toggle navigation menu"
        >
          {mobileSidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--aqua) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px var(--primary-glow)',
            flexShrink: 0,
          }}>
            <Activity size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-main)' }}>
                WellNexa<span style={{ color: 'var(--primary)' }}>.AI</span>
              </span>
              <span className="badge badge-active" style={{ fontSize: '0.65rem', padding: '2px 7px' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
                LIVE: 8000
              </span>
            </div>
            <p className="header-subtitle" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
              One Platform. Your Complete Health Journey.
            </p>
          </div>
        </div>
      </div>

      {/* Right: Quick actions, Theme toggle, Role switcher, User profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Quick Snapshot button */}
        <button
          onClick={onOpenSnapshot}
          className="btn-secondary header-action-btn"
          style={{ fontSize: '0.82rem', padding: '7px 12px' }}
          title="360° AI Health Synthesis"
        >
          <Sparkles size={15} color="var(--primary)" />
          <span className="hide-on-mobile">360° Snapshot</span>
        </button>

        {/* AI Assistant button */}
        <button
          onClick={onOpenAssistant}
          className="btn-primary"
          style={{ fontSize: '0.82rem', padding: '7px 14px' }}
        >
          <Sparkles size={15} />
          <span className="hide-on-mobile">AI Assistant</span>
        </button>

        {/* Day / Night Mode Toggle */}
        <button
          onClick={onToggleTheme}
          className="btn-secondary"
          style={{
            padding: '8px 10px',
            borderRadius: '10px',
            color: 'var(--text-main)',
            position: 'relative',
          }}
          title={theme === 'dark' ? 'Switch to Day Mode (Light)' : 'Switch to Night Mode (Dark)'}
          aria-label="Toggle Theme"
        >
          {theme === 'dark' ? (
            <Sun size={18} color="#f59e0b" />
          ) : (
            <Moon size={18} color="#6366f1" />
          )}
        </button>

        {/* Notification Bell with Badge & Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="btn-secondary"
            style={{ padding: '8px 10px', borderRadius: '10px', position: 'relative' }}
            title="Notifications"
            aria-label="View notifications"
          >
            <Bell size={18} />
            <span style={{
              position: 'absolute',
              top: '4px',
              right: '4px',
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#ef4444',
            }} />
          </button>

          {showNotifications && (
            <div style={{
              position: 'absolute',
              right: 0,
              top: '46px',
              width: '320px',
              background: 'var(--bg-card)',
              backdropFilter: 'blur(16px)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-dropdown)',
              padding: '16px',
              zIndex: 100,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)' }}>Notifications</strong>
                <span className="badge badge-normal" style={{ fontSize: '0.65rem' }}>3 New</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {notifications.map((n) => {
                  const Icon = n.icon;
                  return (
                    <div
                      key={n.id}
                      style={{
                        padding: '10px 12px',
                        background: 'var(--bg-item)',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '10px',
                      }}
                    >
                      <Icon size={16} color="#06b6d4" style={{ marginTop: '2px', flexShrink: 0 }} />
                      <div>
                        <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-main)' }}>{n.title}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{n.desc}</div>
                        <span style={{ fontSize: '0.68rem', color: 'var(--text-faint)' }}>{n.time}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Role Switcher */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: 'var(--bg-item)',
          padding: '3px',
          borderRadius: '12px',
          border: '1px solid var(--border-subtle)',
        }}>
          <button
            onClick={() => onSwitchRole('PATIENT')}
            style={{
              padding: '5px 10px',
              borderRadius: '8px',
              border: 'none',
              background: currentRole === 'PATIENT' ? 'linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)' : 'transparent',
              color: currentRole === 'PATIENT' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <User size={13} />
            <span className="hide-on-mobile">Patient</span>
          </button>
          <button
            onClick={() => onSwitchRole('DOCTOR')}
            style={{
              padding: '5px 10px',
              borderRadius: '8px',
              border: 'none',
              background: currentRole === 'DOCTOR' ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' : 'transparent',
              color: currentRole === 'DOCTOR' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <Stethoscope size={13} />
            <span className="hide-on-mobile">Doctor</span>
          </button>
        </div>

        {/* User Avatar & Name */}
        {currentUser && (
          <div className="hide-on-mobile" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '34px',
              height: '34px',
              borderRadius: '50%',
              background: currentRole === 'DOCTOR' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(6, 182, 212, 0.2)',
              border: `1px solid ${currentRole === 'DOCTOR' ? 'var(--violet)' : 'var(--primary)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.8rem',
              color: 'var(--text-main)',
            }}>
              {currentRole === 'DOCTOR' ? 'HC' : 'BW'}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @media (min-width: 1025px) {
          .mobile-menu-btn { display: none !important; }
        }
        @media (max-width: 768px) {
          .hide-on-mobile { display: none !important; }
          .header-subtitle { display: none !important; }
        }
      `}</style>
    </header>
  );
}
