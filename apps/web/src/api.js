// WellNexa AI API Service Client
const API_BASE = '/api/v1';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('wellnexa_token') || null;
    this.currentRole = localStorage.getItem('wellnexa_role') || 'PATIENT';
  }

  setToken(token, role = 'PATIENT') {
    this.token = token;
    this.currentRole = role;
    if (token) {
      localStorage.setItem('wellnexa_token', token);
      localStorage.setItem('wellnexa_role', role);
    } else {
      localStorage.removeItem('wellnexa_token');
      localStorage.removeItem('wellnexa_role');
    }
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      const json = await response.json().catch(() => null);

      if (!response.ok) {
        // If 401 Unauthorized, token is expired or invalid - silently renew and retry once
        if (response.status === 401 && !options._retry && endpoint !== '/auth/login') {
          console.warn('[WellNexa API] Token expired or invalid, renewing session...');
          try {
            const currentRole = localStorage.getItem('wellnexa_role') || 'PATIENT';
            const email = currentRole === 'DOCTOR' ? 'doctor@wellnexa.ai' : 'patient@wellnexa.ai';
            const loginRes = await fetch(`${API_BASE}/auth/login`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password: 'Password123!' }),
            });
            const loginJson = await loginRes.json();
            const newToken = loginJson?.data?.access_token || loginJson?.access_token;
            if (newToken) {
              this.setToken(newToken, currentRole);
              return this.request(endpoint, { ...options, _retry: true });
            }
          } catch (renewErr) {
            console.error('[WellNexa API] Automatic session renewal failed:', renewErr);
          }
        }

        const errorMsg = json?.message || json?.detail || `API Error: ${response.statusText}`;
        throw new Error(errorMsg);
      }

      return json?.data !== undefined ? json.data : json;
    } catch (err) {
      console.error(`[WellNexa API Request Failed] ${endpoint}:`, err);
      throw err;
    }
  }

  // Auth
  async login(email = 'patient@wellnexa.ai', password = 'Password123!') {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    const role = email.includes('doctor') ? 'DOCTOR' : 'PATIENT';
    this.setToken(data.access_token, role);
    return data;
  }

  async getMe() {
    return this.request('/auth/me');
  }

  // Dashboard
  async getHomeDashboard() {
    return this.request('/dashboard/home');
  }

  // Health Profile & Biometrics
  async getHealthProfile() {
    return this.request('/health/profile');
  }

  async getLatestMetrics() {
    return this.request('/health/metrics/latest');
  }

  async addHealthMetric(metric) {
    return this.request('/health/metrics', {
      method: 'POST',
      body: JSON.stringify(metric),
    });
  }

  async getAllergies() {
    return this.request('/health/allergies');
  }

  async addAllergy(allergy) {
    return this.request('/health/allergies', {
      method: 'POST',
      body: JSON.stringify(allergy),
    });
  }

  async getConditions() {
    return this.request('/health/conditions');
  }

  async getGoals() {
    return this.request('/health/goals');
  }

  async addGoal(goal) {
    return this.request('/health/goals', {
      method: 'POST',
      body: JSON.stringify(goal),
    });
  }

  // Health Timeline
  async getTimeline() {
    return this.request('/timeline');
  }

  // Medical Reports & OCR
  async getReports() {
    return this.request('/reports');
  }

  async getReportDetails(id) {
    return this.request(`/reports/${id}`);
  }

  async getReportExplanation(id) {
    return this.request(`/reports/${id}/explanation`);
  }

  async getReportHistoricalComparison(id) {
    return this.request(`/reports/${id}/compare`);
  }

  async confirmReport(id, items) {
    return this.request(`/reports/${id}/confirm`, {
      method: 'POST',
      body: JSON.stringify({ items }),
    });
  }

  // Medicines & Adherence
  async getMedicines() {
    return this.request('/medicines');
  }

  async addMedicine(medicine) {
    return this.request('/medicines', {
      method: 'POST',
      body: JSON.stringify(medicine),
    });
  }

  async logDose(medicineId, status = 'TAKEN', notes = null) {
    return this.request(`/medicines/${medicineId}/log-dose`, {
      method: 'POST',
      body: JSON.stringify({ status, notes }),
    });
  }

  async getAdherenceScore() {
    return this.request('/medicines/adherence/score');
  }

  // Smart Reminders
  async getReminders() {
    return this.request('/reminders');
  }

  async addReminder(reminder) {
    return this.request('/reminders', {
      method: 'POST',
      body: JSON.stringify(reminder),
    });
  }

  async completeReminder(reminderId) {
    return this.request(`/reminders/${reminderId}/complete`, {
      method: 'PATCH',
    });
  }

  // Clinical & Telehealth Appointments
  async getAppointments() {
    return this.request('/appointments');
  }

  async createAppointment(appointmentData) {
    return this.request('/appointments', {
      method: 'POST',
      body: JSON.stringify(appointmentData),
    });
  }

  async updateAppointment(appointmentId, updateData) {
    return this.request(`/appointments/${appointmentId}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  }

  async cancelAppointment(appointmentId) {
    return this.request(`/appointments/${appointmentId}`, {
      method: 'DELETE',
    });
  }

  // Nutrition & Meal Planning
  async getTodayNutrition() {
    return this.request('/nutrition/today');
  }

  async logMeal(mealData) {
    return this.request('/nutrition/meals', {
      method: 'POST',
      body: JSON.stringify(mealData),
    });
  }

  async getNutritionTargets() {
    return this.request('/nutrition/targets');
  }

  // Fitness & Lifestyle
  async getDailyActivity() {
    return this.request('/fitness/daily-activity');
  }

  async logDailyActivity(activityData) {
    return this.request('/fitness/daily-activity', {
      method: 'POST',
      body: JSON.stringify(activityData),
    });
  }

  async getWorkouts() {
    return this.request('/fitness/workouts');
  }

  async logWorkout(workout) {
    return this.request('/fitness/workouts', {
      method: 'POST',
      body: JSON.stringify(workout),
    });
  }

  async getHabits() {
    return this.request('/fitness/habits');
  }

  async checkInHabit(habitId) {
    return this.request(`/fitness/habits/${habitId}/check-in`, {
      method: 'POST',
      body: JSON.stringify({ completed: true }),
    });
  }

  // Mental Wellness
  async getTodayMood() {
    return this.request('/wellness/today');
  }

  async logMood(moodData) {
    return this.request('/wellness/mood', {
      method: 'POST',
      body: JSON.stringify(moodData),
    });
  }

  // AI Health Assistant
  async getAssistantSessions() {
    return this.request('/assistant/sessions');
  }

  async createAssistantSession(title = 'Health Consultation') {
    return this.request('/assistant/sessions', {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  }

  async sendAssistantMessage(sessionId, message) {
    return this.request(`/assistant/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // 360 Health Snapshot
  async getHealthSnapshot() {
    return this.request('/snapshot');
  }

  // Doctor Portal
  async getAccessGrants() {
    return this.request('/doctor/access-grants');
  }

  async createAccessGrant(grant) {
    return this.request('/doctor/access-grants', {
      method: 'POST',
      body: JSON.stringify(grant),
    });
  }

  async revokeAccessGrant(grantId) {
    return this.request(`/doctor/access-grants/${grantId}`, {
      method: 'DELETE',
    });
  }

  async getDoctorPatientRecords(token) {
    return this.request(`/doctor/patient-records/${token}`);
  }

  async submitDoctorConsultation(consultation) {
    return this.request('/doctor/consultations', {
      method: 'POST',
      body: JSON.stringify(consultation),
    });
  }

  // Privacy & Compliance
  async getUserConsent() {
    return this.request('/privacy/consent');
  }

  async updateUserConsent(consent) {
    return this.request('/privacy/consent', {
      method: 'PUT',
      body: JSON.stringify(consent),
    });
  }

  async exportUserData() {
    return this.request('/privacy/export-data');
  }

  async getAuditLogs() {
    return this.request('/audit/logs');
  }
}

export const api = new ApiService();
export default api;
