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
  ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Home Dashboard', icon: LayoutDashboard },
  { id: 'profile', label: 'Health Profile & Vitals', icon: HeartPulse },
  { id: 'reports', label: 'Lab Reports & OCR', icon: FileSpreadsheet },
  { id: 'medicines', label: 'Medicines & Adherence', icon: Pill },
  { id: 'reminders', label: 'Smart Reminders', icon: BellRing },
  { id: 'nutrition', label: 'Nutrition & Meals', icon: UtensilsCrossed },
  { id: 'fitness', label: 'Fitness & Lifestyle', icon: Flame },
  { id: 'wellness', label: 'Mental Wellness', icon: Smile },
  { id: 'assistant', label: 'AI Health Assistant', icon: BotMessageSquare, highlight: true },
  { id: 'snapshot', label: '360° AI Snapshot', icon: Sparkles },
  { id: 'doctor', label: 'Doctor Clinical Portal', icon: Stethoscope },
  { id: 'privacy', label: 'Consent & Privacy', icon: ShieldCheck },
];

export default function Sidebar({ activeTab, onSelectTab, currentRole }) {
  return (
    <aside style={{
      width: '260px',
      minWidth: '260px',
      background: 'rgba(10, 17, 32, 0.95)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 75px)',
      position: 'sticky',
      top: '75px',
      padding: '20px 14px',
      overflowY: 'auto',
    }}>
      <div style={{
        fontSize: '0.72rem',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        color: 'var(--text-faint)',
        fontWeight: 700,
        padding: '0 12px 10px',
      }}>
        Clinical Modules
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                background: isActive
                  ? 'linear-gradient(90deg, rgba(6, 182, 212, 0.15) 0%, rgba(6, 182, 212, 0.05) 100%)'
                  : 'transparent',
                color: isActive ? '#06b6d4' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.88rem',
                cursor: 'pointer',
                textAlign: 'left',
                borderLeft: isActive ? '3px solid #06b6d4' : '3px solid transparent',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = 'transparent';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Icon size={18} color={isActive ? '#06b6d4' : 'currentColor'} />
                <span>{item.label}</span>
              </div>
              {item.highlight && !isActive && (
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: '#06b6d4',
                  boxShadow: '0 0 8px #06b6d4',
                }} />
              )}
              {isActive && <ChevronRight size={14} color="#06b6d4" />}
            </button>
          );
        })}
      </nav>

      <div style={{
        padding: '14px',
        background: 'rgba(15, 23, 42, 0.6)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        marginTop: '16px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#f8fafc' }}>
            MCA Capstone Active
          </span>
        </div>
        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
          Full-stack integration of OCR, RAG LLM, and Clinical Safety Guardrails.
        </p>
      </div>
    </aside>
  );
}
