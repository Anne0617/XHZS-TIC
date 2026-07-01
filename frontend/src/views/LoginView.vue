<template>
  <div class="login-page">
    <div class="login-bg-pattern"></div>
    
    <div class="login-container">
      <!-- 左侧品牌展示区 -->
      <div class="login-brand">
        <div class="brand-content">
          <div class="brand-lockup">
            <div class="brand-icon">
              <i class="fas fa-star"></i>
            </div>
            <h1 class="brand-name">智善 TIC</h1>
          </div>
          <p class="brand-tagline">三级架构 · 全面覆盖</p>
          <div class="hierarchy-badges">
            <span class="hc-badge"><i class="fas fa-crown"></i> 本部</span>
            <span class="hc-arrow"><i class="fas fa-chevron-right"></i></span>
            <span class="hc-badge"><i class="fas fa-building"></i> 分公司</span>
            <span class="hc-arrow"><i class="fas fa-chevron-right"></i></span>
            <span class="hc-badge"><i class="fas fa-folder"></i> 项目</span>
          </div>
          <div class="brand-features">
            <div class="feature-item">
              <i class="fas fa-user-check"></i>
              <span>Talent · 聚焦人才</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-chart-line"></i>
              <span>Insight · 深度洞察</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-clipboard-check"></i>
              <span>Check · 科学测评</span>
            </div>
          </div>
        </div>
        <div class="brand-footer">
          <p>让人才管理有依据、可衡量</p>
        </div>
      </div>

      <!-- 右侧登录卡片 -->
      <div class="login-card">
        <div class="card-header">
          <h2>管理登录</h2>
          <p class="card-desc">请输入您的管理员账号</p>
        </div>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input id="username" v-model="username" type="text" placeholder="请输入用户名" required />
            </div>
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input id="password" v-model="password" type="password" placeholder="请输入密码" required />
              <button type="button" class="toggle-pwd" @click="showPwd = !showPwd" tabindex="-1">
                <i :class="showPwd ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" v-model="remember" />
              <span>记住登录</span>
            </label>
          </div>
          <div v-if="error" class="error-msg">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ error }}</span>
          </div>
          <button type="submit" class="btn-login" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>登 录</span>
          </button>
        </form>
        <div class="card-footer">
          <p>智善 TIC 人才测评体系 v1.0 — 三级权限架构</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const username = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)
