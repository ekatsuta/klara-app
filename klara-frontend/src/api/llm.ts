import apiClient from '@/lib/apiClient';
import type { BrainDumpResponse } from '@/types';

export const processBrainDump = async (text: string, userId: string): Promise<BrainDumpResponse> => {
  const response = await apiClient.post<BrainDumpResponse>('/brain-dumps', {
    text,
    user_id: userId
  });
  return response.data;
};
