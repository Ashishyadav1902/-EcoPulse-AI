const API_BASE_URL = '/api';

class ApiService {
    static async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };
        
        // Ensure credentials (cookies) are sent with every request for Flask-Login sessions
        config.credentials = 'same-origin';

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.error || data.message || 'API request failed');
            }

            return { data, status: response.status };
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    static async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: { email, password }
        });
    }

    static async register(username, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: { username, email, password }
        });
    }

    static async logout() {
        return this.request('/auth/logout', { method: 'POST' });
    }

    static async getCurrentUser() {
        return this.request('/auth/me');
    }

    static async getDashboard() {
        return this.request('/dashboard');
    }

    static async getRecommendations() {
        return this.request('/recommendations');
    }

    static async calculateFootprint(payload) {
        return this.request('/calculate', {
            method: 'POST',
            body: payload
        });
    }

    static async updateProfile(payload) {
        return this.request('/user/profile', {
            method: 'PUT',
            body: payload
        });
    }

    static async getWeather() {
        return this.request('/weather');
    }

    static async chat(message) {
        return this.request('/chat', {
            method: 'POST',
            body: { message }
        });
    }
}

window.api = ApiService;
