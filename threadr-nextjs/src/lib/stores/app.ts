import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Theme } from '@/types';

interface AppState {
  theme: Theme;
  sidebarOpen: boolean;
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message?: string;
    duration?: number;
  }>;
  
  // Actions
  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  addNotification: (notification: Omit<AppState['notifications'][0], 'id'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      sidebarOpen: false,
      notifications: [],

      setTheme: (theme: Theme) => {
        set({ theme });
        
        // Apply theme to document
        if (typeof window !== 'undefined') {
          const root = window.document.documentElement;
          
          if (theme === 'dark') {
            root.classList.add('dark');
          } else if (theme === 'light') {
            root.classList.remove('dark');
          } else {
            // System theme
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (isDark) {
              root.classList.add('dark');
            } else {
              root.classList.remove('dark');
            }
          }
        }
      },

      toggleSidebar: () => {
        set(state => ({ sidebarOpen: !state.sidebarOpen }));
      },

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },

      addNotification: (notification) => {
        const id = Math.random().toString(36).substring(2, 15);
        const newNotification = { ...notification, id };
        
        set(state => ({
          notifications: [...state.notifications, newNotification]
        }));
        
        // Auto-remove notification after duration
        const duration = notification.duration || 5000;
        if (duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, duration);
        }
      },

      removeNotification: (id: string) => {
        set(state => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }));
      },

      clearNotifications: () => {
        set({ notifications: [] });
      },
    }),
    {
      name: 'threadr-app',
      partialize: (state) => ({ 
        theme: state.theme,
        sidebarOpen: state.sidebarOpen
      }),
    }
  )
);

// Initialize theme on first load
if (typeof window !== 'undefined') {
  const store = useAppStore.getState();
  store.setTheme(store.theme);
  
  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (_e) => {
    const currentTheme = useAppStore.getState().theme;
    if (currentTheme === 'system') {
      store.setTheme('system');
    }
  });
}