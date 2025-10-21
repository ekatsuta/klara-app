import apiClient from '@/lib/apiClient';
import type { UserResponse } from '@/types';

interface AuthResponse {
  user: UserResponse;
}

export const signup = async (email: string, firstName: string): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/auth/signup', { email, firstName });
  return response.data;
};

export const login = async (email: string): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/auth/login', { email });
  return response.data;
};
