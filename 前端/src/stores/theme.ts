import { defineStore } from 'pinia'
import { getStorage, setStorage } from '@/utils/storage'

export type ThemeMode = 'dark' | 'light'

const THEME_KEY = 'lab_theme'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: getStorage<ThemeMode>(THEME_KEY, 'dark'),
  }),
  getters: {
    isDark: (s) => s.mode === 'dark',
  },
  actions: {
    toggle() {
      this.setMode(this.mode === 'dark' ? 'light' : 'dark')
    },
    setMode(mode: ThemeMode) {
      this.mode = mode
      this.apply()
    },
    /** 应用到 <html> 的 class，与 Element Plus 暗色主题联动 */
    apply() {
      setStorage(THEME_KEY, this.mode)
      const root = document.documentElement
      if (this.mode === 'dark') root.classList.add('dark')
      else root.classList.remove('dark')
    },
  },
})