import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import DashboardView from './views/DashboardView';
import HealthProfileView from './views/HealthProfileView';
import ReportsView from './views/ReportsView';
import MedicinesView from './views/MedicinesView';
import RemindersView from './views/RemindersView';
import AppointmentsView from './views/AppointmentsView';
import NutritionView from './views/NutritionView';
import FitnessView from './views/FitnessView';
import WellnessView from './views/WellnessView';
import AssistantView from './views/AssistantView';
import SnapshotView from './views/SnapshotView';
import DoctorView from './views/DoctorView';
import PrivacyView from './views/PrivacyView';
import api from './api';
import {
  LayoutDashboard,
  HeartPulse,
  Pill,
  FileSpreadsheet,
  BotMessageSquare
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentRole, setCurrentRole] = useState(localStorage.getItem('wellnexa_role') || 'PATIENT');
  const [currentUser, setCurrentUser] = useState(null);
  const [theme, setTheme] = useState(localStorage.getItem('wellnexa_theme') || 'light');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [initializing, setInitializing] = useState(true);

  // Apply theme to HTML root element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('wellnexa_theme', theme);
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const initAuth = async (roleToUse = currentRole) => {
    try {
      setInitializing(true);
      const email = roleToUse === 'DOCTOR' ? 'doctor@wellnexa.ai' : 'patient@wellnexa.ai';
      await api.login(email, 'Password123!');
      const me = await api.getMe().catch(() => null);
      setCurrentUser(me);
      setCurrentRole(roleToUse);
    } catch (err) {
      console.warn('Auto-login initialization fallback:', err);
    } finally {
      setInitializing(false);
    }
  };

  useEffect(() => {
    initAuth();
  }, []);

  const handleSwitchRole = (newRole) => {
    initAuth(newRole);
  };

  const [subTab, setSubTab] = useState({
    my_health: 'profile',
    meds_reminders: 'medicines',
    wellness: 'nutrition',
    assistant: 'assistant',
  });

  const handleNavigate = (tab, targetSubTab) => {
    if (tab === 'profile' || tab === 'reports') {
      setActiveTab('my_health');
      setSubTab(prev => ({ ...prev, my_health: tab }));
    } else if (tab === 'medicines' || tab === 'reminders') {
      setActiveTab('meds_reminders');
      setSubTab(prev => ({ ...prev, meds_reminders: tab }));
    } else if (tab === 'nutrition' || tab === 'fitness' || tab === 'wellness') {
      setActiveTab('wellness');
      setSubTab(prev => ({ ...prev, wellness: tab }));
    } else if (tab === 'assistant' || tab === 'snapshot') {
      setActiveTab('assistant');
      setSubTab(prev => ({ ...prev, assistant: tab }));
    } else {
      setActiveTab(tab);
      if (targetSubTab) {
        setSubTab(prev => ({ ...prev, [tab]: targetSubTab }));
      }
    }
  };

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView onNavigate={handleNavigate} />;

      case 'my_health':
      case 'profile':
      case 'reports': {
        const currentHealthSub = activeTab === 'profile' ? 'profile' : activeTab === 'reports' ? 'reports' : (subTab.my_health || 'profile');
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <div className="subnav-pill-container">
              <button
                onClick={() => setSubTab(prev => ({ ...prev, my_health: 'profile' }))}
                className={`subnav-pill ${currentHealthSub === 'profile' ? 'active' : ''}`}
              >
                Health Profile & Vitals
              </button>
              <button
                onClick={() => setSubTab(prev => ({ ...prev, my_health: 'reports' }))}
                className={`subnav-pill ${currentHealthSub === 'reports' ? 'active' : ''}`}
              >
                Medical Reports & OCR Analyzer
              </button>
            </div>
            {currentHealthSub === 'profile' ? <HealthProfileView /> : <ReportsView />}
          </div>
        );
      }

      case 'meds_reminders':
      case 'medicines':
      case 'reminders': {
        const currentMedsSub = activeTab === 'medicines' ? 'medicines' : activeTab === 'reminders' ? 'reminders' : (subTab.meds_reminders || 'medicines');
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <div className="subnav-pill-container">
              <button
                onClick={() => setSubTab(prev => ({ ...prev, meds_reminders: 'medicines' }))}
                className={`subnav-pill ${currentMedsSub === 'medicines' ? 'active' : ''}`}
              >
                Prescriptions & Inventory
              </button>
              <button
                onClick={() => setSubTab(prev => ({ ...prev, meds_reminders: 'reminders' }))}
                className={`subnav-pill ${currentMedsSub === 'reminders' ? 'active' : ''}`}
              >
                Smart Health Reminders
              </button>
            </div>
            {currentMedsSub === 'medicines' ? <MedicinesView /> : <RemindersView />}
          </div>
        );
      }

      case 'appointments':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <AppointmentsView />
          </div>
        );

      case 'wellness':
      case 'nutrition':
      case 'fitness': {
        const currentWellnessSub = activeTab === 'nutrition' ? 'nutrition' : activeTab === 'fitness' ? 'fitness' : (subTab.wellness || 'nutrition');
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <div className="subnav-pill-container">
              <button
                onClick={() => setSubTab(prev => ({ ...prev, wellness: 'nutrition' }))}
                className={`subnav-pill ${currentWellnessSub === 'nutrition' ? 'active' : ''}`}
              >
                AI Nutrition Planner
              </button>
              <button
                onClick={() => setSubTab(prev => ({ ...prev, wellness: 'fitness' }))}
                className={`subnav-pill ${currentWellnessSub === 'fitness' ? 'active' : ''}`}
              >
                Fitness & Lifestyle
              </button>
              <button
                onClick={() => setSubTab(prev => ({ ...prev, wellness: 'wellness' }))}
                className={`subnav-pill ${currentWellnessSub === 'wellness' ? 'active' : ''}`}
              >
                Mental Wellness & Journal
              </button>
            </div>
            {currentWellnessSub === 'nutrition' && <NutritionView />}
            {currentWellnessSub === 'fitness' && <FitnessView />}
            {currentWellnessSub === 'wellness' && <WellnessView />}
          </div>
        );
      }

      case 'assistant':
      case 'snapshot': {
        const currentAiSub = activeTab === 'snapshot' ? 'snapshot' : (subTab.assistant || 'assistant');
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <div className="subnav-pill-container">
              <button
                onClick={() => setSubTab(prev => ({ ...prev, assistant: 'assistant' }))}
                className={`subnav-pill ${currentAiSub === 'assistant' ? 'active' : ''}`}
              >
                Clinical AI Consultation
              </button>
              <button
                onClick={() => setSubTab(prev => ({ ...prev, assistant: 'snapshot' }))}
                className={`subnav-pill ${currentAiSub === 'snapshot' ? 'active' : ''}`}
              >
                360° Health Synthesis
              </button>
            </div>
            {currentAiSub === 'assistant' ? <AssistantView /> : <SnapshotView />}
          </div>
        );
      }

      case 'doctor':
        return <DoctorView currentRole={currentRole} />;

      case 'privacy':
        return <PrivacyView />;

      default:
        return <DashboardView onNavigate={handleNavigate} />;
    }
  };

  return (
    <div>
      <div className="app-bg-glow" />
      <Header
        currentRole={currentRole}
        onSwitchRole={handleSwitchRole}
        currentUser={currentUser}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        mobileSidebarOpen={mobileSidebarOpen}
        onToggleMobileSidebar={() => setMobileSidebarOpen(!mobileSidebarOpen)}
        onOpenSnapshot={() => handleNavigate('assistant', 'snapshot')}
        onOpenAssistant={() => handleNavigate('assistant', 'assistant')}
      />

      <div className="app-container">
        <Sidebar
          activeTab={activeTab}
          onSelectTab={handleNavigate}
          currentRole={currentRole}
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() => setMobileSidebarOpen(false)}
        />

        <main className="main-content" style={{ paddingBottom: '70px' }}>
          {initializing ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '65vh',
              gap: '16px',
            }}>
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                border: '3px solid var(--border-subtle)',
                borderTopColor: 'var(--primary)',
                animation: 'spin 0.8s linear infinite',
              }} />
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>
                Connecting to WellNexa Clinical Engine...
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Validating session credentials and synchronizing biometrics
              </div>
            </div>
          ) : (
            renderActiveView()
          )}
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar (Screens <= 768px) */}
      <nav className="mobile-bottom-nav" style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: 'var(--bg-header)',
        backdropFilter: 'blur(16px)',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        padding: '8px 0',
        zIndex: 80,
      }}>
        {[
          { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
          { id: 'profile', label: 'Vitals', icon: HeartPulse },
          { id: 'medicines', label: 'Meds', icon: Pill },
          { id: 'reports', label: 'Labs', icon: FileSpreadsheet },
          { id: 'assistant', label: 'AI Chat', icon: BotMessageSquare },
        ].map((item) => {
          const Icon = item.icon;
          const isActive =
            activeTab === item.id ||
            (item.id === 'profile' && activeTab === 'my_health' && (subTab.my_health === 'profile' || !subTab.my_health)) ||
            (item.id === 'reports' && activeTab === 'my_health' && subTab.my_health === 'reports') ||
            (item.id === 'medicines' && activeTab === 'meds_reminders' && (subTab.meds_reminders === 'medicines' || !subTab.meds_reminders)) ||
            (item.id === 'assistant' && activeTab === 'assistant');
          return (
            <button
              key={item.id}
              onClick={() => handleNavigate(item.id)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '4px',
                background: 'transparent',
                border: 'none',
                color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                fontSize: '0.72rem',
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                padding: '4px 10px',
              }}
            >
              <Icon size={18} color={isActive ? 'var(--primary)' : 'currentColor'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <style>{`
        @media (min-width: 769px) {
          .mobile-bottom-nav { display: none !important; }
        }
        @media (max-width: 768px) {
          .main-content {
            padding-bottom: 80px !important;
          }
        }
      `}</style>
    </div>
  );
}
