import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import DashboardView from './views/DashboardView';
import HealthProfileView from './views/HealthProfileView';
import ReportsView from './views/ReportsView';
import MedicinesView from './views/MedicinesView';
import RemindersView from './views/RemindersView';
import NutritionView from './views/NutritionView';
import FitnessView from './views/FitnessView';
import WellnessView from './views/WellnessView';
import AssistantView from './views/AssistantView';
import SnapshotView from './views/SnapshotView';
import DoctorView from './views/DoctorView';
import PrivacyView from './views/PrivacyView';
import api from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentRole, setCurrentRole] = useState(localStorage.getItem('wellnexa_role') || 'PATIENT');
  const [currentUser, setCurrentUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

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

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView onNavigate={(tab) => setActiveTab(tab)} />;
      case 'profile':
        return <HealthProfileView />;
      case 'reports':
        return <ReportsView />;
      case 'medicines':
        return <MedicinesView />;
      case 'reminders':
        return <RemindersView />;
      case 'nutrition':
        return <NutritionView />;
      case 'fitness':
        return <FitnessView />;
      case 'wellness':
        return <WellnessView />;
      case 'assistant':
        return <AssistantView />;
      case 'snapshot':
        return <SnapshotView />;
      case 'doctor':
        return <DoctorView currentRole={currentRole} />;
      case 'privacy':
        return <PrivacyView />;
      default:
        return <DashboardView onNavigate={(tab) => setActiveTab(tab)} />;
    }
  };

  return (
    <div>
      <div className="app-bg-glow" />
      <Header
        currentRole={currentRole}
        onSwitchRole={handleSwitchRole}
        currentUser={currentUser}
        onOpenSnapshot={() => setActiveTab('snapshot')}
        onOpenAssistant={() => setActiveTab('assistant')}
      />

      <div className="app-container">
        <Sidebar
          activeTab={activeTab}
          onSelectTab={(tab) => setActiveTab(tab)}
          currentRole={currentRole}
        />

        <main className="main-content">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}
