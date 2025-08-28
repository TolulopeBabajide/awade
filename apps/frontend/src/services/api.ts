// API Service with environment-aware configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Robust test environment detection - multiple fallback methods
const isTestEnvironment = 
  import.meta.env.VITE_ENVIRONMENT === 'test' || 
  window.location.hostname === 'awade-test.vercel.app' ||
  window.location.hostname.includes('test') ||
  window.location.hostname.includes('vercel.app');

// Force test backend URL for test environment
const finalApiBaseUrl = isTestEnvironment 
  ? 'https://awade-backend-test.onrender.com/api'
  : API_BASE_URL;

// Log environment information for debugging
console.log('🌐 API Base URL:', finalApiBaseUrl);
console.log('🔧 Environment:', import.meta.env.MODE);
console.log('🚀 Backend URL:', import.meta.env.VITE_BACKEND_URL);
console.log('🏷️ Environment Type:', import.meta.env.VITE_ENVIRONMENT);
console.log('🧪 Is Test Environment:', isTestEnvironment);
console.log('📍 Current Hostname:', window.location.hostname);
console.log('🔗 Final API URL:', finalApiBaseUrl);

// Always warn if we're in test environment but not using test backend
if (isTestEnvironment && !finalApiBaseUrl.includes('awade-backend-test.onrender.com')) {
  console.error('❌ CRITICAL: Test environment detected but not using test backend!');
  console.error('🔧 Expected: https://awade-backend-test.onrender.com/api');
  console.error('🔧 Actual:', finalApiBaseUrl);
} else if (isTestEnvironment) {
  console.log('✅ Test environment confirmed - using test backend');
}

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
      
      console.error('API Error Response:', {
        status: response.status,
        statusText: response.statusText,
        errorData
      });
      
      // Handle 401 Unauthorized globally
      if (response.status === 401) {
        // Clear invalid tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        
        // Redirect to login page
        window.location.href = '/login';
        
        return { error: 'Session expired. Please login again.' };
      }
      
      // Provide more detailed error messages
      let errorMessage = errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      
      // Handle specific error cases
      if (response.status === 422 && errorData.detail) {
        // Validation errors
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((err: any) => err.msg).join(', ');
        } else {
          errorMessage = errorData.detail;
        }
      }
      
      return { error: errorMessage };
    }
  }

  // Authentication
  async login(email: string, password: string): Promise<ApiResponse<any>> {
    console.log('🔐 Login attempt for email:', email);
    console.log('🔗 Login URL:', `${finalApiBaseUrl}/auth/login`);
    console.log('🧪 Is Test Environment:', isTestEnvironment);
    
    const response = await fetch(`${finalApiBaseUrl}/auth/login`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Origin': window.location.origin
      },
      body: JSON.stringify({ email, password })
    });
    
    console.log('📡 Login response status:', response.status);
    console.log('📡 Login response headers:', Object.fromEntries(response.headers.entries()));
    
    return this.handleResponse(response);
  }

  async signup(userData: any): Promise<ApiResponse<any>> {
    console.log('🚀 Signup attempt with data:', { ...userData, password: '[REDACTED]' });
    console.log('🔗 Signup URL:', `${finalApiBaseUrl}/auth/signup`);
    console.log('🧪 Is Test Environment:', isTestEnvironment);
    
    const response = await fetch(`${finalApiBaseUrl}/auth/signup`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Origin': window.location.origin
      },
      body: JSON.stringify(userData)
    });
    
    console.log('📡 Signup response status:', response.status);
    console.log('📡 Signup response headers:', Object.fromEntries(response.headers.entries()));
    
    return this.handleResponse(response);
  }

  // Get current user profile
  async getCurrentUser(): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/auth/me`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Update user profile
  async updateProfile(profileData: any, userId?: number): Promise<ApiResponse<any>> {
    if (!userId) {
      return { error: 'User ID is required for profile updates.' };
    }
    
    const response = await fetch(`${finalApiBaseUrl}/users/${userId}/profile`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData)
    });
    return this.handleResponse(response);
  }

  // Upload profile image
  async uploadProfileImage(formData: FormData): Promise<ApiResponse<any>> {
    const token = localStorage.getItem('access_token');
    const headers: HeadersInit = {
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
    
    const response = await fetch(`${finalApiBaseUrl}/users/profile/upload-image`, {
      method: 'POST',
      headers,
      body: formData
    });
    return this.handleResponse(response);
  }

  // Delete profile image
  async deleteProfileImage(): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/users/profile/delete-image`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Lesson Plans
  async generateLessonPlan(planData: any): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/generate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(planData)
    });
    return this.handleResponse(response);
  }

  async getLessonPlans(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getLessonPlan(id: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Lesson Resources
  async generateLessonResource(lessonPlanId: string, contextInput: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/${lessonPlanId}/resources/generate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        lesson_plan_id: parseInt(lessonPlanId),
        context_input: contextInput
      })
    });
    return this.handleResponse(response);
  }

  // Context Management
  async submitContext(lessonPlanId: string, contextText: string, contextType?: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/contexts/lesson-plan/${lessonPlanId}/submit`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        context_text: contextText,
        context_type: contextType
      })
    });
    return this.handleResponse(response);
  }

  async getContexts(lessonPlanId: string): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/contexts/lesson-plan/${lessonPlanId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async updateContext(contextId: string, contextText: string, contextType?: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/contexts/${contextId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        context_text: contextText,
        context_type: contextType
      })
    });
    return this.handleResponse(response);
  }

  async deleteContext(contextId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/contexts/${contextId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getLessonResources(lessonPlanId: string): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/${lessonPlanId}/resources`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getAllLessonResources(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/resources`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getLessonResource(resourceId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/resources/${resourceId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async updateLessonResource(resourceId: string, userEditedContent: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/resources/${resourceId}/review`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        user_edited_content: userEditedContent
      })
    });
    return this.handleResponse(response);
  }

  async exportLessonResource(resourceId: string, format: 'pdf' | 'docx'): Promise<ApiResponse<Blob>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/resources/${resourceId}/export`, {
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
    const response = await fetch(`${finalApiBaseUrl}/countries/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getSubjects(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/subjects/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getGradeLevels(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/grade-levels/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getTopics(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/curriculum/topics`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getTopicsByCurriculumStructure(curriculumStructureId: number): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${finalApiBaseUrl}/curriculum/topics?curriculum_structure_id=${curriculumStructureId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Curriculum Data
  async getCurriculums(countryId?: number): Promise<ApiResponse<any[]>> {
    const url = countryId 
      ? `${finalApiBaseUrl}/curriculum/?country_id=${countryId}`
      : `${finalApiBaseUrl}/curriculum/`;
    const response = await fetch(url, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getCurriculumStructures(curriculaId?: number): Promise<ApiResponse<any[]>> {
    const url = curriculaId 
      ? `${finalApiBaseUrl}/curriculum-structures/?curricula_id=${curriculaId}`
      : `${finalApiBaseUrl}/curriculum-structures/`;
    const response = await fetch(url, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Google OAuth
  async googleAuth(credential: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential })
    });
    
    return this.handleResponse(response);
  }

  // Password Reset
  async forgotPassword(email: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return this.handleResponse(response);
  }

  async resetPassword(token: string, newPassword: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: newPassword })
    });
    return this.handleResponse(response);
  }

  // AI Health Check
  async checkAiHealth(): Promise<ApiResponse<any>> {
    const response = await fetch(`${finalApiBaseUrl}/lesson-plans/ai/health`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }
}

export const apiService = new ApiService();
export default apiService; 