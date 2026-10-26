import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LandingView from './views/LandingView';
import AuthModal from './views/AuthModal';
import ProfileView from './views/ProfileView';
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
  BotMessageSquare,
  CalendarDays
} from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentRole, setCurrentRole] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [theme, setTheme] = useState(localStorage.getItem('wellnexa_theme') || 'light');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [initializing, setInitializing] = useState(true);

  // Auth Modal State
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('signin'); // 'signin' or 'signup'

  // Apply theme to HTML root element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('wellnexa_theme', theme);
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Check existing session on boot
  useEffect(() => {
    const checkSession = async () => {
      try {
        setInitializing(true);
        if (api.token) {
          const me = await api.getMe();
          if (me) {
            setCurrentUser(me);
            const isDoc = me.roles && me.roles.some(r => r.toUpperCase().includes('DOCTOR'));
            const role = isDoc ? 'DOCTOR' : (localStorage.getItem('wellnexa_role') || 'PATIENT');
            setCurrentRole(role);
          } else {
            api.setSession(null, null, null);
            setCurrentUser(null);
            setCurrentRole(null);
          }
        } else {
          setCurrentUser(null);
          setCurrentRole(null);
        }
      } catch (err) {
        console.warn('Session check failed, staying on landing page:', err);
        api.setSession(null, null, null);
        setCurrentUser(null);
        setCurrentRole(null);
      } finally {
        setInitializing(false);
      }
    };

    checkSession();

    // Listen for unauthorized 401 events from api.js
    const handleUnauthorized = () => {
      setCurrentUser(null);
      setCurrentRole(null);
      setActiveTab('dashboard');
    };

    window.addEventListener('wellnexa:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('wellnexa:unauthorized', handleUnauthorized);
  }, []);

  // Auth Handlers
  const handleAuthSuccess = (user, role) => {
    setCurrentUser(user);
    setCurrentRole(role || 'PATIENT');
    setActiveTab(role === 'DOCTOR' ? 'doctor' : 'dashboard');
    setShowAuthModal(false);
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } finally {
      setCurrentUser(null);
      setCurrentRole(null);
      setActiveTab('dashboard');
    }
  };

  const handleQuickDemoPatient = async () => {
    try {
      setInitializing(true);
      const res = await api.login('patient@wellnexa.ai', 'Password123!');
      handleAuthSuccess(res.user, 'PATIENT');
    } catch (err) {
      alert('Demo patient sign-in failed: ' + err.message);
    } finally {
      setInitializing(false);
    }
  };

  const handleQuickDemoDoctor = async () => {
    try {
      setInitializing(true);
      const res = await api.login('doctor@wellnexa.ai', 'Password123!');
      handleAuthSuccess(res.user, 'DOCTOR');
    } catch (err) {
      alert('Demo physician sign-in failed: ' + err.message);
    } finally {
      setInitializing(false);
    }
  };

  // Render View by Active Tab
  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView onNavigate={setActiveTab} />;

      case 'profile':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <HealthProfileView />
          </div>
        );

      case 'reports':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <ReportsView />
          </div>
        );

      case 'medicines':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <MedicinesView />
          </div>
        );

      case 'reminders':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <RemindersView />
          </div>
        );

      case 'appointments':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <AppointmentsView />
          </div>
        );

      case 'nutrition':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <NutritionView />
          </div>
        );

      case 'fitness':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <FitnessView />
          </div>
        );

      case 'wellness':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <WellnessView />
          </div>
        );

      case 'assistant':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <AssistantView />
          </div>
        );

      case 'snapshot':
        return (
          <div className="page-wrapper" style={{ paddingTop: '16px' }}>
            <SnapshotView />
          </div>
        );

      case 'doctor':
        return <DoctorView currentRole={currentRole} />;

      case 'privacy':
        return <PrivacyView />;

      case 'profile_account':
        return (
          <ProfileView
            currentUser={currentUser}
            currentRole={currentRole}
            onLogout={handleLogout}
            onNavigate={setActiveTab}
          />
        );

      default:
        return <DashboardView onNavigate={setActiveTab} />;
    }
  };

  // 1. Initial Loading Screen
  if (initializing) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'var(--bg-app)',
        gap: '16px',
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          border: '3px solid var(--border-subtle)',
          borderTopColor: 'var(--primary)',
          animation: 'spin 0.8s linear infinite',
        }} />
        <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
          Connecting to WellNexa Clinical Engine...
        </div>
      </div>
    );
  }

  // 2. Unauthenticated Visitor -> Public Landing Page + Auth Modal
  // STRICT AUTH GUARD: "no one other logged person access any thing"
  if (!currentUser) {
    return (
      <div>
        <LandingView
          onOpenAuth={(mode) => {
            setAuthMode(mode || 'signin');
            setShowAuthModal(true);
          }}
          onQuickDemoPatient={handleQuickDemoPatient}
          onQuickDemoDoctor={handleQuickDemoDoctor}
          theme={theme}
          onToggleTheme={handleToggleTheme}
        />

        <AuthModal
          isOpen={showAuthModal}
          initialMode={authMode}
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      </div>
    );
  }

  // 3. Authenticated User -> Full Integrated Healthcare Application
  return (
    <div>
      <div className="app-bg-glow" />

      {/* Global Authenticated Header (No doctor/patient switch toggle!) */}
      <Header
        currentUser={currentUser}
        currentRole={currentRole}
        onLogout={handleLogout}
        onOpenProfile={() => setActiveTab('profile_account')}
        onOpenPrivacy={() => setActiveTab('privacy')}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        mobileSidebarOpen={mobileSidebarOpen}
        onToggleMobileSidebar={() => setMobileSidebarOpen(!mobileSidebarOpen)}
        onOpenSnapshot={() => setActiveTab('snapshot')}
        onOpenAssistant={() => setActiveTab('assistant')}
        onSearchSelect={(tabId) => setActiveTab(tabId)}
      />

      <div className="app-container">
        {/* Direct, Categorized Sidebar Navigation */}
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          currentRole={currentRole}
          currentUser={currentUser}
          onLogout={handleLogout}
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() => setMobileSidebarOpen(false)}
        />

        <main className="main-content" style={{ paddingBottom: '70px' }}>
          {renderActiveView()}
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar */}
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
          { id: 'appointments', label: 'Visits', icon: CalendarDays },
          { id: 'reports', label: 'Labs', icon: FileSpreadsheet },
          { id: 'assistant', label: 'AI Chat', icon: BotMessageSquare },
        ].map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
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
                padding: '4px 8px',
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
