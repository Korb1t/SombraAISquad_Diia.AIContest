/**
 * TypeScript типи для API
 * Синхронізовано з app/schemas/problems.py
 */

// Запит на класифікацію проблеми
export interface ProblemRequest {
  problem_text: string;
  user_name?: string | null;
  user_address?: string | null;
  user_phone?: string | null;
}

// Відповідь класифікатора
export interface ProblemClassificationResponse {
  category_id: string;
  category_name: string;
  category_description: string;
  confidence: number; // 0.0-1.0
  reasoning: string;
  is_urgent: boolean;
}

// Інформація про сервіс
export interface ServiceInfo {
  service_name: string;
  service_phone?: string | null;
  service_email?: string | null;
  service_address?: string | null;
}

// Повна відповідь (якщо буде endpoint з листом)
export interface ProblemResponse {
  category_id: string;
  category_name: string;
  confidence: number;
  is_urgent: boolean;
  service: ServiceInfo;
  letter_text: string;
}




