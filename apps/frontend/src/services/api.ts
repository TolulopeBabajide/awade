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

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    if (response.ok) {
      const data = await response.json();
      return { data };
    } else {
      const errorData = await response.json().catch(() => ({}));

      // Handle 401 Unauthorized globally
      if (response.status === 401) {
        // Clear invalid tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');

        // Redirect to login page
        window.location.href = '/login';

        return { error: 'Session expired. Please login again.' };
      }

      return { error: errorData.detail || `HTTP ${response.status}: ${response.statusText}` };
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
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Update user profile
  async updateProfile(profileData: any, userId?: number): Promise<ApiResponse<any>> {
    if (!userId) {
      return { error: 'User ID is required for profile updates.' };
    }

    const response = await fetch(`${API_BASE_URL}/users/${userId}/profile`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData)
    });
    return this.handleResponse(response);
  }

  // Lesson Plans
  async generateLessonPlan(planData: any): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/generate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(planData)
    });
    return this.handleResponse(response);
  }

  async getLessonPlans(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getLessonPlan(id: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Lesson Resources
  async generateLessonResource(lessonPlanId: string, contextInput: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/${lessonPlanId}/resources/generate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        lesson_plan_id: parseInt(lessonPlanId),
        context_input: sanitizeInput(contextInput)
      })
    });
    return this.handleResponse(response);
  }

  // Context Management
  async submitContext(lessonPlanId: string, contextText: string, contextType?: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/contexts/lesson-plan/${lessonPlanId}/submit`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        context_text: sanitizeInput(contextText),
        context_type: contextType
      })
    });
    return this.handleResponse(response);
  }

  async getContexts(lessonPlanId: string): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${API_BASE_URL}/contexts/lesson-plan/${lessonPlanId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
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
    const response = await fetch(`${API_BASE_URL}/lesson-plans/${lessonPlanId}/resources`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getAllLessonResources(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/resources`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getLessonResource(resourceId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/resources/${resourceId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async updateLessonResource(resourceId: string, userEditedContent: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/resources/${resourceId}/review`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        user_edited_content: userEditedContent
      })
    });
    return this.handleResponse(response);
  }

  async exportLessonResource(resourceId: string, format: 'pdf' | 'docx'): Promise<ApiResponse<Blob>> {
    const response = await fetch(`${API_BASE_URL}/lesson-plans/resources/${resourceId}/export`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        format: format
      })
    });

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
    const response = await fetch(`${API_BASE_URL}/countries/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getSubjects(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${API_BASE_URL}/subjects/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getGradeLevels(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${API_BASE_URL}/grade-levels/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getTopics(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${API_BASE_URL}/curriculum/topics`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getTopicsByCurriculumStructure(curriculumStructureId: number): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${API_BASE_URL}/curriculum/topics?curriculum_structure_id=${curriculumStructureId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Curriculum Data
  async getCurriculums(countryId?: number): Promise<ApiResponse<any[]>> {
    const url = countryId
      ? `${API_BASE_URL}/curriculum/?country_id=${countryId}`
      : `${API_BASE_URL}/curriculum/`;
    const response = await fetch(url, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getCurriculumStructures(curriculaId?: number): Promise<ApiResponse<any[]>> {
    const url = curriculaId
      ? `${API_BASE_URL}/curriculum-structures/?curricula_id=${curriculaId}`
      : `${API_BASE_URL}/curriculum-structures/`;
    const response = await fetch(url, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
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
    const response = await fetch(`${API_BASE_URL}/lesson-plans/ai/health`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }
}

export const apiService = new ApiService();
export default apiService; 