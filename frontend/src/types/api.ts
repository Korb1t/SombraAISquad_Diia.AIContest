export interface PersonalInfo {
  name?: string | null;
  address?: string | null;
  city?: string | null;
  phone?: string | null;
  apartment?: string | null;
}

export interface SolveProblemRequest {
  user_info: PersonalInfo;
  problem_text: string;
}

export interface ProblemClassification {
  category_id: string;
  category_name: string;
  confidence: number;
  is_urgent: boolean;
  is_relevant?: boolean;
  category_description: string;
  reasoning: string;
}

export interface ServiceInfo {
  service_type: string;
  service_name: string;
  service_phone?: string | null;
  service_email?: string | null;
  service_website?: string | null;
  service_address?: string | null;
}

export interface ServiceResponse {
  category_id: string;
  category_name: string;
  confidence: number;
  is_urgent: boolean;
  service_info: ServiceInfo;
  reasoning: string;
}

export interface SolveProblemResponse {
  user_info: PersonalInfo;
  classification: ProblemClassification;
  service: ServiceResponse;
  appeal_text: string;
}




