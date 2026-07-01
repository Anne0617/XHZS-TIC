<template>
  <div>
    <div class="page-header">
      <h2>项目管理</h2>
      <button class="btn btn-primary" @click="openAdd"><i class="fas fa-plus"></i>添加项目</button>
    </div>

    <div class="search-bar">
      <select v-model="filterBranch" @change="loadProjects">
        <option value="">全部分公司</option>
        <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>项目名称</th>
            <th>代码</th>
            <th>所属分公司</th>
            <th>联系电话</th>
            <th>地址</th>
            <th>状态</th>
            <th>创建时间</th>
            <th style="width:80px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in projects" :key="p.id">
            <td><strong>{{ p.name }}</strong></td>
            <td><code>{{ p.code }}</code></td>
            <td>{{ p.branch_name || "-" }}</td>
            <td>{{ p.contact_phone || "-" }}</td>
            <td>{{ p.address || "-" }}</td>
            <td><span class="tag" :class="p.is_active ? 'tag-approved' : 'tag-rejected'">{{ p.is_active ? "启用" : "停用" }}</span></td>
            <td>{{ p.created_at?.slice(0, 10) || "-" }}</td>
            <td>
              <button class="btn btn-sm btn-outline" @click="openEdit(p)"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-danger" @click="confirmDelete(p)"><i class="fas fa-trash"></i></button>
            </td>
          </tr>
          <tr v-if="projects.length === 0">
            <td colspan="8"><div class="empty-state"><i class="fas fa-folder-tree"></i><p>暂无项目数据</p></div></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false">
      <div class="modal-box" style="max-width:480px">
        <div class="modal-header">
          <h3>{{ editing ? "编辑项目" : "添加项目" }}</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>项目名称 *</label>
            <input v-model="form.name" placeholder="如：深圳-人力资源项目" />
          </div>
          <div class="form-group">
            <label>项目代码 *</label>
            <input v-model="form.code" placeholder="如 SZ-HR" />
          </div>
          <div class="form-group">
            <label>所属分公司 *</label>
            <select v-model="form.branch">
              <option value="">请选择</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group"><label>联系电话</label><input v-model="form.contact_phone" placeholder="电话" /></div>
            <div class="form-group"><label>排序</label><input v-model.number="form.sort_order" type="number" placeholder="0" /></div>
          </div>
          <div class="form-group"><label>地址</label><input v-model="form.address" placeholder="地址（选填）" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="saveProject">{{ saving ? "保存中..." : "保存" }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div class="modal-overlay" v-if="showDelete" @click.self="showDelete = false">
      <div class="modal-box" style="max-width:380px">
        <div class="modal-header"><h3>确认删除</h3></div>
        <div class="modal-body"><p>确定要删除项目 <strong>{{ deleting?.name }}</strong> 吗？</p></div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showDelete = false">取消</button>
          <button class="btn btn-danger" :disabled="saving" @click="doDelete">{{ saving ? "删除中..." : "确认删除" }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"

const projects = ref([])
const branches = ref([])
const filterBranch = ref("")
const showModal = ref(false)
const showDelete = ref(false)
const editing = ref(false)
const saving = ref(false)
const deleting = ref(null)

const form = ref({ name: "", code: "", branch: "", contact_phone: "", address: "", sort_order: 0 })
const defaultForm = () => ({ name: "", code: "", branch: "", contact_phone: "", address: "", sort_order: 0 })

function openAdd() { editing.value = false; form.value = defaultForm(); showModal.value = true }
function openEdit(p) { editing.value = true; form.value = { ...p }; showModal.value = true }
function confirmDelete(p) { deleting.value = p; showDelete.value = true }

async function loadProjects() {
  try {
    const params = {}
    if (filterBranch.value) params.branch = filterBranch.value
    const r = await api.get("/projects/", { params })
    projects.value = r.data.results || r.data
  } catch (e) { console.error(e) }
}

async function loadBranches() {
  try { const r = await api.get("/branches/"); branches.value = r.data.results || r.data } catch (e) {}
}

async function saveProject() {
  if (!form.value.name || !form.value.code || !form.value.branch) return
  saving.value = true
  try {
    const payload = { ...form.value }
    if (editing.value) { await api.put(`/projects/${form.value.id}/`, payload) }
    else { await api.post("/projects/", payload) }
    showModal.value = false; loadProjects()
  } catch (e) { console.error(e) } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try { await api.delete(`/projects/${deleting.value.id}/`); showDelete.value = false; loadProjects() }
  catch (e) { console.error(e) } finally { saving.value = false }
}

onMounted(() => { loadProjects(); loadBranches() })
</script>
