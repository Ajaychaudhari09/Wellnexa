import React from 'react';
import {
  LayoutDashboard,
  HeartPulse,
  FileSpreadsheet,
  Pill,
  BellRing,
  UtensilsCrossed,
  Flame,
  Smile,
  BotMessageSquare,
  Sparkles,
  Stethoscope,
  ShieldCheck,
  ChevronRight,
  CalendarDays,
  X
} from 'lucide-react';

const PATIENT_NAV_ITEMS = [
  { id: 'dashboard', label: 'Overview', icon: LayoutDashboard, aliases: ['dashboard'] },
  { id: 'my_health', label: 'My Health', icon: HeartPulse, aliases: ['my_health', 'profile', 'reports'] },
  { id: 'meds_reminders', label: 'Medicines & Reminders', icon: Pill, aliases: ['meds_reminders', 'medicines', 'reminders'] },
  { id: 'appointments', label: 'Appointments', icon: CalendarDays, aliases: ['appointments'] },
  { id: 'wellness', label: 'Wellness Hub', icon: Flame, aliases: ['wellness', 'nutrition', 'fitness'] },
  { id: 'assistant', label: 'AI Health Assistant', icon: BotMessageSquare, highlight: true, aliases: ['assistant', 'snapshot'] },
  { id: 'privacy', label: 'Settings & Privacy', icon: ShieldCheck, aliases: ['privacy'] },
];

const DOCTOR_NAV_ITEMS = [
  { id: 'doctor', label: 'Clinical Portal', icon: Stethoscope, highlight: true, aliases: ['doctor'] },
  { id: 'appointments', label: 'Patient Consultations', icon: CalendarDays, aliases: ['appointments'] },
  { id: 'privacy', label: 'Compliance & Audit', icon: ShieldCheck, aliases: ['privacy'] },
];

export default function Sidebar({ activeTab, onSelectTab, currentRole, mobileOpen, onCloseMobile }) {
  const items = currentRole === 'DOCTOR' ? DOCTOR_NAV_ITEMS : PATIENT_NAV_ITEMS;

  const handleItemClick = (id) => {
    onSelectTab(id);
    if (onCloseMobile) onCloseMobile();
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div
          onClick={onCloseMobile}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(36, 59, 58, 0.45)',
            backdropFilter: 'blur(4px)',
            zIndex: 90,
          }}
          className="mobile-backdrop"
        />
      )}

      {/* Sidebar Drawer */}
      <aside
        className={`sidebar-container ${mobileOpen ? 'mobile-open' : ''}`}
        style={{
          width: '260px',
          minWidth: '260px',
          background: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 65px)',
          position: 'sticky',
          top: '65px',
          padding: '20px 14px',
          overflowY: 'auto',
          zIndex: 95,
          transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.25s',
        }}
      >
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0 10px 12px',
        }}>
          <span style={{
            fontSize: '0.72rem',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--text-faint)',
            fontWeight: 700,
          }}>
            {currentRole === 'DOCTOR' ? 'Physician Workspace' : 'Health Journey'}
          </span>

          {mobileOpen && (
            <button
              onClick={onCloseMobile}
              className="btn-secondary"
              style={{ padding: '4px', borderRadius: '6px' }}
            >
              <X size={16} />
            </button>
          )}
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '5px', flex: 1 }}>
          {items.map((item) => {
            const Icon = item.icon;
            const isActive = item.aliases ? item.aliases.includes(activeTab) : activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleItemClick(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '11px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  background: isActive
                    ? 'linear-gradient(90deg, var(--mint-surface) 0%, rgba(209, 250, 229, 0.3) 100%)'
                    : 'transparent',
                  color: isActive ? 'var(--primary-deep)' : 'var(--text-muted)',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  borderLeft: isActive ? '3px solid var(--primary)' : '3px solid transparent',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'var(--btn-secondary-bg)';
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'transparent';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Icon size={18} color={isActive ? 'var(--primary)' : 'currentColor'} />
                  <span>{item.label}</span>
                </div>
                {item.highlight && !isActive && (
                  <span style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: 'var(--primary)',
                    boxShadow: '0 0 8px var(--primary)',
                  }} />
                )}
                {isActive && <ChevronRight size={14} color="var(--primary)" />}
              </button>
            );
          })}
        </nav>

        <div style={{
          padding: '14px',
          background: 'var(--bg-item)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
          marginTop: '16px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
            <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-main)' }}>
              MCA Capstone Active
            </span>
          </div>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
            Full OCR, RAG LLM, and Clinical Safety Engine connected.
          </p>
        </div>
      </aside>

      <style>{`
        @media (max-width: 1024px) {
          .sidebar-container {
            position: fixed !important;
            top: 0 !important;
            bottom: 0 !important;
            left: 0 !important;
            height: 100vh !important;
            transform: translateX(-100%);
            box-shadow: var(--shadow-dropdown);
          }
          .sidebar-container.mobile-open {
            transform: translateX(0) !important;
          }
        }
      `}</style>
    </>
  );
}
