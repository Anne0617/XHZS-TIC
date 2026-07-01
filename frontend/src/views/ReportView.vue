<template>
  <div>
    <div class="page-header">
      <h2>评估报告</h2>
      <button class="btn-export" @click="exportExcel"><i class="fas fa-download"></i> 导出Excel</button>
    </div>
    <div class="search-bar">
      <select v-model="filterRisk" @change="loadResults">
        <option value="">全部风险等级</option>
        <option value="low">健康</option>
        <option value="medium">有风险</option>
        <option value="high">有风险</option>
      </select>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>员工</th>
            <th>任务</th>
            <th>总分</th>
            <th>得分率</th>
            <th>风险等级</th>
            <th>岗位适配度</th>
            <th>评估时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in results" :key="r.id">
            <td><strong>{{ r.employee_name || '-' }}</strong></td>
            <td>{{ r.task_name || '-' }}</td>
            <td>{{ r.total_score }} / {{ r.max_score }}</td>
            <td>{{ r.score_percent }}%</td>
            <td><span class="tag" :class="'tag-' + r.risk_level">{{ riskLabel(r.risk_level) }}</span></td>
            <td>{{ r.fit_score ?? '-' }}</td>
            <td>{{ r.generated_at?.slice(0,10) }}</td>
            <td>
              <button class="btn-pdf" @click="downloadPdf(r.id)">下载 PDF</button>
            </td>
          </tr>
          <tr v-if="results.length === 0">
            <td colspan="8">
              <div class="empty-state"><i class="fas fa-file-alt"></i><p>暂无评估报告</p></div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page <= 1" @click="page = page - 1; loadResults()">上一页</button>
        <button v-for="p in totalPages" :key="p" :class="{ active: p === page }" @click="page = p; loadResults()">{{ p }}</button>
        <button :disabled="page >= totalPages" @click="page = page + 1; loadResults()">下一页</button>
        <span>共 {{ total }} 条</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const filterRisk = ref('')
const page = ref(1)
const total = ref(0)
const totalPages = ref(1)
const results = ref([])

function riskLabel(s) {
  return { low: '健康', medium: '有风险', high: '有风险' }[s] || s
}

function exportExcel() {
  const token = localStorage.getItem('token')
  const url = '/api/results/export/excel/'
  fetch(url, { headers: { Authorization: 'Bearer ' + token } })
    .then(r => { if (!r.ok) throw new Error('Export failed'); return r.blob() })
    .then(blob => {
      const u = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = u
      a.download = 'TIC_Reports.xlsx'
      document.body.appendChild(a)
      a.click()
      setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(u) }, 100)
    })
    .catch(e => { console.error(e); alert('导出失败，请重试') })
}

function downloadPdf(id) {
  const token = localStorage.getItem('token')
  const url = '/api/results/' + id + '/pdf/'
  fetch(url, { headers: { Authorization: 'Bearer ' + token } })
    .then(r => { if (!r.ok) throw new Error('Download failed'); return r.blob() })
    .then(blob => {
      const u = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = u
      a.download = 'TIC_Report_' + id + '.pdf'
      document.body.appendChild(a)
      a.click()
      setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(u) }, 100)
    })
    .catch(e => { console.error(e); alert('下载失败，请重试') })
}

function downloadPpt(id) {
  const token = localStorage.getItem('token')
  const url = '/api/results/' + id + '/ppt/'
  const link = document.createElement('a')
  link.href = url
  if (token) {
    fetch(url, { headers: { Authorization: 'Bearer ' + token } })
      .then(r => { if (!r.ok) throw new Error('Download failed'); return r.blob() })
      .then(blob => {
        const u = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = u
        a.download = 'TIC_Report_' + id + '.pptx'
        document.body.appendChild(a)
        a.click()
        setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(u) }, 100)
      })
      .catch(e => { console.error(e); alert('下载失败，请重试') })
  } else {
    window.open(url, '_blank')
  }
}

async function loadResults() {
  try {
    const params = { page: page.value }
    if (filterRisk.value) params.risk = filterRisk.value
    const r = await api.get('/results/', { params })
    results.value = r.data.results || r.data
    total.value = r.data.count || results.value.length
    totalPages.value = Math.ceil(total.value / 20) || 1
  } catch (e) { console.error(e) }
}

onMounted(loadResults)
</script>

<style scoped>
.btn-pdf {
  background: #c62828;
  color: #fff;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-pdf:hover { opacity: 0.85; }
.btn-export {
  background: #1565c0;
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: opacity 0.2s;
}
.btn-export:hover { opacity: 0.85; }
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
