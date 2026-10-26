import React, { useState, useRef, useEffect } from 'react';
import {
  Activity,
  User,
  Sparkles,
  Sun,
  Moon,
  Menu,
  X,
  Bell,
  CheckCircle2,
  Clock,
  ShieldCheck,
  LogOut,
  Search,
  ChevronDown,
  Stethoscope,
  HeartPulse,
  Pill,
  CalendarDays,
  FileSpreadsheet
} from 'lucide-react';

const SEARCHABLE_MODULES = [
  { id: 'dashboard', label: 'Overview Dashboard', category: 'General' },
  { id: 'profile', label: 'Health Profile & Vitals', category: 'My Health' },
  { id: 'reports', label: 'Medical Lab Reports & OCR', category: 'My Health' },
  { id: 'medicines', label: 'Medicines & Inventory', category: 'Prescriptions' },
  { id: 'reminders', label: 'Smart Health Reminders', category: 'Prescriptions' },
  { id: 'appointments', label: 'Clinical Appointments & Telehealth', category: 'Visits' },
  { id: 'nutrition', label: 'AI Nutrition & Meal Planner', category: 'Wellness' },
  { id: 'fitness', label: 'Fitness & Lifestyle Tracking', category: 'Wellness' },
  { id: 'wellness', label: 'Mental Wellness & Mood Journal', category: 'Wellness' },
  { id: 'assistant', label: 'Grounded AI Health Assistant', category: 'AI Tools' },
  { id: 'snapshot', label: '360° Health Synthesis', category: 'AI Tools' },
  { id: 'privacy', label: 'Consent & Privacy Center', category: 'Security' },
  { id: 'doctor', label: 'Physician Review Portal', category: 'Clinical', doctorOnly: true },
];

