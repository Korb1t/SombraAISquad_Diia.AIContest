import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from './client';
import type { ProblemRequest } from '@/types/api';

/**
 * React Query hooks для роботи з API
 */

/**
 * Hook для перевірки здоров'я API
 * Використання: const { data, isLoading } = useHealthCheck();
 */
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health-check'],
    queryFn: api.healthCheck,
    staleTime: 60000, // Кеш на 1 хв
  });
};

/**
 * Hook для класифікації проблеми
 * Використання:
 * const { mutate: classify, data, isLoading } = useClassifyProblem();
 * classify({ problem_text: "..." });
 */
export const useClassifyProblem = () => {
  return useMutation({
    mutationFn: (data: ProblemRequest) => api.classifyProblem(data),
  });
};




