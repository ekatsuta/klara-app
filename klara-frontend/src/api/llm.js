import apiClient from '../lib/apiClient';

export const processBrainDump = async (text, userId) => {
  const response = await apiClient.post('/brain-dumps', {
    text,
    user_id: userId
  });
  return response.data;
};
