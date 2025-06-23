// src/services/authService.js
import api from './api';

export const authService = {
  // Регистрация нового пользователя
  async register(userData) {
    try {
      const response = await api.post('/auth/register', {
        email: userData.email,
        password: userData.password,
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        role: 'user' // По умолчанию обычный пользователь
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Авторизация пользователя
  async login(credentials) {
    try {
      // FastAPI OAuth2PasswordRequestForm ожидает username и password
      const formData = new FormData();
      formData.append('username', credentials.email); // В FastAPI username = email
      formData.append('password', credentials.password);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token, token_type } = response.data;
      
      // Сохраняем токен
      localStorage.setItem('access_token', access_token);
      
      // Получаем данные пользователя
      const user = await this.getCurrentUser();
      localStorage.setItem('user_data', JSON.stringify(user));
      
      return { access_token, token_type, user };
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Получение данных текущего пользователя
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Выход из системы
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
  },

  // Проверка авторизации
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  // Получение сохраненных данных пользователя
  getStoredUser() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  },

  // Получение токена
  getToken() {
    return localStorage.getItem('access_token');
  }
};