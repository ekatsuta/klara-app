import apiClient from '../lib/apiClient';

export const signup = async (email, firstName) => {
  const response = await apiClient.post('/auth/signup', { email, firstName });
  return response.data;
};

export const login = async (email) => {
  const response = await apiClient.post('/auth/login', { email });
  return response.data;
};
