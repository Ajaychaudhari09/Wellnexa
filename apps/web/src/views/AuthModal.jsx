import React, { useState } from 'react';
import {
  Activity,
  Lock,
  Mail,
  User,
  AlertCircle,
  CheckCircle,
  Eye,
  EyeOff,
  X,
  Stethoscope,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import api from '../api';

export default function AuthModal({
  isOpen,
  initialMode = 'signin',
  onClose,
  onAuthSuccess
}) {
  if (!isOpen) return null;

  const [mode, setMode] = useState(initialMode); // 'signin' or 'signup'
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Sign In Form
  const [signInForm, setSignInForm] = useState({
    email: '',
    password: '',
  });

  // Sign Up Form
  const [signUpForm, setSignUpForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
    role: 'PATIENT',
    agree_terms: true,
  });

  const handleSignInSubmit = async (e) => {
    if (e) e.preventDefault();
    setErrorMsg('');

    if (!signInForm.email || !signInForm.password) {
      setErrorMsg('Please enter both your email and password.');
      return;
    }

    try {
      setLoading(true);
      const res = await api.login(signInForm.email, signInForm.password);
      if (onAuthSuccess) {
        onAuthSuccess(res.user, res.role);
      }
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUpSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    // Client-side validations
    if (!signUpForm.first_name.trim() || !signUpForm.last_name.trim()) {
      setErrorMsg('Please enter your full first and last name.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(signUpForm.email)) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }

    if (signUpForm.password.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }

    if (signUpForm.password !== signUpForm.confirm_password) {
      setErrorMsg('Passwords do not match. Please re-enter.');
      return;
    }

    if (!signUpForm.agree_terms) {
      setErrorMsg('Please agree to the health data privacy terms to create an account.');
      return;
    }

    try {
      setLoading(true);
      const res = await api.register({
        email: signUpForm.email,
        password: signUpForm.password,
        first_name: signUpForm.first_name,
        last_name: signUpForm.last_name,
        role: signUpForm.role,
      });

      if (onAuthSuccess) {
        onAuthSuccess(res.user, res.role);
      }
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSignIn = async (email, password) => {
    setErrorMsg('');
    setSignInForm({ email, password });
    try {
      setLoading(true);
      const res = await api.login(email, password);
      if (onAuthSuccess) {
        onAuthSuccess(res.user, res.role);
      }
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Demo login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" style={{ zIndex: 120 }}>
      <div className="glass-card modal-card" style={{ maxWidth: '480px', width: '92%', padding: '32px 28px', position: 'relative' }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '4px',
          }}
          aria-label="Close modal"
        >
          <X size={20} />
        </button>

        {/* Brand Icon & Title */}
        <div style={{ textAlign: 'center', marginBottom: '22px' }}>
          <div style={{
            width: '46px',
            height: '46px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--aqua) 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px var(--primary-glow)',
            marginBottom: '12px',
          }}>
            <Activity size={24} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, margin: '0 0 6px', color: 'var(--text-main)' }}>
            {mode === 'signin' ? 'Sign In to WellNexa AI' : 'Create Your Health Profile'}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>
            {mode === 'signin'
              ? 'Access your centralized medical records, vitals & wellness tracker'
              : 'Join the unified personal healthcare platform today'}
          </p>
        </div>

        {/* Tab Switcher: Sign In vs Sign Up */}
        <div style={{
          display: 'flex',
          background: 'var(--bg-item)',
          borderRadius: 'var(--radius-md)',
          padding: '4px',
          marginBottom: '20px',
        }}>
          <button
            type="button"
            onClick={() => { setMode('signin'); setErrorMsg(''); }}
            style={{
              flex: 1,
              padding: '9px',
              borderRadius: '8px',
              border: 'none',
              background: mode === 'signin' ? 'var(--primary)' : 'transparent',
              color: mode === 'signin' ? '#ffffff' : 'var(--text-muted)',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setMode('signup'); setErrorMsg(''); }}
            style={{
              flex: 1,
              padding: '9px',
              borderRadius: '8px',
              border: 'none',
              background: mode === 'signup' ? 'var(--primary)' : 'transparent',
              color: mode === 'signup' ? '#ffffff' : 'var(--text-muted)',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            Create Account
          </button>
        </div>

        {/* Error Alert Banner */}
        {errorMsg && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 14px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-sm)',
            color: '#ef4444',
            fontSize: '0.82rem',
            marginBottom: '16px',
          }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Mode: Sign In Form */}
        {mode === 'signin' ? (
          <form onSubmit={handleSignInSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label className="input-label">Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '13px' }} />
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  className="input-field"
                  style={{ paddingLeft: '38px' }}
                  value={signInForm.email}
                  onChange={(e) => setSignInForm({ ...signInForm, email: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="input-label">Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '13px' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="••••••••"
                  className="input-field"
                  style={{ paddingLeft: '38px', paddingRight: '38px' }}
                  value={signInForm.password}
                  onChange={(e) => setSignInForm({ ...signInForm, password: e.target.value })}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '11px',
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                  }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
              style={{ width: '100%', padding: '12px', marginTop: '6px', fontSize: '0.95rem' }}
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>

            {/* Quick 1-Click Evaluation Accounts */}
            <div style={{ marginTop: '16px', borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, display: 'block', marginBottom: '8px', textAlign: 'center' }}>
                PROJECT EVALUATION QUICK ACCESS:
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  onClick={() => handleDemoSignIn('patient@wellnexa.ai', 'Password123!')}
                  className="btn-secondary"
                  style={{ flex: 1, fontSize: '0.78rem', padding: '8px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                >
                  <User size={13} color="var(--primary)" /> Demo Patient
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoSignIn('doctor@wellnexa.ai', 'Password123!')}
                  className="btn-secondary"
                  style={{ flex: 1, fontSize: '0.78rem', padding: '8px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                >
                  <Stethoscope size={13} color="#8b5cf6" /> Demo Physician
                </button>
              </div>
            </div>
          </form>
        ) : (
          /* Mode: Sign Up Form */
          <form onSubmit={handleSignUpSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', gap: '10px' }}>
              <div style={{ flex: 1 }}>
                <label className="input-label">First Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Bruce"
                  className="input-field"
                  value={signUpForm.first_name}
                  onChange={(e) => setSignUpForm({ ...signUpForm, first_name: e.target.value })}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label className="input-label">Last Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Wayne"
                  className="input-field"
                  value={signUpForm.last_name}
                  onChange={(e) => setSignUpForm({ ...signUpForm, last_name: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="input-label">Email Address</label>
              <input
                type="email"
                required
                placeholder="name@example.com"
                className="input-field"
                value={signUpForm.email}
                onChange={(e) => setSignUpForm({ ...signUpForm, email: e.target.value })}
              />
            </div>

            <div>
              <label className="input-label">Account Role</label>
              <select
                className="input-field"
                value={signUpForm.role}
                onChange={(e) => setSignUpForm({ ...signUpForm, role: e.target.value })}
              >
                <option value="PATIENT">Patient / Individual Health Manager</option>
                <option value="DOCTOR">Healthcare Professional / Physician</option>
              </select>
            </div>

            <div>
              <label className="input-label">Password (min 8 characters)</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                className="input-field"
                value={signUpForm.password}
                onChange={(e) => setSignUpForm({ ...signUpForm, password: e.target.value })}
              />
            </div>

            <div>
              <label className="input-label">Confirm Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                className="input-field"
                value={signUpForm.confirm_password}
                onChange={(e) => setSignUpForm({ ...signUpForm, confirm_password: e.target.value })}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <input
                type="checkbox"
                id="agree_terms"
                checked={signUpForm.agree_terms}
                onChange={(e) => setSignUpForm({ ...signUpForm, agree_terms: e.target.checked })}
                style={{ accentColor: 'var(--primary)', cursor: 'pointer' }}
              />
              <label htmlFor="agree_terms" style={{ fontSize: '0.78rem', color: 'var(--text-muted)', cursor: 'pointer' }}>
                I agree to the DPDP / HIPAA health data privacy terms.
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
              style={{ width: '100%', padding: '12px', marginTop: '8px', fontSize: '0.95rem' }}
            >
              {loading ? 'Creating Profile...' : 'Complete Registration'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
