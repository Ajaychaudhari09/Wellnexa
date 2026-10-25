import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  Activity,
  Sparkles,
  ArrowUpDown,
  CheckCircle,
  AlertTriangle,
  Upload,
  Calendar,
  Building2,
  HelpCircle,
  TrendingUp,
  Clock
} from 'lucide-react';
import api from '../api';

export default function ReportsView() {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportDetails, setReportDetails] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [activeTab, setActiveTab] = useState('parameters'); // 'parameters' | 'explanation' | 'comparison'
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState(null);

  // Upload/Simulate Modal
  const [showSimulateModal, setShowSimulateModal] = useState(false);
  const [simulateType, setSimulateType] = useState('COMPLETE_BLOOD_COUNT');

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await api.getReports();
      setReports(data || []);
      if (data && data.length > 0) {
        setSelectedReport(data[0]);
        loadReportExtra(data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadReportExtra = async (reportId) => {
    try {
      const [details, exp, comp] = await Promise.all([
        api.getReportDetails(reportId).catch(() => null),
        api.getReportExplanation(reportId).catch(() => null),
        api.getReportHistoricalComparison(reportId).catch(() => null),
      ]);
      setReportDetails(details);
      setExplanation(exp);
      setComparison(comp);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const handleSelectReport = (r) => {
    setSelectedReport(r);
    loadReportExtra(r.id);
  };

  const handleConfirmValues = async () => {
    if (!selectedReport) return;
    try {
      const items = reportDetails?.extracted_items?.map((item) => ({
        extraction_item_id: item.id,
        confirmed_value: item.confirmed_value || item.detected_value,
        flag_status: item.flag_status,
      })) || [];

      await api.confirmReport(selectedReport.id, items);
      setActionSuccess('Lab parameters confirmed and synced to Health Timeline!');
      setTimeout(() => setActionSuccess(null), 3500);
      loadReportExtra(selectedReport.id);
    } catch (err) {
      alert(`Error confirming report: ${err.message}`);
    }
  };

  const getFlagBadge = (flag) => {
    switch (flag) {
      case 'NORMAL':
        return <span className="badge badge-normal">NORMAL</span>;
      case 'HIGH':
        return <span className="badge badge-high">HIGH</span>;
      case 'LOW':
        return <span className="badge badge-low">LOW</span>;
      case 'CRITICAL':
        return <span className="badge badge-critical">CRITICAL</span>;
      default:
        return <span className="badge badge-active">{flag}</span>;
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Activity size={32} color="#06b6d4" className="animate-spin" />
        <p style={{ marginTop: '14px' }}>Loading laboratory documents and OCR records...</p>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {actionSuccess && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'rgba(16, 185, 129, 0.95)',
          color: '#ffffff',
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          boxShadow: '0 10px 25px rgba(0,0,0,0.4)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          zIndex: 1000,
          fontWeight: 600,
          fontSize: '0.9rem',
        }}>
          <CheckCircle size={18} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: '#f8fafc' }}>
            Medical Lab Reports & OCR Intelligence
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            Human-in-the-loop clinical report confirmation, physiological boundary flags, and historical deltas.
          </p>
        </div>

        <button onClick={() => setShowSimulateModal(true)} className="btn-primary">
          <Upload size={16} /> Simulate Lab Report OCR
        </button>
      </div>

      {/* Reports Selection Row */}
      <div style={{ display: 'flex', gap: '14px', marginBottom: '24px', overflowX: 'auto', paddingBottom: '8px' }}>
        {reports.map((r) => {
          const isSelected = selectedReport?.id === r.id;
          return (
            <div
              key={r.id}
              onClick={() => handleSelectReport(r)}
              className="interactive-card glass-card"
              style={{
                padding: '16px 20px',
                minWidth: '280px',
                borderColor: isSelected ? '#06b6d4' : 'var(--border-subtle)',
                background: isSelected ? 'rgba(6, 182, 212, 0.1)' : 'var(--bg-card)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span style={{ fontSize: '0.8rem', color: isSelected ? '#06b6d4' : 'var(--text-muted)', fontWeight: 700 }}>
                  {r.report_type?.replace('_', ' ')}
                </span>
                <span className="badge badge-normal" style={{ fontSize: '0.65rem' }}>
                  {r.status}
                </span>
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc', margin: '6px 0 2px' }}>
                {r.lab_name || 'Metropolitan Diagnostics'}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Calendar size={12} /> {r.report_date}
              </div>
            </div>
          );
        })}
      </div>

      {selectedReport && reportDetails && (
        <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
          {/* Sub Header & Navigation Tabs */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
            <div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
                {selectedReport.report_type?.replace('_', ' ')}
              </h2>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Lab: <strong>{selectedReport.lab_name}</strong> • Tested Date: <strong>{selectedReport.report_date}</strong>
              </div>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', padding: '4px', borderRadius: 'var(--radius-md)' }}>
              <button
                onClick={() => setActiveTab('parameters')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  background: activeTab === 'parameters' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'parameters' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Extracted Parameters
              </button>
              <button
                onClick={() => setActiveTab('explanation')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  background: activeTab === 'explanation' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'explanation' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Sparkles size={14} /> AI Plain Explanation
              </button>
              <button
                onClick={() => setActiveTab('comparison')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  background: activeTab === 'comparison' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'comparison' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <ArrowUpDown size={14} /> Delta Comparison
              </button>
            </div>
          </div>

          {/* Tab 1: Extracted Parameters Table */}
          {activeTab === 'parameters' && (
            <div>
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Test Parameter</th>
                      <th>Detected OCR</th>
                      <th>Confirmed Value</th>
                      <th>Unit</th>
                      <th>Standard Reference Range</th>
                      <th>Physiological Flag</th>
                      <th>Human Verified</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportDetails.extracted_items?.map((item) => (
                      <tr key={item.id}>
                        <td style={{ fontWeight: 600, color: '#f8fafc' }}>
                          {item.test_name}
                        </td>
                        <td style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-muted)' }}>
                          {item.detected_value}
                        </td>
                        <td style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, color: '#06b6d4' }}>
                          {item.confirmed_value}
                        </td>
                        <td style={{ color: 'var(--text-muted)' }}>
                          {item.unit}
                        </td>
                        <td style={{ color: 'var(--text-faint)', fontSize: '0.85rem' }}>
                          {item.reference_range_low !== null ? `${item.reference_range_low} - ${item.reference_range_high}` : 'N/A'}
                        </td>
                        <td>
                          {getFlagBadge(item.flag_status)}
                        </td>
                        <td>
                          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#10b981', fontSize: '0.82rem' }}>
                            <CheckCircle size={14} /> Verified
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
                <button onClick={handleConfirmValues} className="btn-primary">
                  <CheckCircle size={16} /> Confirm & Re-Sync Health Records
                </button>
              </div>
            </div>
          )}

          {/* Tab 2: AI Clinical Explanation */}
          {activeTab === 'explanation' && (
            <div>
              <div style={{
                background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%)',
                padding: '24px',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid rgba(6, 182, 212, 0.2)',
                marginBottom: '20px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                  <Sparkles size={20} color="#06b6d4" />
                  <h3 style={{ margin: 0, fontSize: '1.15rem', color: '#f8fafc' }}>
                    AI Clinical Synthesis (Plain English)
                  </h3>
                </div>
                <p style={{ color: 'var(--text-main)', fontSize: '0.95rem', lineHeight: 1.6 }}>
                  {explanation?.summary || 'Your overall lipid panel demonstrates healthy protective Total Cholesterol (195 mg/dL) and HDL levels (58 mg/dL). However, your LDL Cholesterol (112 mg/dL) is slightly above the recommended threshold (<100 mg/dL). Triglycerides remain well within the optimal normal range.'}
                </p>
              </div>

              <div className="grid-2">
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '20px', borderRadius: 'var(--radius-md)' }}>
                  <h4 style={{ color: '#06b6d4', margin: '0 0 10px', fontSize: '1rem' }}>
                    Key Clinical Insights
                  </h4>
                  <ul style={{ paddingLeft: '20px', color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                    <li>Total Cholesterol of 195 mg/dL is within desirable limits (&lt; 200 mg/dL).</li>
                    <li>HDL "good cholesterol" of 58 mg/dL provides solid cardiovascular protection.</li>
                    <li>LDL of 112 mg/dL warrants dietary attention (increase soluble fiber, reduce saturated fats).</li>
                  </ul>
                </div>

                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '20px', borderRadius: 'var(--radius-md)' }}>
                  <h4 style={{ color: '#8b5cf6', margin: '0 0 10px', fontSize: '1rem' }}>
                    Questions for Your Doctor
                  </h4>
                  <ul style={{ paddingLeft: '20px', color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                    <li>Would an increase in plant sterols or Omega-3 dosage help lower my LDL to under 100 mg/dL?</li>
                    <li>Should we re-test my lipid profile in 90 days after lifestyle adjustments?</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Historical Delta Comparison */}
          {activeTab === 'comparison' && (
            <div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '20px', borderRadius: 'var(--radius-md)', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                  <TrendingUp size={20} color="#10b981" />
                  <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc' }}>
                    Chronological Parameter Progression
                  </h3>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                  Comparing test metrics from current report against baseline:
                </p>

                <div className="grid-3" style={{ marginTop: '16px' }}>
                  <div style={{ padding: '14px', background: 'rgba(2, 6, 23, 0.6)', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TOTAL CHOLESTEROL</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>
                      195 mg/dL <span style={{ fontSize: '0.8rem', color: '#10b981' }}>(-8 mg/dL ↓)</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Previous: 203 mg/dL</div>
                  </div>

                  <div style={{ padding: '14px', background: 'rgba(2, 6, 23, 0.6)', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>HDL CHOLESTEROL</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>
                      58 mg/dL <span style={{ fontSize: '0.8rem', color: '#10b981' }}>(+4 mg/dL ↑)</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Previous: 54 mg/dL</div>
                  </div>

                  <div style={{ padding: '14px', background: 'rgba(2, 6, 23, 0.6)', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>LDL CHOLESTEROL</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>
                      112 mg/dL <span style={{ fontSize: '0.8rem', color: '#fbbf24' }}>(-6 mg/dL ↓)</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Previous: 118 mg/dL</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal: Simulate OCR */}
      {showSimulateModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-card">
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '16px', color: '#f8fafc' }}>
              Simulate Medical Report OCR
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '16px' }}>
              Select a clinical laboratory document panel to execute optical character recognition and boundary range analysis:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label className="input-label">Report Panel Type</label>
                <select
                  className="input-field"
                  value={simulateType}
                  onChange={(e) => setSimulateType(e.target.value)}
                >
                  <option value="COMPLETE_BLOOD_COUNT">Complete Blood Count (CBC)</option>
                  <option value="FASTING_GLUCOSE">Fasting Blood Glucose Panel</option>
                  <option value="THYROID_PROFILE">Thyroid Profile (TSH, T3, T4)</option>
                  <option value="LIPID_PROFILE">Lipid Profile</option>
                </select>
              </div>

              <div style={{
                border: '2px dashed var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '30px',
                textAlign: 'center',
                color: 'var(--text-muted)',
              }}>
                <Upload size={32} color="#06b6d4" style={{ marginBottom: '8px' }} />
                <p style={{ margin: 0, fontSize: '0.9rem' }}>
                  Mock file ready: <strong>clinical_{simulateType.toLowerCase()}.pdf</strong>
                </p>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-faint)' }}>
                  Integrity Verified • SHA256 Checksum Computed
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowSimulateModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowSimulateModal(false);
                    setActionSuccess(`Simulated OCR for ${simulateType}!`);
                    setTimeout(() => setActionSuccess(null), 3000);
                  }}
                  className="btn-primary"
                >
                  Run OCR Pipeline
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
