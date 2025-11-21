import axios from 'axios';
import type { ProblemRequest, ProblemClassificationResponse } from '@/types/api';

/**
 * Axios клієнт для роботи з API
 * В dev режимі використовує Vite proxy (/api -> http://localhost:8000/api)
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 секунд (для LLM може бути довго)
});

/**
 * API методи
 */
export const api = {
  /**
   * Перевірка здоров'я сервера
   */
  healthCheck: async (): Promise<boolean> => {
    const response = await apiClient.get<boolean>('/utils/health-check/');
    return response.data;
  },

  /**
   * Класифікація проблеми користувача
   */
  classifyProblem: async (
    data: ProblemRequest
  ): Promise<ProblemClassificationResponse> => {
    const response = await apiClient.post<ProblemClassificationResponse>(
      '/classify/',
      data
    );
    return response.data;
  },
};




