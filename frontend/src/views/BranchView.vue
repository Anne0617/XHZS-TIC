<template>
  <div>
    <div class="page-header"><h2>分公司管理</h2><button class="btn btn-primary" @click="openAdd"><i class="fas fa-plus"></i>添加分公司</button></div>
    <div class="table-wrap"><table><thead><tr><th>名称</th><th>编码</th><th>联系电话</th><th>地址</th><th style="width:70px">操作</th></tr></thead>
      <tbody>
        <tr v-for="b in branches" :key="b.id"><td><strong>{{ b.name }}</strong></td><td>{{ b.code }}</td><td>{{ b.contact_phone || '-' }}</td><td>{{ b.address || '-' }}</td>
          <td><button class="btn btn-sm btn-danger" @click="confirmDelete(b)"><i class="fas fa-trash"></i></button></td></tr>
        <tr v-if="branches.length===0"><td colspan="5"><div class="empty-state"><i class="fas fa-building"></i><p>暂无分公司</p></div></td></tr>
      </tbody></table></div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal=false">
      <div class="modal-box"><div class="modal-header"><h3>添加分公司</h3><button class="modal-close" @click="showModal=false">&times;</button></div>
        <div class="modal-body">
          <div class="form-row"><div class="form-group"><label>名称 *</label><input v-model="form.name" placeholder="分公司名称" /></div>
            <div class="form-group"><label>编码 *</label><input v-model="form.code" placeholder="唯一编码，如 BJ" /></div></div>
          <div class="form-row"><div class="form-group"><label>联系电话</label><input v-model="form.contact_phone" placeholder="联系电话" /></div>
            <div class="form-group"><label>地址</label><input v-model="form.address" placeholder="详细地址" /></div></div>
        </div>
        <div class="modal-footer"><button class="btn btn-outline" @click="showModal=false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="saveBranch">{{ saving?'保存中...':'保存' }}</button></div></div></div>

    <div class="modal-overlay" v-if="showDelete" @click.self="showDelete=false">
      <div class="modal-box" style="max-width:380px"><div class="modal-header"><h3>确认删除</h3></div>
        <div class="modal-body"><p>确定要删除分公司 <strong>{{ deleting?.name }}</strong> 吗？</p></div>
        <div class="modal-footer"><button class="btn btn-outline" @click="showDelete=false">取消</button>
          <button class="btn btn-danger" :disabled="saving" @click="doDelete">{{ saving?'删除中...':'确认删除' }}</button></div></div></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import api from '@/api'
const branches=ref([]); const showModal=ref(false); const showDelete=ref(false); const saving=ref(false); const deleting=ref(null)
const form=ref({name:'',code:'',contact_phone:'',address:''})
async function load(){try{const r=await api.get('/branches/');branches.value=r.data.results||r.data}catch(e){console.error(e)}}
function openAdd(){form.value={name:'',code:'',contact_phone:'',address:''};showModal.value=true}
async function saveBranch(){if(!form.value.name||!form.value.code)return;saving.value=true;try{await api.post('/branches/',form.value);showModal.value=false;load()}catch(e){console.error(e)}finally{saving.value=false}}
function confirmDelete(b){deleting.value=b;showDelete.value=true}
async function doDelete(){saving.value=true;try{await api.delete(`/branches/${deleting.value.id}/`);showDelete.value=false;deleting.value=null;load()}catch(e){console.error(e)}finally{saving.value=false}}
onMounted(load)
</script>
