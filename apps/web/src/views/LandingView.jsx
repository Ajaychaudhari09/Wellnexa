import React from 'react';
import {
  Activity,
  ShieldCheck,
  Sparkles,
  HeartPulse,
  FileSpreadsheet,
  Pill,
  CalendarDays,
  UtensilsCrossed,
  Flame,
  Smile,
  BotMessageSquare,
  Lock,
  ArrowRight,
  CheckCircle,
  Stethoscope,
  TrendingUp,
  Clock,
  ChevronRight,
  Sun,
  Moon
} from 'lucide-react';

export default function LandingView({
  onOpenAuth,
  onQuickDemoPatient,
  onQuickDemoDoctor,
  theme,
  onToggleTheme
}) {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-app)', color: 'var(--text-main)', position: 'relative', overflowX: 'hidden' }}>
      <div className="app-bg-glow" />

      {/* Public Landing Navbar */}
      <nav style={{
        position: 'sticky',
        top: 0,
        zIndex: 60,
        background: 'var(--bg-header)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '14px 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Logo */}
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
          }}>
            <Activity size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-main)' }}>
              WellNexa<span style={{ color: 'var(--primary)' }}>.AI</span>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Unified Healthcare & Wellness
            </span>
          </div>
        </div>

        {/* Center Nav Links (Desktop) */}
        <div className="hide-on-mobile" style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <a href="#features" style={{ color: 'var(--text-muted)', fontSize: '0.88rem', fontWeight: 600, textDecoration: 'none' }}>Features</a>
          <a href="#workflows" style={{ color: 'var(--text-muted)', fontSize: '0.88rem', fontWeight: 600, textDecoration: 'none' }}>Workflow</a>
          <a href="#modules" style={{ color: 'var(--text-muted)', fontSize: '0.88rem', fontWeight: 600, textDecoration: 'none' }}>Modules</a>
          <a href="#security" style={{ color: 'var(--text-muted)', fontSize: '0.88rem', fontWeight: 600, textDecoration: 'none' }}>Privacy & Safety</a>
        </div>

        {/* Right Nav CTAs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Theme Toggle */}
          <button
            onClick={onToggleTheme}
            className="btn-secondary"
            style={{ padding: '8px 12px', borderRadius: '10px' }}
            title={theme === 'dark' ? 'Switch to Day Mode' : 'Switch to Night Mode'}
          >
            {theme === 'dark' ? <Sun size={17} color="#f59e0b" /> : <Moon size={17} color="#6366f1" />}
          </button>

          <button
            onClick={() => onOpenAuth('signin')}
            className="btn-secondary"
            style={{ padding: '8px 18px', fontSize: '0.88rem', fontWeight: 600 }}
          >
            Sign In
          </button>

          <button
            onClick={() => onOpenAuth('signup')}
            className="btn-primary"
            style={{ padding: '8px 20px', fontSize: '0.88rem', fontWeight: 700 }}
          >
            Get Started Free
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '70px 24px 60px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
      }}>
        {/* Pill Badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 16px',
          background: 'var(--mint-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '999px',
          fontSize: '0.82rem',
          fontWeight: 700,
          color: 'var(--primary-deep)',
          marginBottom: '24px',
        }}>
          <Sparkles size={14} color="var(--primary)" />
          <span>AI-POWERED PERSONAL HEALTH ECOSYSTEM · DPDP & HIPAA COMPLIANT</span>
        </div>

        {/* Hero Title */}
        <h1 style={{
          fontSize: 'clamp(2.3rem, 5vw, 3.8rem)',
          fontWeight: 900,
          letterSpacing: '-0.03em',
          lineHeight: 1.15,
          margin: '0 0 20px',
          maxWidth: '960px',
          color: 'var(--text-main)',
        }}>
          One Platform. <br />
          <span style={{
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--aqua) 50%, #38bdf8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Your Complete Health Journey.
          </span>
        </h1>

        {/* Subtitle */}
        <p style={{
          fontSize: 'clamp(1rem, 2vw, 1.25rem)',
          color: 'var(--text-muted)',
          maxWidth: '780px',
          lineHeight: 1.6,
          margin: '0 0 36px',
        }}>
          Stop juggling disconnected fitness apps, lost paper prescriptions, and confusing lab sheets.
          WellNexa AI unifies medical records, OCR lab analysis, medicines, nutrition, fitness, appointments, and mental wellness through one user-controlled health profile.
        </p>

        {/* CTA Button Group */}
        <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', justifyContent: 'center', marginBottom: '40px' }}>
          <button
            onClick={() => onOpenAuth('signup')}
            className="btn-primary"
            style={{ padding: '14px 32px', fontSize: '1rem', fontWeight: 700, borderRadius: 'var(--radius-md)' }}
          >
            Create Your Health Profile <ArrowRight size={18} />
          </button>

          <button
            onClick={() => onOpenAuth('signin')}
            className="btn-secondary"
            style={{ padding: '14px 28px', fontSize: '1rem', fontWeight: 600, borderRadius: 'var(--radius-md)' }}
          >
            Sign In to Existing Account
          </button>
        </div>

        {/* 1-Click Evaluation Bar */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '16px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap',
          boxShadow: 'var(--shadow-card)',
          marginBottom: '50px',
        }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Instant Evaluation Demo:
          </span>
          <button
            onClick={onQuickDemoPatient}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '8px 16px', border: '1px solid var(--primary)', color: 'var(--primary-deep)' }}
          >
            👤 1-Click Patient Sign-In (Bruce Wayne)
          </button>
          <button
            onClick={onQuickDemoDoctor}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '8px 16px', border: '1px solid var(--border-subtle)' }}
          >
            🩺 1-Click Physician Sign-In (Dr. Helen Cho)
          </button>
        </div>

        {/* Trust Badges */}
        <div style={{ display: 'flex', gap: '30px', flexWrap: 'wrap', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle size={16} color="var(--primary)" /> 100% Patient-Controlled Consent
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={16} color="var(--primary)" /> Human-in-the-Loop OCR Verification
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Lock size={16} color="var(--primary)" /> DPDP Act & HIPAA Compliant Architecture
          </div>
        </div>
      </section>

      {/* Problem vs Solution Section */}
      <section id="workflows" style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '60px 24px',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '44px' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 10px', color: 'var(--text-main)' }}>
            Solving Fragmented Healthcare at Its Core
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '640px', margin: '0 auto' }}>
            Modern healthcare is split across dozens of disconnected silos. WellNexa AI bridges every gap into a single continuum of care.
          </p>
        </div>

        <div className="grid-3" style={{ gap: '20px' }}>
          {[
            {
              problem: 'Scattered Records & Lost Paperwork',
              solution: 'Central Personal Health Profile',
              desc: 'Biometrics, allergies, chronic conditions, and lifestyle data organized with chronological timestamps in one secure place.',
              icon: HeartPulse,
              color: 'var(--primary)',
            },
            {
              problem: 'Cryptic Lab Reports & Complex Numbers',
              solution: 'AI & OCR Medical Report Analyzer',
              desc: 'Extract numerical values, highlight normal ranges, explain clinical terms in plain English, and plot multi-year parameter deltas.',
              icon: FileSpreadsheet,
              color: '#0284c7',
            },
            {
              problem: 'Missed Medication & Untracked Refills',
              solution: 'Prescriptions & Dose Adherence',
              desc: 'Structured schedules, automated pill stock monitoring, refill threshold alerts, and verified dose event logs.',
              icon: Pill,
              color: '#10b981',
            },
            {
              problem: 'Fragmented Lifestyle & Sleep Data',
              solution: 'Consolidated Fitness & Habit Tracking',
              desc: 'Sync step counts, active minutes, sleep quality, workout logs, and daily streaks without needing 5 separate apps.',
              icon: Flame,
              color: '#f59e0b',
            },
            {
              problem: 'Inconvenient Calorie & Macro Planning',
              solution: 'Smart AI Nutrition Planner',
              desc: 'Log meals with instant macro summaries, water balance counters, and clinical AI meal plans matched to your vitals.',
              icon: UtensilsCrossed,
              color: '#8b5cf6',
            },
            {
              problem: 'Uncontrolled & Insecure Doctor Sharing',
              solution: 'Time-Bound Physician Access Portal',
              desc: 'Generate temporary (1 hr - 30 days) cryptographic access passes for doctors with an instant kill-switch revocation.',
              icon: Stethoscope,
              color: '#ec4899',
            },
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="glass-card"
                style={{
                  padding: '24px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px',
                  borderTop: `3px solid ${item.color}`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    background: 'var(--mint-surface)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <Icon size={20} color={item.color} />
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#ef4444', fontWeight: 700 }}>
                      Problem: {item.problem}
                    </span>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: '2px 0 0', color: 'var(--text-main)' }}>
                      {item.solution}
                    </h3>
                  </div>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.6 }}>
                  {item.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* 9 Modules Grid Section */}
      <section id="modules" style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '60px 24px',
        background: 'var(--bg-item)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-subtle)',
        marginBottom: '60px',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 10px', color: 'var(--text-main)' }}>
            Complete 9-Module Healthcare Suite
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Built specifically to solve fragmented management through one authorized profile.
          </p>
        </div>

        <div className="grid-3" style={{ gap: '16px' }}>
          {[
            { title: 'Personal Health Profile', desc: 'Vitals, blood pressure, BMI, glucose, and allergy alerts.', icon: HeartPulse },
            { title: 'Medical Report Analyzer', desc: 'OCR laboratory extraction with physiological boundary flags.', icon: FileSpreadsheet },
            { title: 'Prescriptions & Medicines', desc: 'Active doses, stock countdowns, and refill warnings.', icon: Pill },
            { title: 'Clinical Appointments', desc: 'Schedule doctor consultations and launch telehealth visits.', icon: CalendarDays },
            { title: 'AI Nutrition Planner', desc: 'Macronutrient targets, hydration logging, and diet recipes.', icon: UtensilsCrossed },
            { title: 'Fitness & Lifestyle', desc: 'Steps, sleep metrics, workout records, and habit streaks.', icon: Flame },
            { title: 'Mental Wellness & Journal', desc: 'Mood reflections, gratitude notes, and Tele-MANAS guardrails.', icon: Smile },
            { title: 'AI Health Assistant', desc: 'Grounded conversational RAG citing trusted WHO/ICMR guidelines.', icon: BotMessageSquare },
            { title: 'Controlled Doctor Portal', desc: 'Role-appropriate portal with time-bound RBAC clinical passes.', icon: Stethoscope },
          ].map((mod, i) => {
            const Icon = mod.icon;
            return (
              <div
                key={i}
                style={{
                  padding: '18px 20px',
                  background: 'var(--bg-card)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  gap: '14px',
                  alignItems: 'flex-start',
                }}
              >
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  background: 'var(--mint-surface)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <Icon size={18} color="var(--primary)" />
                </div>
                <div>
                  <h4 style={{ margin: '0 0 4px', fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {mod.title}
                  </h4>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {mod.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Security & Clinical Safety Section */}
      <section id="security" style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '40px 24px 80px',
        textAlign: 'center',
      }}>
        <div className="glass-card" style={{
          padding: '40px',
          background: 'linear-gradient(135deg, var(--mint-surface) 0%, var(--bg-card) 100%)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
        }}>
          <ShieldCheck size={36} color="var(--primary)" style={{ marginBottom: '16px' }} />
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: '0 0 12px', color: 'var(--text-main)' }}>
            Clinical Safety & Data Sovereignty First
          </h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: '720px', margin: '0 auto 24px', fontSize: '0.92rem', lineHeight: 1.6 }}>
            WellNexa AI adheres strictly to Digital Personal Data Protection (DPDP) and HIPAA guidelines. AI explanations are transparently labeled as educational and non-diagnostic, accompanied by verified emergency hotlines (Tele-MANAS 14416 / KIRAN 1800-599-0019) and immutable audit trails.
          </p>

          <button
            onClick={() => onOpenAuth('signup')}
            className="btn-primary"
            style={{ padding: '12px 30px', fontSize: '0.95rem', fontWeight: 700 }}
          >
            Join WellNexa AI Today <ArrowRight size={16} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '30px 24px',
        background: 'var(--bg-card)',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
      }}>
        <p style={{ margin: '0 0 6px' }}>
          <strong>WellNexa AI</strong> — An AI-Powered Integrated Personal Healthcare & Wellness Management Platform
        </p>
        <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-faint)' }}>
          © 2026 WellNexa AI. Designed for MCA Capstone Project evaluation. Not an automated medical diagnostic tool.
        </p>
      </footer>
    </div>
  );
}
