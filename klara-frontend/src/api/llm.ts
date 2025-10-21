import apiClient from '@/lib/apiClient';

interface BrainDumpResponse {
  id: string;
  text: string;
  user_id: string;
  processed: boolean;
  created_at: string;
}

export const processBrainDump = async (text: string, userId: string): Promise<BrainDumpResponse> => {
  const response = await apiClient.post<BrainDumpResponse>('/brain-dumps', {
    text,
    user_id: userId
  });
  return response.data;
};