export default function Header({
  currentUser,
  currentRole,
  onLogout,
  onOpenProfile,
  onOpenPrivacy,
  theme,
  onToggleTheme,
  mobileSidebarOpen,
  onToggleMobileSidebar,
  onOpenSnapshot,
  onOpenAssistant,
  onSearchSelect
}) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);

  const searchRef = useRef(null);
  const userMenuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSearchDropdown(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const notifications = [
    { id: 1, title: 'Medication Due', desc: 'Take Metformin (500mg) at 08:30 AM', time: '10m ago', icon: Clock },
    { id: 2, title: 'Lab Results Verified', desc: 'Annual Lipid Profile 2026 is confirmed', time: '1h ago', icon: CheckCircle2 },
    { id: 3, title: 'Clinical Review Ready', desc: 'Consultation notes updated by physician', time: '3h ago', icon: ShieldCheck },
  ];

  const filteredModules = SEARCHABLE_MODULES.filter(m => {
    if (m.doctorOnly && currentRole !== 'DOCTOR') return false;
    return m.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
           m.category.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const userName = currentUser
    ? `${currentUser.first_name || 'Health'} ${currentUser.last_name || 'User'}`
    : currentRole === 'DOCTOR' ? 'Dr. Helen Cho' : 'Bruce Wayne';

  const userInitials = currentUser?.first_name
    ? `${currentUser.first_name[0]}${currentUser.last_name ? currentUser.last_name[0] : ''}`
    : currentRole === 'DOCTOR' ? 'HC' : 'BW';

  const userEmail = currentUser?.email || (currentRole === 'DOCTOR' ? 'doctor@wellnexa.ai' : 'patient@wellnexa.ai');

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
      gap: '16px',
    }}>
      {/* Left: Mobile Menu Toggle + Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexShrink: 0 }}>
        {/* Mobile Hamburger */}
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
                CONNECTED
              </span>
            </div>
            <p className="header-subtitle" style={{ fontSize: '0.74rem', color: 'var(--text-muted)', margin: 0 }}>
              One Platform. Your Complete Health Journey.
            </p>
          </div>
        </div>
      </div>

      {/* Center: Global Feature Quick-Search / Jump Bar (Desktop) */}
      <div ref={searchRef} className="hide-on-mobile" style={{ flex: 1, maxWidth: '420px', position: 'relative' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'var(--bg-item)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '7px 12px',
        }}>
          <Search size={15} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search features (reports, meds, vitals)..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setShowSearchDropdown(true);
            }}
            onFocus={() => setShowSearchDropdown(true)}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: '0.82rem',
              color: 'var(--text-main)',
              width: '100%',
            }}
          />
        </div>

        {/* Search Results Dropdown */}
        {showSearchDropdown && (
          <div style={{
            position: 'absolute',
            top: '42px',
            left: 0,
            right: 0,
            background: 'var(--bg-card)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-dropdown)',
            padding: '8px',
            zIndex: 110,
            maxHeight: '280px',
            overflowY: 'auto',
          }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-faint)', fontWeight: 700, padding: '4px 8px', display: 'block', textTransform: 'uppercase' }}>
              Jump to Feature
            </span>
            {filteredModules.length === 0 ? (
              <div style={{ padding: '8px 12px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                No features found matching "{searchQuery}"
              </div>
            ) : (
              filteredModules.map((m) => (
                <div
                  key={m.id}
                  onClick={() => {
                    if (onSearchSelect) onSearchSelect(m.id);
                    setShowSearchDropdown(false);
                    setSearchQuery('');
                  }}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    fontSize: '0.84rem',
                    color: 'var(--text-main)',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-item)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <span style={{ fontWeight: 600 }}>{m.label}</span>
                  <span className="badge badge-normal" style={{ fontSize: '0.65rem' }}>{m.category}</span>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Right: Quick actions, Theme toggle, Notifications, User profile dropdown */}
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
          }}
          title={theme === 'dark' ? 'Switch to Day Mode (Light)' : 'Switch to Night Mode (Dark)'}
          aria-label="Toggle Theme"
        >
          {theme === 'dark' ? <Sun size={18} color="#f59e0b" /> : <Moon size={18} color="#6366f1" />}
        </button>

        {/* Notification Bell */}
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
                      <Icon size={16} color="var(--primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
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

        {/* User Profile Menu (Replaces the doctor/patient toggle!) */}
        <div ref={userMenuRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'var(--bg-item)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '4px 10px 4px 6px',
              cursor: 'pointer',
            }}
          >
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: currentRole === 'DOCTOR' ? '#8b5cf6' : 'var(--primary)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.78rem',
            }}>
              {userInitials}
            </div>

            <div className="hide-on-mobile" style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', lineHeight: 1.2 }}>
                {userName}
              </div>
              <span style={{ fontSize: '0.68rem', color: currentRole === 'DOCTOR' ? '#8b5cf6' : 'var(--primary-deep)', fontWeight: 600 }}>
                {currentRole === 'DOCTOR' ? 'Physician' : 'Patient'}
              </span>
            </div>

            <ChevronDown size={14} color="var(--text-muted)" />
          </button>

          {/* User Menu Dropdown */}
          {showUserMenu && (
            <div style={{
              position: 'absolute',
              right: 0,
              top: '46px',
              width: '230px',
              background: 'var(--bg-card)',
              backdropFilter: 'blur(16px)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-dropdown)',
              padding: '10px 8px',
              zIndex: 100,
            }}>
              <div style={{ padding: '6px 10px 10px', borderBottom: '1px solid var(--border-subtle)', marginBottom: '6px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>{userName}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{userEmail}</div>
              </div>

              <button
                onClick={() => {
                  setShowUserMenu(false);
                  if (onOpenProfile) onOpenProfile();
                }}
                className="btn-secondary"
                style={{
                  width: '100%',
                  textAlign: 'left',
                  justifyContent: 'flex-start',
                  border: 'none',
                  padding: '8px 10px',
                  fontSize: '0.82rem',
                }}
              >
                <User size={15} color="var(--primary)" />
                <span>My Profile & Account</span>
              </button>

              <button
                onClick={() => {
                  setShowUserMenu(false);
                  if (onOpenPrivacy) onOpenPrivacy();
                }}
                className="btn-secondary"
                style={{
                  width: '100%',
                  textAlign: 'left',
                  justifyContent: 'flex-start',
                  border: 'none',
                  padding: '8px 10px',
                  fontSize: '0.82rem',
                }}
              >
                <ShieldCheck size={15} color="#10b981" />
                <span>Privacy & Consent</span>
              </button>

              <div style={{ borderTop: '1px solid var(--border-subtle)', margin: '6px 0' }} />

              <button
                onClick={() => {
                  setShowUserMenu(false);
                  if (onLogout) onLogout();
                }}
                className="btn-danger"
                style={{
                  width: '100%',
                  textAlign: 'left',
                  justifyContent: 'flex-start',
                  padding: '8px 10px',
                  fontSize: '0.82rem',
                }}
              >
                <LogOut size={15} />
                <span>Log Out of Session</span>
              </button>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @media (min-width: 1025px) {
          .mobile-menu-btn { display: none !important; }
        }
        @media (max-width: 860px) {
          .hide-on-mobile { display: none !important; }
          .header-subtitle { display: none !important; }
        }
      `}</style>
    </header>
  );
}
