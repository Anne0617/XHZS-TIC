<template>
  <div class="template-manager">
    <div class="toolbar">
      <h2><i class="fas fa-file-alt"></i> 试卷管理</h2>
      <button class="btn-add" @click="showForm = true; editing = null; form = {name:'',description:'',exam_type:'',target_position:'',estimated_minutes:30,is_active:true}">
        <i class="fas fa-plus"></i> 新建试卷
      </button>
    </div>

    <div class="card" v-if="showForm">
      <h3>{{ editing ? "编辑试卷" : "新建试卷" }}</h3>
      <div class="form-grid">
        <div class="form-group"><label>试卷名称 <span class="req">*</span></label>
          <input v-model="form.name" placeholder="如：2024年度综合测评" /></div>
        <div class="form-group"><label>考试类型</label>
          <select v-model="form.exam_type">
            <option value="">选择题库分类</option>
            <option value="comprehensive">综合评估</option>
            <option value="bigfive">大五人格</option>
            <option value="pdp">PDP性格</option>
            <option value="mbti">MBTI人格</option>
          </select></div>
        <div class="form-group"><label>适用岗位</label>
          <input v-model="form.target_position" placeholder="如：通用/销售/技术" /></div>
        <div class="form-group"><label>预计用时(分钟)</label>
          <input type="number" v-model.number="form.estimated_minutes" /></div>
        <div class="form-group" style="grid-column:1/-1"><label>描述</label>
          <textarea v-model="form.description" rows="2"></textarea></div>
      </div>
      <div class="form-actions">
        <button class="btn-save" @click="saveTemplate"><i class="fas fa-save"></i> 保存</button>
        <button class="btn-cancel" @click="showForm = false">取消</button>
      </div>
    </div>

    <div class="card">
      <div class="search-bar"><input v-model="search" placeholder="搜索试卷..." @input="loadTemplates" /></div>
      <table><thead><tr>
        <th>名称</th><th>类型</th><th>题目数</th><th>用时</th><th>状态</th><th>操作</th>
      </tr></thead><tbody>
        <tr v-for="t in templates" :key="t.id">
          <td><strong>{{ t.name }}</strong><br><small>{{ t.description }}</small></td>
          <td>{{ t.exam_type || "-" }}</td>
          <td>{{ t.total_questions || 0 }}</td>
          <td>{{ t.estimated_minutes }}分钟</td>
          <td><span :class="t.is_active ? 'badge-on' : 'badge-off'">{{ t.is_active ? "启用" : "停用" }}</span></td>
          <td class="actions">
            <button class="btn-sm" @click="editTemplate(t)"><i class="fas fa-edit"></i></button>
            <button class="btn-sm btn-danger" @click="deleteTemplate(t)"><i class="fas fa-trash"></i></button>
          </td>
        </tr>
        <tr v-if="templates.length === 0"><td colspan="6" style="text-align:center;color:#999">暂无试卷数据</td></tr>
      </tbody></table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const templates = ref([])
const showForm = ref(false)
const editing = ref(null)
const search = ref('')
const form = ref({})

async function loadTemplates() {
  const r = await api.get('/templates/', { params: { search: search.value } })
  templates.value = r.data.results || r.data
}

async function saveTemplate() {
  if (!form.value.name) return alert("请填写试卷名称")
  if (editing.value) {
    await api.put(`/templates/${editing.value.id}/`, form.value)
  } else {
    await api.post('/templates/', form.value)
  }
  showForm.value = false
  loadTemplates()
  alert("保存成功！")
}

function editTemplate(t) {
  editing.value = t
  form.value = { ...t }
  showForm.value = true
}

async function deleteTemplate(t) {
  if (!confirm(`确定删除试卷"${t.name}"？`)) return
  await api.delete(`/templates/${t.id}/`)
  loadTemplates()
}

onMounted(loadTemplates)
</script>

<style scoped>
.template-manager{padding:20px}.toolbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.toolbar h2{color:#3a5a8a}.btn-add{padding:10px 20px;background:#4a6fa5;color:#fff;border:none;border-radius:6px;cursor:pointer}
.card{background:#fff;border-radius:10px;padding:20px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.form-group label{display:block;font-size:13px;color:#455a64;margin-bottom:4px}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:10px;border:2px solid #e0e4e8;border-radius:8px;font-size:14px}
.form-group textarea{resize:vertical}
.req{color:#e74c3c}.form-actions{display:flex;gap:10px;margin-top:16px}
.btn-save{padding:10px 24px;background:#27ae60;color:#fff;border:none;border-radius:6px;cursor:pointer}
.btn-cancel{padding:10px 24px;background:#eee;border:none;border-radius:6px;cursor:pointer}
.search-bar{margin-bottom:16px}.search-bar input{width:100%;padding:10px 14px;border:2px solid #e0e4e8;border-radius:8px}
table{width:100%;border-collapse:collapse}th{text-align:left;padding:10px 8px;border-bottom:2px solid #eee;color:#7f8c9b;font-size:13px}
td{padding:10px 8px;border-bottom:1px solid #f0f2f5;font-size:14px}td small{color:#999;font-size:12px}
.badge-on{background:#e8f5e9;color:#27ae60;padding:2px 10px;border-radius:10px;font-size:12px}
.badge-off{background:#fbe9e7;color:#e74c3c;padding:2px 10px;border-radius:10px;font-size:12px}
.actions{display:flex;gap:6px}.btn-sm{padding:6px 10px;border:1px solid #ddd;border-radius:4px;cursor:pointer;background:#fff}
.btn-danger{color:#e74c3c;border-color:#e74c3c}
@media(max-width:600px){.form-grid{grid-template-columns:1fr}}
</style>
