import { sanitizeInput } from '../utils/sanitizer';

const API_BASE_URL = '/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  private async handleResponse<T>(response: Response, retryCallback?: () => Promise<ApiResponse<T>>): Promise<ApiResponse<T>> {
    if (response.ok) {
      if (response.status === 204) {
        return {};
      }
      const data = await response.json();
      return { data };
    } else {
      let errorData: any = {};
      try {
        errorData = await response.json();
      } catch (e) {
        // Response body might be empty or not JSON
      }

      // Handle 401 Unauthorized globally
      if (response.status === 401) {
        // Login and Signup endpoints return 401 for invalid credentials, not token expiry
        if (response.url.includes('/auth/login') || response.url.includes('/auth/signup')) {
          return { error: errorData.detail || 'Invalid credentials' };
        }

        // If this was already a refresh attempt or we have no retry logic, fail
        if (response.url.includes('/auth/refresh') || !retryCallback) {
          this.logout();
          return { error: 'Session expired. Please login again.' };
        }

        // Attempt to refresh token
        try {
          const refreshSuccess = await this.refreshAccessToken();
          if (refreshSuccess && retryCallback) {
            // Retry original request
            return await retryCallback();
          }
        } catch (e) {
          console.error("Refresh failed", e);
        }

        // If refresh failed, logout
        this.logout();
        return { error: 'Session expired. Please login again.' };
      }

      return { error: errorData.detail || `HTTP ${response.status}: ${response.statusText}` };
    }
  }

  private logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    window.location.href = '/login';
  }

  private async refreshAccessToken(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // Authentication
  async login(email: string, password: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return this.handleResponse(response);
  }

  async signup(userData: any): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    return this.handleResponse(response);
  }

  // Get current user profile
  async getCurrentUser(): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }

    // We pass a closure that re-executes the fetch to handleResponse for retries
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getCurrentUser());
  }

  // Update user profile
  async updateProfile(profileData: any, userId?: number): Promise<ApiResponse<any>> {
    if (!userId) {
      return { error: 'User ID is required for profile updates.' };
    }

    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/users/${userId}/profile`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(profileData)
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.updateProfile(profileData, userId));
  }

  // Lesson Plans
  async generateLessonPlan(planData: any): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/generate`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(planData)
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.generateLessonPlan(planData));
  }

  async getLessonPlans(): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getLessonPlans());
  }

  async getLessonPlan(id: string): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/${id}`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getLessonPlan(id));
  }

  // Lesson Resources
  async generateLessonResource(lessonPlanId: string, contextInput: string): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/${lessonPlanId}/resources/generate`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          lesson_plan_id: parseInt(lessonPlanId),
          context_input: sanitizeInput(contextInput)
        })
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.generateLessonResource(lessonPlanId, contextInput));
  }

  // Context Management
  async submitContext(lessonPlanId: string, contextText: string, contextType?: string): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/contexts/lesson-plan/${lessonPlanId}/submit`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          context_text: sanitizeInput(contextText),
          context_type: contextType
        })
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.submitContext(lessonPlanId, contextText, contextType));
  }

  async getContexts(lessonPlanId: string): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/contexts/lesson-plan/${lessonPlanId}`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getContexts(lessonPlanId));
  }

  async updateContext(contextId: string, contextText: string, contextType?: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/contexts/${contextId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        context_text: sanitizeInput(contextText),
        context_type: contextType
      })
    });
    return this.handleResponse(response);
  }

  async deleteContext(contextId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/contexts/${contextId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getLessonResources(lessonPlanId: string): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/${lessonPlanId}/resources`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getLessonResources(lessonPlanId));
  }

  async getAllLessonResources(): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/resources`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getAllLessonResources());
  }

  async getLessonResource(resourceId: string): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/resources/${resourceId}`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getLessonResource(resourceId));
  }

  async updateLessonResource(resourceId: string, userEditedContent: string): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/resources/${resourceId}/review`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          user_edited_content: userEditedContent
        })
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.updateLessonResource(resourceId, userEditedContent));
  }

  async exportLessonResource(resourceId: string, format: 'pdf' | 'docx'): Promise<ApiResponse<Blob>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/resources/${resourceId}/export`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          format: format
        })
      });
      return response;
    }

    // Export needs special handling because it returns a blob, not JSON
    // We handle the retry manually here because handleResponse expects JSON usually 
    // BUT our current handleResponse is generic ApiResponse<T>
    // However, handleResponse parses JSON: `const data = await response.json();`
    // This breaks for Blobs. We need to update exportLessonResource to NOT use handleResponse for success
    // Or update handleResponse to support non-JSON?
    // Given the complexity, let's just implement the retry logic manually here for export

    // First try
    let response = await fetchFn();

    if (response.status === 401) {
      // Try refresh
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        response = await fetchFn();
      } else {
        this.logout();
        return { error: 'Session expired. Please login again.' };
      }
    }

    if (response.ok) {
      const blob = await response.blob();
      return { data: blob };
    } else {
      const errorData = await response.json().catch(() => ({}));
      return { error: errorData.detail || `HTTP ${response.status}: ${response.statusText}` };
    }
  }

  // Curriculum Data
  async getCountries(): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/countries/`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getCountries());
  }

  async getSubjects(): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/subjects/`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getSubjects());
  }

  async getGradeLevels(): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/grade-levels/`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getGradeLevels());
  }

  async getTopics(): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/curriculum/topics`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getTopics());
  }

  async getTopicsByCurriculumStructure(curriculumStructureId: number): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/curriculum/topics?curriculum_structure_id=${curriculumStructureId}`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getTopicsByCurriculumStructure(curriculumStructureId));
  }

  // Curriculum Data
  async getCurriculums(countryId?: number): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const url = countryId
        ? `${API_BASE_URL}/curriculum/?country_id=${countryId}`
        : `${API_BASE_URL}/curriculum/`;
      const response = await fetch(url, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getCurriculums(countryId));
  }

  async getCurriculumStructures(curriculaId?: number): Promise<ApiResponse<any[]>> {
    const fetchFn = async () => {
      const url = curriculaId
        ? `${API_BASE_URL}/curriculum-structures/?curricula_id=${curriculaId}`
        : `${API_BASE_URL}/curriculum-structures/`;
      const response = await fetch(url, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.getCurriculumStructures(curriculaId));
  }

  // Google OAuth
  async googleAuth(credential: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential })
    });

    return this.handleResponse(response);
  }

  // Password Reset
  async forgotPassword(email: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return this.handleResponse(response);
  }

  async resetPassword(token: string, newPassword: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: newPassword })
    });
    return this.handleResponse(response);
  }

  // AI Health Check
  async checkAiHealth(): Promise<ApiResponse<any>> {
    const fetchFn = async () => {
      const response = await fetch(`${API_BASE_URL}/lesson-plans/ai/health`, {
        headers: this.getAuthHeaders()
      });
      return response;
    }
    const response = await fetchFn();
    return this.handleResponse(response, () => this.checkAiHealth());
  }
}

export const apiService = new ApiService();
export default apiService;