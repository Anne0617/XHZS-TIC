<template>
  <div class="app-layout" v-if="auth.isLoggedIn">
    <!-- 背景装饰 -->
    <div class="bg-tech"></div>
    
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo"><i class="fas fa-star"></i></div>
        <div class="sidebar-brand">
          <h2>智善 TIC</h2>
          <span class="sidebar-sub">管理后台</span>
        </div>
      </div>

      <div class="sidebar-user">
        <div class="user-avatar">{{ (auth.user?.first_name || auth.user?.username)[0] }}</div>
        <div class="user-info">
          <span class="user-name">{{ auth.user?.first_name || auth.user?.username }}</span>
          <span class="user-role">{{ auth.user?.role === "super_admin" ? "超级管理员" : "HR管理员" }}</span>
        </div>
      </div>

      <nav class="sidebar-menu">
        <div class="menu-label">概览</div>
        <router-link to="/dashboard" class="menu-item"><i class="fas fa-chart-pie"></i><span>数据看板</span></router-link>
        
        <div class="menu-label">业务管理</div>
        <router-link to="/employees" class="menu-item"><i class="fas fa-users"></i><span>员工管理</span></router-link>
        <router-link to="/questions" class="menu-item"><i class="fas fa-question-circle"></i><span>题目管理</span></router-link>
        <router-link to="/templates" class="menu-item"><i class="fas fa-file-alt"></i><span>试卷管理</span></router-link>
        <router-link to="/questions/import" class="menu-item"><i class="fas fa-file-import"></i><span>试卷导入</span></router-link>
        <router-link to="/tasks" class="menu-item"><i class="fas fa-tasks"></i><span>任务管理</span></router-link>
       <router-link to="/reports" class="menu-item"><i class="fas fa-file-alt"></i><span>评估报告</span></router-link>
        <a href="/exam-qrcode/" target="_blank" class="menu-item"><i class="fas fa-share-alt"></i><span>测评分享</span></a>

       <div class="menu-label" v-if="auth.isSuperAdmin">系统管理</div>
        <router-link to="/branches" class="menu-item" v-if="auth.isSuperAdmin"><i class="fas fa-building"></i><span>分公司</span></router-link>
        <router-link to="/projects" class="menu-item" v-if="auth.isSuperAdmin"><i class="fas fa-folder-tree"></i><span>项目管理</span></router-link>
        <router-link to="/admins" class="menu-item" v-if="auth.isSuperAdmin"><i class="fas fa-user-shield"></i><span>管理员</span></router-link>
        
        <div class="sidebar-spacer"></div>

        <a class="menu-item menu-logout" @click="logout">
          <i class="fas fa-sign-out-alt"></i><span>退出登录</span>
        </a>
      </nav>
    </aside>

    <!-- 主内容 -->
    <main class="main-content">
      <!-- 顶栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <div class="breadcrumb">
            <i class="fas fa-home"></i>
            <span class="bc-sep">/</span>
            <span class="bc-current">{{ routeName || "加载中..." }}</span>
          </div>
        </div>
        <div class="topbar-right">
          <div class="header-time">{{ currentTime }}</div>
          <div class="user-dropdown">
            <div class="user-badge">
              <span>{{ (auth.user?.first_name || auth.user?.username)[0] }}</span>
            </div>
            <span class="user-name-top">{{ auth.user?.first_name || auth.user?.username }}</span>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="content-area"><router-view /></div>
    </main>
  </div>
  <router-view v-else />
</template>

