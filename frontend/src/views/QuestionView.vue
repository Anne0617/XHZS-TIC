<template>
  <div>
    <div class="page-header">
      <h2>题目管理</h2>
    </div>
    <div class="search-bar">
      <input v-model="search" placeholder="搜索题目内容..." @input="onSearch" />
      <select v-model="filterCategory" @change="loadQuestions">
        <option value="">全部维度</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>
      <select v-model="filterType" @change="loadQuestions">
        <option value="">全部题型</option>
        <option value="single">单选题</option>
        <option value="multiple">多选题</option>
        <option value="likert5">量表题(5级)</option>
        <option value="likert7">量表题(7级)</option>
      </select>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th style="width:40%">题目内容</th>
            <th>所属维度</th>
            <th>题型</th>
            <th>分值</th>
            <th>审核状态</th>
            <th>启用</th>
            <th>创建时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="q in questions" :key="q.id">
            <td><span :title="q.text">{{ truncate(q.text, 60) }}</span></td>
            <td>{{ q.category_name }}</td>
            <td>{{ typeLabel(q.question_type) }}</td>
            <td>{{ q.score }}</td>
            <td><span class="tag" :class="'tag-' + reviewClass(q.review_status)">{{ reviewLabel(q.review_status) }}</span></td>
            <td>
              <span class="tag" :class="q.is_active ? 'tag-approved' : 'tag-rejected'" style="cursor:pointer" @click="toggleActive(q)">
                {{ q.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ q.created_at?.slice(0, 10) }}</td>
          </tr>
          <tr v-if="questions.length === 0">
            <td colspan="7">
              <div class="empty-state"><i class="fas fa-question-circle"></i><p>暂无题目数据</p></div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page <= 1" @click="page = page - 1; loadQuestions()">上一页</button>
        <button v-for="p in totalPages" :key="p" :class="{ active: p === page }" @click="page = p; loadQuestions()">{{ p }}</button>
        <button :disabled="page >= totalPages" @click="page = page + 1; loadQuestions()">下一页</button>
        <span>共 {{ total }} 条</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const search = ref('')
const filterCategory = ref('')
const filterType = ref('')
const page = ref(1)
const total = ref(0)
const totalPages = ref(1)
const questions = ref([])
const categories = ref([])

let searchTimer = null

function truncate(t, n) { return t?.length > n ? t.slice(0, n) + '...' : t }
function typeLabel(t) {
  return { single: '单选题', multiple: '多选题', likert5: '量表题(5级)', likert7: '量表题(7级)' }[t] || t
}
function reviewLabel(s) {
  return { pending: '待审核', approved: '已通过', rejected: '已驳回' }[s] || s
}
function reviewClass(s) {
  return { pending: 'pending-review', approved: 'approved', rejected: 'rejected' }[s] || ''
}

async function loadQuestions() {
  try {
    const params = { page: page.value }
    if (search.value) params.search = search.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterType.value) params.type = filterType.value
    const r = await api.get('/questions/', { params })
    questions.value = r.data.results || r.data
    total.value = r.data.count || questions.value.length
    totalPages.value = Math.ceil(total.value / 20) || 1
  } catch (e) { console.error(e) }
}

async function loadCategories() {
  try {
    const r = await api.get('/categories/')
    categories.value = r.data.results || r.data
  } catch (e) {
    // categories might not have a dedicated endpoint; try extracting from questions
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; loadQuestions() }, 300)
}

async function toggleActive(q) {
  try {
    await api.put(`/questions/${q.id}/`, { ...q, is_active: !q.is_active })
    q.is_active = !q.is_active
  } catch (e) { console.error(e) }
}

onMounted(() => { loadCategories(); loadQuestions() })
</script>
