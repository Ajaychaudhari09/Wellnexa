// WellNexa AI API Service Client
const API_BASE = '/api/v1';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('wellnexa_token') || null;
    this.currentRole = localStorage.getItem('wellnexa_role') || null;
    this.currentUser = null;
    try {
      const stored = localStorage.getItem('wellnexa_user');
      if (stored) this.currentUser = JSON.parse(stored);
    } catch (e) {
      this.currentUser = null;
    }
  }

  setSession(token, role = 'PATIENT', user = null) {
    this.token = token;
    this.currentRole = role;
    this.currentUser = user;
    if (token) {
      localStorage.setItem('wellnexa_token', token);
      localStorage.setItem('wellnexa_role', role);
      if (user) localStorage.setItem('wellnexa_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('wellnexa_token');
      localStorage.removeItem('wellnexa_role');
      localStorage.removeItem('wellnexa_user');
    }
  }

  setToken(token, role = 'PATIENT') {
    this.setSession(token, role, this.currentUser);
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
        if (response.status === 401) {
          // Token expired or invalid: clear session and notify app
          console.warn('[WellNexa API] 401 Unauthorized encountered for:', endpoint);
          this.setSession(null, null, null);
          if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('wellnexa:unauthorized'));
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

  // Auth Operations
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    const accessToken = data.access_token;
    // Set token temporarily to fetch authenticated profile details
    this.token = accessToken;
    let me = null;
    try {
      me = await this.getMe();
    } catch (e) {
      console.warn('Could not fetch /auth/me after login:', e);
    }

    const isDoctor = email.toLowerCase().includes('doctor') ||
      (me?.roles && me.roles.some(r => r.toUpperCase().includes('DOCTOR')));
    const role = isDoctor ? 'DOCTOR' : 'PATIENT';

    this.setSession(accessToken, role, me);
    return { token: accessToken, role, user: me };
  }

  async register({ email, password, first_name, last_name, role = 'PATIENT' }) {
    const res = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        first_name,
        last_name,
        role: role.toUpperCase(),
      }),
    });

    // Auto-login newly registered user
    return this.login(email, password);
  }

  async logout() {
    try {
      if (this.token) {
        await this.request('/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: 'dummy_revoke' }),
        }).catch(() => null);
      }
    } finally {
      this.setSession(null, null, null);
    }
  }

  async getMe() {
    return this.request('/auth/me');
  }

  // Personal Profile
  async getProfile() {
    return this.request('/profile/me');
  }

  async updateProfile(profileData) {
    return this.request('/profile/me', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
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
