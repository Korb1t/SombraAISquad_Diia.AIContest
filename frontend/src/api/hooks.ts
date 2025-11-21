import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from './client';
import type { SolveProblemRequest } from '@/types/api';

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health-check'],
    queryFn: api.healthCheck,
    staleTime: 60000,
  });
};

export const useSolveProblem = () => {
  return useMutation({
    mutationFn: (data: SolveProblemRequest) => api.solveProblem(data),
  });
};




