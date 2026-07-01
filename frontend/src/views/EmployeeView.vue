<template>
  <div>
    <div class="page-header">
      <h2>员工管理</h2>
      <button class="btn btn-primary" @click="openAdd"><i class="fas fa-plus"></i>添加员工</button>
    </div>
    <div class="search-bar">
      <input v-model="search" placeholder="搜索姓名/手机号..." @input="onSearch" />
      <select v-model="filterStatus" @change="loadEmployees">
        <option value="">全部状态</option>
        <option value="pending">待测评</option>
        <option value="assessed">已测评</option>
        <option value="excluded">已排除</option>
      </select>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>姓名</th>
            <th>性别</th>
            <th>年龄</th>
            <th>手机</th>
            <th>应聘岗位</th>
            <th>部门</th>
            <th>状态</th>
            <th>入职时间</th>
            <th style="width:90px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="emp in employees" :key="emp.id">
            <td><strong>{{ emp.name }}</strong></td>
            <td>{{ genderLabel(emp.gender) }}</td>
            <td>{{ emp.age ?? '-' }}</td>
            <td>{{ emp.phone || '-' }}</td>
            <td>{{ emp.position || '-' }}</td>
            <td>{{ emp.department || '-' }}</td>
            <td><span class="tag" :class="'tag-' + emp.status">{{ statusLabel(emp.status) }}</span></td>
            <td>{{ emp.entry_date || '-' }}</td>
            <td>
              <button class="btn btn-sm btn-outline" @click="openEdit(emp)"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-danger" @click="confirmDelete(emp)"><i class="fas fa-trash"></i></button>
            </td>
          </tr>
          <tr v-if="employees.length === 0">
            <td colspan="9">
              <div class="empty-state"><i class="fas fa-users"></i><p>暂无员工数据</p></div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page <= 1" @click="page = page - 1; loadEmployees()">上一页</button>
        <button v-for="p in totalPages" :key="p" :class="{ active: p === page }" @click="page = p; loadEmployees()">{{ p }}</button>
        <button :disabled="page >= totalPages" @click="page = page + 1; loadEmployees()">下一页</button>
        <span>共 {{ total }} 条</span>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ editing ? '编辑员工' : '添加员工' }}</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>姓名 *</label>
              <input v-model="form.name" placeholder="请输入姓名" />
            </div>
            <div class="form-group">
              <label>性别</label>
              <select v-model="form.gender">
                <option value="">请选择</option>
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="other">其他</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>年龄</label>
              <input v-model.number="form.age" type="number" placeholder="年龄" />
            </div>
            <div class="form-group">
              <label>手机</label>
              <input v-model="form.phone" placeholder="手机号" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>邮箱</label>
              <input v-model="form.email" placeholder="邮箱" />
            </div>
            <div class="form-group">
              <label>应聘岗位</label>
              <input v-model="form.position" placeholder="岗位名称" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>部门</label>
              <input v-model="form.department" placeholder="所属部门" />
            </div>
            <div class="form-group">
              <label>入职时间</label>
              <input v-model="form.entry_date" type="date" />
            </div>
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="form.notes" placeholder="备注信息"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="saveEmployee">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div class="modal-overlay" v-if="showDelete" @click.self="showDelete = false">
      <div class="modal-box" style="max-width:380px">
        <div class="modal-header"><h3>确认删除</h3></div>
        <div class="modal-body">
          <p>确定要删除员工 <strong>{{ deleting?.name }}</strong> 吗？此操作不可恢复。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showDelete = false">取消</button>
          <button class="btn btn-danger" :disabled="saving" @click="doDelete">{{ saving ? '删除中...' : '确认删除' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const search = ref('')
const filterStatus = ref('')
const page = ref(1)
const total = ref(0)
const totalPages = ref(1)
const employees = ref([])
const showModal = ref(false)
const showDelete = ref(false)
const editing = ref(false)
const saving = ref(false)
const deleting = ref(null)

const defaultForm = { name: '', gender: '', age: null, phone: '', email: '', position: '', department: '', entry_date: '', notes: '' }
const form = ref({ ...defaultForm })

let searchTimer = null

function genderLabel(g) {
  return { male: '男', female: '女', other: '其他' }[g] || '-'
}
function statusLabel(s) {
  return { pending: '待测评', assessed: '已测评', excluded: '已排除' }[s] || s
}

async function loadEmployees() {
  try {
    const params = { page: page.value }
    if (search.value) params.search = search.value
    if (filterStatus.value) params.status = filterStatus.value
    const r = await api.get('/employees/', { params })
    employees.value = r.data.results || r.data
    total.value = r.data.count || employees.value.length
    totalPages.value = Math.ceil(total.value / 20) || 1
  } catch (e) { console.error(e) }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; loadEmployees() }, 300)
}

function openAdd() {
  editing.value = false
  form.value = { ...defaultForm }
  showModal.value = true
}
function openEdit(emp) {
  editing.value = true
  form.value = { ...emp }
  showModal.value = true
}
async function saveEmployee() {
  if (!form.value.name) return
  saving.value = true
  try {
    if (editing.value) {
      await api.put(`/employees/${form.value.id}/`, form.value)
    } else {
      await api.post('/employees/', form.value)
    }
    showModal.value = false
    loadEmployees()
  } catch (e) { console.error(e) }
  finally { saving.value = false }
}
function confirmDelete(emp) {
  deleting.value = emp
  showDelete.value = true
}
async function doDelete() {
  saving.value = true
  try {
    await api.delete(`/employees/${deleting.value.id}/`)
    showDelete.value = false
    deleting.value = null
    loadEmployees()
  } catch (e) { console.error(e) }
  finally { saving.value = false }
}

onMounted(loadEmployees)
</script>
