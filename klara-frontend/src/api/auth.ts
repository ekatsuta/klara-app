import apiClient from '@/lib/apiClient';
import type { User } from '@/types';

interface SignupResponse {
  user: User;
  token: string;
}

interface LoginResponse {
  user: User;
  token: string;
}

export const signup = async (email: string, firstName: string): Promise<SignupResponse> => {
  const response = await apiClient.post<SignupResponse>('/auth/signup', { email, firstName });
  return response.data;
};

export const login = async (email: string): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>('/auth/login', { email });
  return response.data;
};
