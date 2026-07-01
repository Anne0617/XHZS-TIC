import { defineStore } from 'pinia'
import api from '@/api'
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    isSuperAdmin: (s) => s.user?.role === 'super_admin'
  },
  actions: {
    async login(username, password) {
      const r = await api.post('/login/', { username, password })
      this.token = r.data.access; localStorage.setItem('token', this.token)
      this.user = r.data.user
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    async changePassword(oldPwd, newPwd) { const r = await api.post('/change-password/', { old_password: oldPwd, new_password: newPwd }); return r },
  logout() { this.token = ''; this.user = null; localStorage.removeItem('token'); localStorage.removeItem('user') }
  }
})
