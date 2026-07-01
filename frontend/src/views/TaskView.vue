<template>
  <div>
    <div class="page-header">
      <h2>任务管理</h2>
      <button class="btn btn-primary" @click="openCreate"><i class="fas fa-plus"></i>创建任务</button>
    </div>
    <div class="search-bar">
      <select v-model="filterStatus" @change="loadTasks">
        <option value="">全部状态</option>
        <option value="draft">未开始</option>
        <option value="in_progress">进行中</option>
        <option value="paused">已暂停</option>
        <option value="finished">已结束</option>
        <option value="cancelled">已作废</option>
      </select>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>任务名称</th>
            <th>模板</th>
            <th>状态</th>
            <th>有效期限</th>
            <th>作答时长</th>
            <th>创建时间</th>
            <th style="width:64px">分享</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tasks" :key="t.id">
            <td><strong>{{ t.name }}</strong></td>
            <td>{{ t.template_name || '-' }}</td>
            <td><span class="tag" :class="'tag-' + t.status">{{ statusLabel(t.status) }}</span></td>
            <td>{{ t.valid_from?.slice(0,10) }} ~ {{ t.valid_until?.slice(0,10) }}</td>
            <td>{{ t.duration_minutes }}分钟</td>
            <td>{{ t.created_at?.slice(0,10) }}</td>
            <td>
              <button class="btn btn-sm btn-outline" @click="openShare(t)" title="分享测评链接"><i class="fas fa-share-alt"></i></button>
            </td>
          </tr>
          <tr v-if="tasks.length === 0">
            <td colspan="7"><div class="empty-state"><i class="fas fa-tasks"></i><p>暂无任务数据</p></div></td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page <= 1" @click="page = page - 1; loadTasks()">上一页</button>
        <button v-for="p in totalPages" :key="p" :class="{ active: p === page }" @click="page = p; loadTasks()">{{ p }}</button>
        <button :disabled="page >= totalPages" @click="page = page + 1; loadTasks()">下一页</button>
        <span>共 {{ total }} 条</span>
      </div>
    </div>

    <!-- Create Task Modal -->
    <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
      <div class="modal-box" style="max-width:640px">
        <div class="modal-header"><h3>创建测评任务</h3><button class="modal-close" @click="showCreate = false">&times;</button></div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group"><label>任务名称 *</label><input v-model="createForm.name" placeholder="如：2024年入职测评" /></div>
            <div class="form-group">
              <label>测评模板 *</label>
              <select v-model="createForm.template">
                <option value="">请选择模板</option>
                <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">{{ tpl.name }} ({{ tpl.total_questions }}题)</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>作答时长 (分钟)</label><input v-model.number="createForm.duration_minutes" type="number" placeholder="30" /></div>
            <div class="form-group"><label>有效天数</label><input v-model.number="createForm.valid_days" type="number" placeholder="7" /></div>
          </div>
          <div class="form-group"><label>任务描述</label><textarea v-model="createForm.description" placeholder="任务说明（选填）"></textarea></div>
          <div class="form-group">
            <label>选择员工（待测评）</label>
            <div class="employee-selector">
              <div class="emp-header">
                <span>可选员工 ({{ pendingEmployees.length }})</span>
                <button class="btn btn-sm btn-outline" @click="selectAll" type="button">全选</button>
              </div>
              <div class="emp-list">
                <label v-for="emp in pendingEmployees" :key="emp.id" class="emp-item" :class="{ selected: createForm.employee_ids.includes(emp.id) }">
                  <input type="checkbox" :value="emp.id" v-model="createForm.employee_ids" />
                  <span>{{ emp.name }} <em v-if="emp.position">{{ emp.position }}</em></span>
                </label>
                <div v-if="pendingEmployees.length === 0" class="empty-state" style="padding:16px"><p>无可选员工，请先在员工管理中添加</p></div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreate = false">取消</button>
          <button class="btn btn-primary" :disabled="creating" @click="doCreateTask">{{ creating ? '创建中...' : '创建任务并分配' }}</button>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <div class="modal-overlay" v-if="showShare" @click.self="showShare = false">
      <div class="modal-box" style="max-width:700px">
        <div class="modal-header"><h3>分享测评 — {{ shareTask?.name }}</h3><button class="modal-close" @click="showShare = false">&times;</button></div>
        <div class="modal-body">
          <div class="share-loading" v-if="loadingAssignments">加载中...</div>
          <div v-else-if="assignments.length === 0" class="empty-state"><i class="fas fa-users"></i><p>暂无员工分配</p></div>
          <div v-for="(a, idx) in assignments" :key="a.id" class="share-item">
            <div class="share-header"><strong>{{ a.employee_name }}</strong><span class="tag" :class="'tag-' + a.status">{{ assignStatusLabel(a.status) }}</span></div>
            <div class="share-body">
              <div class="share-link-row">
                <span class="share-label">测评链接：</span>
                <input class="share-link-input" :value="getAssessLink(a.access_code)" readonly @click="$event.target.select()" />
                <button class="btn btn-sm btn-outline" @click="copyLink(a.access_code)"><i class="fas fa-copy"></i></button>
              </div>
              <div class="share-qr-row">
                <span class="share-label">二维码：</span>
                <img :src="'https://api.qrserver.com/v1/create-qr-code/?size=130x130&data=' + encodeURIComponent(getAssessLink(a.access_code))" :alt="'二维码_' + a.employee_name" class="share-qr" />
              </div>
            </div>
            <div class="share-actions">
              <button class="btn btn-sm btn-outline" @click="copyNotification(a)"><i class="fas fa-envelope"></i> 复制通知消息</button>
            </div>
          </div>
        </div>
        <div class="modal-footer"><button class="btn btn-outline" @click="showShare = false">关闭</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const filterStatus = ref('')
