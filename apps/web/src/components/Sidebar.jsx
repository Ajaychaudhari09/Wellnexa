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
  User,
  LogOut,
  X
} from 'lucide-react';

const PATIENT_NAV_SECTIONS = [
  {
    title: 'OVERVIEW',
    items: [
      { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
    ],
  },
  {
    title: 'HEALTH RECORDS',
    items: [
      { id: 'profile', label: 'Health Profile & Vitals', icon: HeartPulse },
      { id: 'reports', label: 'Lab Reports & OCR', icon: FileSpreadsheet },
    ],
  },
  {
    title: 'SCHEDULES & VISITS',
    items: [
      { id: 'medicines', label: 'Prescriptions & Meds', icon: Pill },
      { id: 'reminders', label: 'Smart Reminders', icon: BellRing },
      { id: 'appointments', label: 'Appointments & Visits', icon: CalendarDays },
    ],
  },
  {
    title: 'WELLNESS & LIFESTYLE',
    items: [
      { id: 'nutrition', label: 'AI Nutrition & Diet', icon: UtensilsCrossed },
      { id: 'fitness', label: 'Fitness & Activity', icon: Flame },
      { id: 'wellness', label: 'Mental Wellness', icon: Smile },
    ],
  },
  {
    title: 'CLINICAL AI',
    items: [
      { id: 'assistant', label: 'AI Health Assistant', icon: BotMessageSquare, highlight: true },
      { id: 'snapshot', label: '360° Health Synthesis', icon: Sparkles },
    ],
  },
  {
    title: 'ACCOUNT & PRIVACY',
    items: [
      { id: 'profile_account', label: 'My Account Profile', icon: User },
      { id: 'privacy', label: 'Settings & Privacy', icon: ShieldCheck },
    ],
  },
];

const DOCTOR_NAV_SECTIONS = [
  {
    title: 'PHYSICIAN WORKSPACE',
    items: [
      { id: 'doctor', label: 'Clinical Review Portal', icon: Stethoscope, highlight: true },
      { id: 'appointments', label: 'Patient Consultations', icon: CalendarDays },
      { id: 'profile_account', label: 'Physician Profile', icon: User },
      { id: 'privacy', label: 'Compliance & Audit', icon: ShieldCheck },
    ],
  },
];

export default function Sidebar({
  activeTab,
  onSelectTab,
  currentRole,
  currentUser,
  onLogout,
  mobileOpen,
  onCloseMobile
}) {
  const sections = currentRole === 'DOCTOR' ? DOCTOR_NAV_SECTIONS : PATIENT_NAV_SECTIONS;

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
          padding: '16px 12px',
          overflowY: 'auto',
          zIndex: 95,
          transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.25s',
        }}
      >
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0 8px 12px',
        }}>
          <span style={{
            fontSize: '0.72rem',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--text-faint)',
            fontWeight: 700,
          }}>
            {currentRole === 'DOCTOR' ? 'PHYSICIAN WORKSPACE' : 'HEALTHCARE NAVIGATION'}
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

        {/* Navigation Sections */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '14px', flex: 1 }}>
          {sections.map((section, sIdx) => (
            <div key={sIdx}>
              <div style={{
                fontSize: '0.66rem',
                textTransform: 'uppercase',
                letterSpacing: '0.07em',
                color: 'var(--text-faint)',
                fontWeight: 700,
                padding: '4px 10px',
                marginBottom: '2px',
              }}>
                {section.title}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleItemClick(item.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '9px 12px',
                        borderRadius: 'var(--radius-md)',
                        border: 'none',
                        background: isActive
                          ? 'linear-gradient(90deg, var(--mint-surface) 0%, rgba(209, 250, 229, 0.4) 100%)'
                          : 'transparent',
                        color: isActive ? 'var(--primary-deep)' : 'var(--text-muted)',
                        fontWeight: isActive ? 700 : 500,
                        fontSize: '0.85rem',
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
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Icon size={17} color={isActive ? 'var(--primary)' : 'currentColor'} />
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
              </div>
            </div>
          ))}
        </nav>

        {/* User Card & Logout at Bottom */}
        <div style={{
          padding: '12px',
          background: 'var(--bg-item)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
          marginTop: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
            <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {currentUser?.email || (currentRole === 'DOCTOR' ? 'doctor@wellnexa.ai' : 'patient@wellnexa.ai')}
            </span>
          </div>

          <button
            onClick={onLogout}
            className="btn-danger"
            style={{
              padding: '6px 10px',
              fontSize: '0.76rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
            }}
          >
            <LogOut size={13} /> Sign Out
          </button>
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