<script setup>
import { computed, ref, reactive, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import api from "@/api"
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const routeName = computed(() => route.name || "")
const currentTime = ref("")

let timer
onMounted(() => {
  const update = () => {
    const d = new Date()
    currentTime.value = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")} ${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}`
  }
  update()
  timer = setInterval(update, 60000)
})
onUnmounted(() => clearInterval(timer))

const showPwdModal = ref(false)
const pwdForm = reactive({ old: "", new: "", confirm: "" })
const pwdError = ref("")
const pwdSuccess = ref("")
const pwdSaving = ref(false)

async function doChangePwd() {
  pwdError.value = ""; pwdSuccess.value = ""
  if (!pwdForm.old || !pwdForm.new) { pwdError.value = "请填写密码"; return }
  if (pwdForm.new.length < 6) { pwdError.value = "新密码至少6位"; return }
  if (pwdForm.new !== pwdForm.confirm) { pwdError.value = "两次密码不一致"; return }
  pwdSaving.value = true
  try {
    await api.post("/change-password/", { old_password: pwdForm.old, new_password: pwdForm.new })
    pwdSuccess.value = "密码修改成功"
    pwdForm.old = ""; pwdForm.new = ""; pwdForm.confirm = ""
    setTimeout(() => { showPwdModal.value = false; pwdSuccess.value = "" }, 1500)
  } catch (e) {
    pwdError.value = e.response?.data?.error || "修改失败"
  } finally { pwdSaving.value = false }
}

function logout() { auth.logout(); router.push("/login") }
</script>

<style>
/* ===== 全局变量 ===== */
:root {
  --bg-deep: #0a1628;
  --bg-card: #111d36;
  --bg-card-hover: #162348;
  --bg-input: rgba(255,255,255,0.03);
  --accent-warm: #ff8f00;
  --accent-warm-light: #ffb300;
  --accent-warm-glow: rgba(255,143,0,0.25);
  --accent-blue: #1565c0;
  --accent-blue-light: #1e88e5;
  --text: #e8eaf6;
  --text-light: #90a4ae;
  --text-muted: #546e7a;
  --border: rgba(255,255,255,0.06);
  --border-hover: rgba(255,143,0,0.15);
  --shadow: 0 4px 24px rgba(0,0,0,0.3);
  --shadow-glow: 0 4px 20px rgba(255,143,0,0.15);
  --radius: 8px;
  --radius-sm: 6px;
  --radius-lg: 12px;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font);
  background: var(--bg-deep);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
}

/* ===== 背景装饰 ===== */
.bg-tech {
  position: fixed;
  inset: 0;
  background:
    linear-gradient(rgba(255,143,0,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,143,0,0.02) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

.bg-tech::after {
  content: "";
  position: fixed;
  top: -20%;
  right: -10%;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,143,0,0.05) 0%, transparent 60%);
  pointer-events: none;
  animation: techGlow 15s ease-in-out infinite alternate;
}

@keyframes techGlow {
  0% { transform: translate(0, 0) scale(1); opacity: 0.5; }
  100% { transform: translate(-30px, 20px) scale(1.15); opacity: 0.8; }
}

/* ===== 布局 ===== */
.app-layout {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* ===== 侧边栏 ===== */
.sidebar {
  width: 240px;
  background: rgba(10, 22, 40, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255,143,0,0.06);
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  transition: width 0.25s ease;
}

.sidebar-header {
  padding: 20px 18px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}

.sidebar-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #e65100, #ff8f00);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
  box-shadow: 0 3px 10px rgba(255,143,0,0.3);
  flex-shrink: 0;
}

.sidebar-brand h2 {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.sidebar-sub {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 1px;
}

/* 用户信息 */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1565c0, #1e88e5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.user-role {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.3px;
}

