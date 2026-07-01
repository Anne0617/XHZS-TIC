<template>
  <div class="change-pwd-page">
    <div class="pwd-card">
      <div class="pwd-header">
        <i class="fas fa-key"></i>
        <h2>????</h2>
        <p>??????????????</p>
      </div>
      <form @submit.prevent="handleChange" class="pwd-form">
        <div class="form-group">
          <label>????</label>
          <div class="input-wrapper">
            <i class="fas fa-lock input-icon"></i>
            <input v-model="oldPwd" type="password" placeholder="???????" required />
          </div>
        </div>
        <div class="form-group">
          <label>???</label>
          <div class="input-wrapper">
            <i class="fas fa-key input-icon"></i>
            <input v-model="newPwd" type="password" placeholder="??6???" required minlength="6" />
          </div>
        </div>
        <div class="form-group">
          <label>?????</label>
          <div class="input-wrapper">
            <i class="fas fa-check-circle input-icon"></i>
            <input v-model="confirmPwd" type="password" placeholder="???????" required minlength="6" />
          </div>
        </div>
        <div v-if="error" class="error-msg"><i class="fas fa-exclamation-circle"></i> {{ error }}</div>
        <div v-if="success" class="success-msg"><i class="fas fa-check-circle"></i> {{ success }}</div>
        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span><span v-else>????</span>
        </button>
        <button type="button" class="btn-back" @click="$router.push('/dashboard')">?????</button>
      </form>
    </div>
  </div>
</template>
<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
const router = useRouter()
const auth = useAuthStore()
const oldPwd = ref(""); const newPwd = ref(""); const confirmPwd = ref("")
const error = ref(""); const success = ref(""); const loading = ref(false)
async function handleChange() {
  error.value = ""; success.value = ""
  if (!oldPwd.value || !newPwd.value || !confirmPwd.value) { error.value = "???????"; return }
  if (newPwd.value.length < 6) { error.value = "?????6?"; return }
  if (newPwd.value !== confirmPwd.value) { error.value = "???????"; return }
  loading.value = true
  try {
    const r = await auth.changePassword(oldPwd.value, newPwd.value)
    success.value = "???????"
    oldPwd.value = ""; newPwd.value = ""; confirmPwd.value = ""
    setTimeout(() => router.push("/dashboard"), 2000)
  } catch (e) {
    error.value = e.response?.data?.error || "????????"
  } finally { loading.value = false }
}
</script>
<style scoped>
.change-pwd-page { min-height:100vh; display:flex; align-items:center; justify-content:center; background:#f0f2f5; }
.pwd-card { background:#fff; border-radius:12px; padding:40px; width:420px; box-shadow:0 2px 12px rgba(0,0,0,.08); }
.pwd-header { text-align:center; margin-bottom:32px; }
.pwd-header i { font-size:40px; color:#1565c0; margin-bottom:8px; }
.pwd-header h2 { margin:0; font-size:22px; color:#1a1a2e; }
.pwd-header p { margin:6px 0 0; color:#888; font-size:14px; }
.form-group { margin-bottom:20px; }
.form-group label { display:block; margin-bottom:6px; font-size:14px; font-weight:500; color:#333; }
.input-wrapper { position:relative; }
.input-wrapper input { width:100%; padding:10px 12px 10px 36px; border:1px solid #d9d9d9; border-radius:8px; font-size:14px; box-sizing:border-box; }
.input-wrapper input:focus { border-color:#1565c0; outline:none; box-shadow:0 0 0 2px rgba(21,101,192,.15); }
.input-icon { position:absolute; left:12px; top:50%; transform:translateY(-50%); color:#bbb; font-size:14px; }
.error-msg { background:#fff2f0; border:1px solid #ffccc7; border-radius:6px; padding:8px 12px; margin-bottom:16px; color:#cf1322; font-size:13px; display:flex; align-items:center; gap:6px; }
.success-msg { background:#f6ffed; border:1px solid #b7eb8f; border-radius:6px; padding:8px 12px; margin-bottom:16px; color:#389e0d; font-size:13px; display:flex; align-items:center; gap:6px; }
.btn-submit { width:100%; padding:10px; background:linear-gradient(135deg,#1565c0,#1e88e5); color:#fff; border:none; border-radius:8px; font-size:15px; cursor:pointer; margin-top:4px; }
.btn-submit:disabled { opacity:.6; cursor:not-allowed; }
.btn-back { width:100%; padding:10px; background:#fff; color:#666; border:1px solid #d9d9d9; border-radius:8px; font-size:14px; cursor:pointer; margin-top:10px; }
.btn-back:hover { border-color:#1565c0; color:#1565c0; }
.spinner { display:inline-block; width:16px; height:16px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; }
@keyframes spin { to { transform:rotate(360deg) } }
</style>