import axios from 'axios';
import type { SolveProblemRequest, SolveProblemResponse } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

export const api = {
  healthCheck: async (): Promise<boolean> => {
    const response = await apiClient.get<boolean>('/utils/health-check/');
    return response.data;
  },

  solveProblem: async (
    data: SolveProblemRequest
  ): Promise<SolveProblemResponse> => {
    const response = await apiClient.post<SolveProblemResponse>(
      '/solve/',
      data
    );
    return response.data;
  },
};