const remember = ref(false)
const showPwd = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function handleLogin() {
  if (!username.value || !password.value) { error.value = "请输入用户名和密码"; return }
  loading.value = true; error.value = ""
  try {
    await auth.login(username.value, password.value)
    router.push("/dashboard")
  } catch (e) {
    error.value = "用户名或密码错误"
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #0a1628;
  position: relative;
  overflow: hidden;
}
.login-bg-pattern {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 10% 90%, rgba(198,40,40,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 70% 50% at 90% 10%, rgba(198,40,40,0.05) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 50% 50%, rgba(255,255,255,0.02) 0%, transparent 60%);
  pointer-events: none;
}
.login-container {
  display: flex;
  position: relative;
  z-index: 1;
  width: 880px;
  max-width: 94vw;
  min-height: 560px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04);
}
.login-brand {
  flex: 1;
  background: linear-gradient(145deg, #101c36, #0d1a34, #121e38);
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}
.login-brand::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -30%;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(198,40,40,0.08) 0%, transparent 70%);
  pointer-events: none;
}
.login-brand::after {
  content: '';
  position: absolute;
  bottom: -20%;
  left: -20%;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
  pointer-events: none;
}
.brand-content { position: relative; z-index: 1; }
.brand-lockup { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.brand-icon {
  width: 48px; height: 48px; border-radius: 12px;
  background: linear-gradient(135deg, #c62828, #e53935);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; color: #fff;
  box-shadow: 0 4px 12px rgba(198,40,40,0.3);
}
.brand-name { font-size: 26px; font-weight: 700; color: #fff; letter-spacing: 1px; }
.brand-tagline { font-size: 15px; color: rgba(255,255,255,0.5); margin-bottom: 40px; padding-left: 2px; letter-spacing: 0.5px; }
.brand-features { display: flex; flex-direction: column; gap: 18px; }
.feature-item { display: flex; align-items: center; gap: 14px; color: rgba(255,255,255,0.6); font-size: 14px; transition: color 0.2s; }
.feature-item i { width: 20px; color: #c62828; font-size: 15px; text-align: center; }
.feature-item:hover { color: rgba(255,255,255,0.85); }
.brand-footer { position: relative; z-index: 1; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); }
.brand-footer p { font-size: 13px; color: rgba(255,255,255,0.3); letter-spacing: 0.3px; }
.login-card { width: 400px; background: #111c36; padding: 48px 40px; display: flex; flex-direction: column; justify-content: center; }
.card-header { margin-bottom: 36px; }
.card-header h2 { font-size: 22px; font-weight: 700; color: #e8eaf6; margin-bottom: 6px; }
.card-desc { font-size: 13px; color: rgba(255,255,255,0.35); }
.login-form { flex: 1; display: flex; flex-direction: column; }
.form-group { margin-bottom: 22px; }
.form-group label { display: block; font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.5); margin-bottom: 6px; letter-spacing: 0.3px; }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-wrapper input {
  width: 100%; padding: 12px 12px 12px 40px;
  border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;
  background: rgba(255,255,255,0.03); color: #e8eaf6; font-size: 14px;
  transition: all 0.2s ease; outline: none;
}
.input-wrapper input::placeholder { color: rgba(255,255,255,0.2); }
.input-wrapper input:focus { border-color: #c62828; background: rgba(255,255,255,0.05); box-shadow: 0 0 0 3px rgba(198,40,40,0.1); }
.input-icon { position: absolute; left: 13px; color: rgba(255,255,255,0.2); font-size: 14px; z-index: 1; pointer-events: none; }
.input-wrapper input:focus ~ .input-icon { color: #c62828; }
.toggle-pwd { position: absolute; right: 10px; background: none; border: none; color: rgba(255,255,255,0.2); cursor: pointer; padding: 4px; font-size: 14px; transition: color 0.2s; }
.toggle-pwd:hover { color: rgba(255,255,255,0.5); }
.form-options { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.remember-me { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px; color: rgba(255,255,255,0.4); }
.remember-me input { accent-color: #c62828; width: 14px; height: 14px; }
.error-msg { display: flex; align-items: center; gap: 8px; background: rgba(229,57,53,0.12); color: #ef9a9a; padding: 10px 14px; border-radius: 8px; margin-bottom: 16px; font-size: 13px; border: 1px solid rgba(229,57,53,0.15); }
.error-msg i { font-size: 15px; flex-shrink: 0; }
.btn-login {
  width: 100%; padding: 13px;
  background: linear-gradient(135deg, #c62828, #e53935); color: #fff;
  border: none; border-radius: 8px; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.2s ease; letter-spacing: 2px;
  margin-top: 8px; display: flex; align-items: center; justify-content: center; min-height: 44px;
}
.btn-login:hover { background: linear-gradient(135deg, #b71c1c, #c62828); box-shadow: 0 4px 16px rgba(198,40,40,0.3); transform: translateY(-1px); }
.btn-login:active { transform: translateY(0); }
.btn-login:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
.spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.card-footer { margin-top: auto; padding-top: 24px; }
.card-footer p { font-size: 11px; color: rgba(255,255,255,0.2); text-align: center; letter-spacing: 0.3px; }
.hierarchy-badges {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 36px;
  flex-wrap: wrap;
}
.hc-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.6);
}
.hc-badge i { font-size: 11px; }
.hc-arrow { color: rgba(255,255,255,0.15); font-size: 10px; }
.hc-badge:first-child i { color: #ff8f00; }
.hc-badge:nth-child(3) i { color: #64b5f6; }
.hc-badge:last-child i { color: #81c784; }

@media (max-width: 768px) {
  .login-brand { display: none; }
  .login-card { width: 100%; padding: 40px 28px; }
  .login-container { max-width: 100%; min-height: auto; border-radius: 0; box-shadow: none; background: #111c36; }
  .login-page { align-items: flex-start; padding-top: 40px; }
}
</style>