/* 菜单 */
.sidebar-menu {
  flex: 1;
  padding: 10px 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.menu-label {
  padding: 14px 20px 6px;
  font-size: 10px;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 1.5px;
  font-weight: 600;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 18px;
  margin: 2px 10px;
  border-radius: var(--radius-sm);
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 14px;
  cursor: pointer;
}

.menu-item:hover {
  background: rgba(255,143,0,0.06);
  color: #fff;
}

.menu-item.router-link-active {
  background: rgba(255,143,0,0.1);
  color: var(--accent-warm-light);
  font-weight: 600;
  border-left: 3px solid var(--accent-warm);
  margin-left: 7px;
  padding-left: 15px;
}

.menu-item i {
  width: 20px;
  text-align: center;
  font-size: 15px;
}

.menu-logout {
  margin-top: auto;
  color: var(--text-muted);
}

.menu-logout:hover {
  background: rgba(229,57,53,0.08);
  color: #ef9a9a;
}

.sidebar-spacer {
  flex: 1;
}

/* ===== 主内容区 ===== */
.main-content {
  margin-left: 240px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* ===== 顶栏 ===== */
.topbar {
  background: rgba(13, 26, 52, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 0 28px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
}

.breadcrumb i {
  color: var(--accent-warm-light);
  font-size: 12px;
}

.bc-sep {
  color: rgba(255,255,255,0.1);
}

.bc-current {
  color: var(--text-light);
  font-weight: 500;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-time {
  font-size: 12px;
  color: var(--text-muted);
  font-family: "Consolas", monospace;
  letter-spacing: 0.5px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: default;
}

.user-badge {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  background: linear-gradient(135deg, #e65100, #ff8f00);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.user-name-top {
  font-size: 13px;
  color: var(--text);
  font-weight: 500;
}

/* ===== 内容区 ===== */
.content-area {
  padding: 24px 28px;
  flex: 1;
}

/* ===== 页面头部 ===== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.3px;
}

/* ===== 按钮 ===== */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
}

.btn i { font-size: 13px; }

.btn-primary {
  background: linear-gradient(135deg, #e65100, #ff8f00);
  color: #fff;
  box-shadow: 0 2px 8px rgba(255,143,0,0.2);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #bf360c, #e65100);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(255,143,0,0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-outline {
  background: transparent;
  color: var(--text-light);
  border: 1px solid var(--border);
}

.btn-outline:hover {
  border-color: var(--accent-warm);
  color: var(--accent-warm-light);
  background: rgba(255,143,0,0.04);
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

.btn-sm i { font-size: 12px; }

.btn-danger {
  background: rgba(229,57,53,0.9);
  color: #fff;
}

.btn-danger:hover {
  background: #c62828;
}

.btn-blue {
  background: linear-gradient(135deg, #1565c0, #1e88e5);
  color: #fff;
}

.btn-blue:hover {
  box-shadow: 0 4px 16px rgba(21,101,192,0.3);
  transform: translateY(-1px);
}

/* ===== 搜索/过滤栏 ===== */
.search-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.search-bar input,
.search-bar select {
  padding: 8px 14px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 38px;
}

.search-bar input { flex: 1; min-width: 180px; }

.search-bar input:focus,
.search-bar select:focus {
  border-color: var(--accent-warm);
  box-shadow: 0 0 0 2px var(--accent-warm-glow);
}

.search-bar select option {
  background: #162348;
  color: var(--text);
}

/* ===== 表格 ===== */
.table-wrap {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: rgba(255,143,0,0.04);
}

thead th {
  padding: 12px 14px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

tbody tr {
  border-bottom: 1px solid rgba(255,255,255,0.03);
  transition: background 0.15s;
}

tbody tr:last-child { border-bottom: none; }

tbody tr:hover {
  background: rgba(255,143,0,0.03);
}

tbody td {
  padding: 11px 14px;
  font-size: 13px;
  color: var(--text);
}

tbody td strong {
  color: #fff;
  font-weight: 600;
}

/* ===== 标签 ===== */
.tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.2px;
}

.tag-pending, .tag-pending-review, .tag-draft { background: rgba(255,152,0,0.15); color: #ffb74d; }
.tag-in_progress { background: rgba(33,150,243,0.15); color: #64b5f6; }
.tag-completed, .tag-approved, .tag-assessed, .tag-finished { background: rgba(76,175,80,0.15); color: #81c784; }
.tag-expired, .tag-rejected, .tag-cancelled, .tag-excluded { background: rgba(229,57,53,0.15); color: #ef9a9a; }
.tag-low, .tag-paused { background: rgba(33,150,243,0.12); color: #64b5f6; }
.tag-medium { background: rgba(255,152,0,0.12); color: #ffb74d; }
.tag-high { background: rgba(229,57,53,0.15); color: #ef9a9a; }
.tag-active, .tag-已通过 { background: rgba(76,175,80,0.12); color: #81c784; }

/* ===== 分页 ===== */
.pagination {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 14px;
  border-top: 1px solid var(--border);
}

.pagination button {
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-light);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.pagination button:hover:not(:disabled) {
  border-color: var(--accent-warm);
  color: var(--accent-warm-light);
}

.pagination button.active {
  background: rgba(255,143,0,0.1);
  border-color: var(--accent-warm);
  color: var(--accent-warm-light);
  font-weight: 600;
}

.pagination button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pagination span {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
}

/* ===== 空状态 ===== */
.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: var(--text-muted);
}

.empty-state i {
  font-size: 40px;
  color: var(--border);
  margin-bottom: 12px;
}

.empty-state p {
  font-size: 13px;
}

/* ===== 模态框 ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-box {
  background: rgba(17, 29, 54, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,143,0,0.1);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 520px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  animation: slideUp 0.25s ease;
  max-height: 90vh;
  overflow-y: auto;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px 14px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 22px;
  cursor: pointer;
  padding: 0 4px;
  transition: color 0.15s;
}

.modal-close:hover { color: #fff; }

.modal-body {
  padding: 20px 22px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 14px 22px 18px;
  border-top: 1px solid var(--border);
}

/* ===== 表单 ===== */
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-light);
  margin-bottom: 5px;
  letter-spacing: 0.2px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 9px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--accent-warm);
  box-shadow: 0 0 0 2px var(--accent-warm-glow);
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.form-group select option {
  background: #162348;
  color: var(--text);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

/* ===== 滚动条 ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .sidebar { width: 200px; }
  .main-content { margin-left: 200px; }
  .sidebar-user { display: none; }
  .topbar { padding: 0 14px; }
  .content-area { padding: 16px; }
  .form-row { grid-template-columns: 1fr; }
  .header-time, .user-name-top { display: none; }
}
</style>




