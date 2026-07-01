import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/LoginView.vue') },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/employees', name: '员工管理', component: () => import('@/views/EmployeeView.vue'), meta: { requiresAuth: true } },
  { path: '/questions', name: '题目管理', component: () => import('@/views/QuestionView.vue'), meta: { requiresAuth: true } },
  { path: '/questions/import', name: '试卷导入', component: () => import('@/views/QuestionImportView.vue'), meta: { requiresAuth: true } },

  { path: '/tasks', name: '任务管理', component: () => import('@/views/TaskView.vue'), meta: { requiresAuth: true } },
  { path: '/reports', name: '评估报告', component: () => import('@/views/ReportView.vue'), meta: { requiresAuth: true } },
  { path: '/assessment', name: '在线测评', component: () => import('@/views/AssessmentView.vue') },
  { path: '/assessment/:code', name: '测评作答', component: () => import('@/views/AssessmentView.vue') },
  { path: '/assess/:code', component: () => import('@/views/AssessmentView.vue') },
  { path: '/branches', name: '分公司管理', component: () => import('@/views/BranchView.vue'), meta: { requiresAuth: true } },
  { path: "/projects", name: "项目管理", component: () => import("@/views/ProjectView.vue"), meta: { requiresAuth: true } },
  { path: '/admins', name: '管理员管理', component: () => import('@/views/AdminView.vue'), meta: { requiresAuth: true } },
  { path: '/change-password', name: '????', component: () => import('@/views/ChangePasswordView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) next('/login')
  else if (to.path === '/login' && auth.isLoggedIn) next('/dashboard')
  else next()
})
export default router



