import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserResponse } from '@/types';

interface UserState {
  user: UserResponse | null;
  setUser: (user: UserResponse) => void;
  clearUser: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      setUser: (user: UserResponse) => set({ user }),
      clearUser: () => set({ user: null }),
    }),
    {
      name: 'user-storage',
    }
  )
);
