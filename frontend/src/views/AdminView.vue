<template>
  <div>
    <div class="page-header"><h2>管理员账号</h2><button class="btn btn-primary" @click="openAdd"><i class="fas fa-plus"></i>添加管理员</button></div>
    <div class="table-wrap"><table><thead><tr><th>用户名</th><th>姓名</th><th>所属分公司</th><th>状态</th><th style="width:130px">操作</th></tr></thead>
      <tbody>
        <tr v-for="a in admins" :key="a.id"><td><strong>{{ a.username }}</strong></td><td>{{ a.first_name || '-' }}</td><td>{{ a.branch_name || '-' }}</td>
          <td><span class="tag" :class="a.is_locked?'tag-danger':'tag-approved'">{{ a.is_locked ? '已冻结' : '正常' }}</span></td>
          <td>
            <button class="btn btn-sm btn-warning" @click="toggleLock(a)" :title="a.is_locked?'解冻':'冻结'"><i :class="a.is_locked?'fas fa-unlock':'fas fa-lock'"></i></button>
            <button class="btn btn-sm btn-outline" @click="resetPwd(a)" title="重置密码"><i class="fas fa-key"></i></button>
          </td></tr>
        <tr v-if="admins.length===0"><td colspan="5"><div class="empty-state"><i class="fas fa-user-shield"></i><p>暂无管理员</p></div></td></tr>
      </tbody></table></div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal=false">
      <div class="modal-box"><div class="modal-header"><h3>添加管理员</h3><button class="modal-close" @click="showModal=false">&times;</button></div>
        <div class="modal-body">
          <div class="form-row"><div class="form-group"><label>用户名 *</label><input v-model="form.username" placeholder="登录账号" /></div>
            <div class="form-group"><label>密码 *</label><input v-model="form.password" type="password" placeholder="初始密码" /></div></div>
          <div class="form-group"><label>姓名</label><input v-model="form.first_name" placeholder="管理员姓名" /></div>
          <div class="form-group"><label>所属分公司</label>
            <select v-model="form.branch"><option value="">请选择</option><option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option></select></div>
          <div class="form-row">
            <label class="emp-item"><input type="checkbox" v-model="form.can_manage_questions" /><span>题库管理</span></label>
            <label class="emp-item"><input type="checkbox" v-model="form.can_manage_tasks" /><span>任务管理</span></label>
            <label class="emp-item"><input type="checkbox" v-model="form.can_view_data" /><span>查看数据</span></label>
            <label class="emp-item"><input type="checkbox" v-model="form.can_export_data" /><span>导出数据</span></label>
            <label class="emp-item"><input type="checkbox" v-model="form.can_manage_employees" /><span>员工管理</span></label>
          </div>
        </div>
        <div class="modal-footer"><button class="btn btn-outline" @click="showModal=false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="saveAdmin">{{ saving?'保存中...':'保存' }}</button></div></div></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import api from '@/api'
const admins=ref([]); const branches=ref([]); const showModal=ref(false); const saving=ref(false)
const form=ref({username:'',password:'',first_name:'',branch:''})
const defPerms={can_manage_questions:true,can_manage_tasks:true,can_view_data:true,can_export_data:false,can_manage_employees:true}
async function load(){try{const[aR,bR]=await Promise.all([api.get('/admins/'),api.get('/branches/')]);admins.value=aR.data.results||aR.data;branches.value=bR.data.results||bR.data}catch(e){console.error(e)}}
function openAdd(){form.value={...defPerms,username:'',password:'',first_name:'',branch:''};showModal.value=true}
async function saveAdmin(){if(!form.value.username||!form.value.password)return;saving.value=true;try{await api.post('/admins/',{...form.value,role:'hr_admin'});showModal.value=false;load()}catch(e){console.error(e)}finally{saving.value=false}}
async function toggleLock(a){try{const r=await api.post(`/admins/${a.id}/toggle_lock/`);a.is_locked=r.data.is_locked;a.is_active=!r.data.is_locked;load()}catch(e){console.error(e)}}
async function resetPwd(a){const pw=prompt('输入新密码：','hr123456');if(!pw)return;try{await api.post(`/admins/${a.id}/reset_password/`,{password:pw})}catch(e){console.error(e)}}
onMounted(load)
</script>
<style scoped>.emp-item{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text)}</style>