const page = ref(1); const total = ref(0); const totalPages = ref(1)
const tasks = ref([]); const showShare = ref(false); const shareTask = ref(null)
const assignments = ref([]); const loadingAssignments = ref(false)
const showCreate = ref(false); const creating = ref(false)
const templates = ref([]); const pendingEmployees = ref([])
const createForm = ref({ name: '', template: '', duration_minutes: 30, valid_days: 7, description: '', employee_ids: [] })

function statusLabel(s) { return { draft: '未开始', in_progress: '进行中', paused: '已暂停', finished: '已结束', cancelled: '已作废' }[s] || s }
function assignStatusLabel(s) { return { pending: '待作答', in_progress: '作答中', completed: '已完成', expired: '已超时', invalid: '已作废' }[s] || s }
function getAssessLink(code) { return window.location.origin + '/assess/' + code }

function getNotificationText(a) {
  return `【智善TIC·人才测评通知】

${a.employee_name}，您好！请按以下步骤完成人才测评：

📌 第一步：点击测评链接进入
${getAssessLink(a.access_code)}

📌 第二步：填写姓名、手机号（必填）和面试岗位（选填）开始测评
（请使用本人真实手机号）

⏰ 请在规定时间内完成，测评约需15-20分钟。
如有疑问请联系人力资源中心。

——智善TIC生活集团 人力资源中心`
}

async function loadTasks() {
  try {
    const r = await api.get('/tasks/', { params: { page: page.value, status: filterStatus.value || undefined } })
    tasks.value = r.data.results || r.data; total.value = r.data.count || tasks.value.length; totalPages.value = Math.ceil(total.value / 20) || 1
  } catch (e) { console.error(e) }
}

async function openCreate() {
  showCreate.value = true; createForm.value = { name: '', template: '', duration_minutes: 30, valid_days: 7, description: '', employee_ids: [] }
  try {
    const [tr, er] = await Promise.all([api.get('/templates/'), api.get('/employees/', { params: { status: 'pending' } })])
    templates.value = tr.data.results || tr.data
    pendingEmployees.value = er.data.results || er.data
  } catch (e) { console.error(e) }
}

function selectAll() {
  if (createForm.value.employee_ids.length === pendingEmployees.value.length) createForm.value.employee_ids = []
  else createForm.value.employee_ids = pendingEmployees.value.map(e => e.id)
}

async function doCreateTask() {
  if (!createForm.value.name || !createForm.value.template) return
  creating.value = true
  try {
    const now = new Date()
    const until = new Date(now.getTime() + createForm.value.valid_days * 86400000)
    const taskR = await api.post('/tasks/', {
      name: createForm.value.name,
      template: createForm.value.template,
      duration_minutes: createForm.value.duration_minutes,
      valid_from: now.toISOString(),
      valid_until: until.toISOString(),
      description: createForm.value.description,
      status: 'in_progress'
    })
    if (createForm.value.employee_ids.length > 0) {
      await api.post(`/tasks/${taskR.data.id}/assign_employees/`, { employee_ids: createForm.value.employee_ids })
    }
    showCreate.value = false; loadTasks()
  } catch (e) { console.error(e) }
  finally { creating.value = false }
}

async function openShare(task) {
  shareTask.value = task; showShare.value = true; assignments.value = []; loadingAssignments.value = true
  try { const r = await api.get(`/tasks/${task.id}/assignments/`); assignments.value = r.data } catch (e) { console.error(e) }
  loadingAssignments.value = false
}

function copyLink(code) { navigator.clipboard.writeText(getAssessLink(code)).catch(() => {}) }
function copyNotification(a) { navigator.clipboard.writeText(getNotificationText(a)).catch(() => {}) }

onMounted(loadTasks)
</script>

<style scoped>
.share-item { background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-bottom: 12px }
.share-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px }
.share-header strong { color: #fff; font-size: 14px }
.share-body { margin-bottom: 8px }
.share-link-row { display: flex; align-items: center; gap: 6px; margin-bottom: 8px }
.share-label { font-size: 12px; color: var(--text-muted); white-space: nowrap; min-width: 64px }
.share-link-input { flex: 1; padding: 6px 8px; border: 1px solid var(--border); border-radius: 4px; background: rgba(255,255,255,0.03); color: var(--text); font-size: 12px; font-family: monospace }
.share-qr-row { display: flex; align-items: center; gap: 6px }
.share-qr { width: 130px; height: 130px; border: 1px solid var(--border); border-radius: 4px; background: #fff; padding: 4px }
.share-actions { display: flex; gap: 6px; margin-top: 6px }
.share-loading { color: var(--text-muted); padding: 20px; text-align: center }
.employee-selector { border: 1px solid var(--border); border-radius: 6px; overflow: hidden }
.emp-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255,255,255,0.02); font-size: 12px; color: var(--text-muted) }
.emp-list { max-height: 200px; overflow-y: auto }
.emp-item { display: flex; align-items: center; gap: 8px; padding: 8px 12px; cursor: pointer; font-size: 13px; color: var(--text) }
.emp-item:hover, .emp-item.selected { background: rgba(255,255,255,0.04) }
.emp-item em { color: var(--text-muted); font-size: 11px; margin-left: 6px }
.emp-item input { accent-color: var(--accent) }
</style>

