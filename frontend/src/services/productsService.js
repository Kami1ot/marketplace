// src/services/productsService.js
import api from './api';

export const productsService = {
  // Получить все товары с фильтрами
  async getProducts(params = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.skip) queryParams.append('skip', params.skip);
      if (params.limit) queryParams.append('limit', params.limit);
      if (params.category_id) queryParams.append('category_id', params.category_id);
      if (params.search) queryParams.append('search', params.search);
      if (params.min_price) queryParams.append('min_price', params.min_price);
      if (params.max_price) queryParams.append('max_price', params.max_price);

      const response = await api.get(`/products?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Получить товар по ID
  async getProduct(productId) {
    try {
      const response = await api.get(`/products/${productId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Получить категории
  async getCategories() {
    try {
      const response = await api.get('/products/categories');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // === Функции для BUSINESS пользователей ===

  // Получить свои товары
  async getMyProducts(includeInactive = false) {
    try {
      const response = await api.get(`/products/my/products?include_inactive=${includeInactive}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Создать товар
  async createProduct(productData) {
    try {
      const response = await api.post('/products', productData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Обновить товар
  async updateProduct(productId, productData) {
    try {
      const response = await api.put(`/products/${productId}`, productData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Деактивировать товар
  async deactivateProduct(productId) {
    try {
      const response = await api.patch(`/products/${productId}/deactivate`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Активировать товар
  async activateProduct(productId) {
    try {
      const response = await api.patch(`/products/${productId}/activate`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Удалить товар навсегда
  async deleteProduct(productId) {
    try {
      const response = await api.delete(`/products/${productId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Получить статистику своих товаров
  async getMyProductsStats() {
    try {
      const response = await api.get('/products/my/products/stats');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};