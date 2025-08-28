// Test Environment API Configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://awade-backend-test.onrender.com/api'
  : '/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class TestApiService {
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
      
      console.error('Test API Error Response:', {
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

  // Health check for test environment
  async healthCheck(): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
    return this.handleResponse(response);
  }

  // Test environment info
  async getEnvironmentInfo(): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/`);
    return this.handleResponse(response);
  }
}

export const testApiService = new TestApiService();
export default testApiService;
