<template>
  <div>
    <div class="page-header">
      <h2>试卷导入</h2>
      <a :href="templateUrl" class="btn btn-primary" download>
        <i class="fas fa-download"></i> 下载导入模板
      </a>
    </div>

    <div class="card" style="max-width: 720px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px;">
      <p style="color: var(--text-light); margin-bottom: 16px; font-size: 13px;">
        上传 Excel (.xlsx/.xls) 或 CSV 文件，系统自动解析并创建题目。
        支持题型：单选题、多选题、量表题(5级)、量表题(7级)。
      </p>

      <div class="upload-zone"
        :class="{ 'drag-over': dragging }"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()">
        <i class="fas fa-cloud-upload-alt" style="font-size: 40px; color: var(--accent-warm-light); margin-bottom: 12px;"></i>
        <p v-if="!file">拖拽文件到此处，或点击选择文件</p>
        <p v-else style="color: var(--accent-warm-light); font-weight: 600;">
          <i class="fas fa-file"></i> {{ file.name }}
          <span style="color: var(--text-muted); font-weight: 400; margin-left: 8px;">({{ formatSize(file.size) }})</span>
        </p>
        <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv" @change="onFileChange" style="display:none" />
      </div>

      <div v-if="file" class="template-preview" style="margin-top: 16px;">
        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">文件列头预览（需包含以下列）：</p>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
          <span class="tag tag-approved" v-for="col in expectedCols" :key="col">{{ col }}</span>
        </div>
      </div>

      <button class="btn btn-primary" style="margin-top: 20px;" :disabled="!file || uploading" @click="submitImport">
        <i class="fas fa-upload"></i> {{ uploading ? '导入中...' : '开始导入' }}
      </button>
    </div>

    <!-- Result -->
    <div v-if="result" class="result-card" style="max-width: 720px; margin-top: 16px; padding: 20px; border-radius: var(--radius); border: 1px solid var(--border); background: var(--bg-card);">
      <h3 style="font-size: 15px; color: #81c784; margin-bottom: 12px;">
        <i class="fas fa-check-circle"></i> 导入完成
      </h3>
      <p style="font-size: 13px; color: var(--text);">新创建维度：<strong>{{ result.categories_created }}</strong> 个</p>
      <p style="font-size: 13px; color: var(--text);">新创建题目：<strong>{{ result.questions_created }}</strong> 道</p>
      <p v-if="result.errors && result.errors.length" style="font-size: 12px; color: #ef9a9a; margin-top: 8px;">
        <i class="fas fa-exclamation-triangle"></i> {{ result.errors.length }} 个导入警告
      </p>
    </div>

    <!-- Error -->
    <div v-if="errorMsg" class="error-card" style="max-width: 720px; margin-top: 16px; padding: 20px; border-radius: var(--radius); border: 1px solid rgba(229,57,53,0.2); background: rgba(229,57,53,0.06);">
      <p style="color: #ef9a9a; font-size: 13px;"><i class="fas fa-times-circle"></i> {{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/api'

const templateUrl = '/api/questions/import-template/'
const file = ref(null)
const dragging = ref(false)
const uploading = ref(false)
const result = ref(null)
const errorMsg = ref('')
const expectedCols = ['题型', '题目内容', '分值', '所属维度', '时间(秒)', '选项A~E']

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  return (bytes / 1024).toFixed(1) + ' KB'
}

function onDrop(e) {
  dragging.value = false
  const f = e.dataTransfer.files[0]
  if (f) validateAndSet(f)
}

function onFileChange(e) {
  const f = e.target.files[0]
  if (f) validateAndSet(f)
}

function validateAndSet(f) {
  const ext = f.name.split('.').pop().toLowerCase()
  if (!['xlsx', 'xls', 'csv'].includes(ext)) {
    errorMsg.value = '仅支持 Excel (.xlsx/.xls) 和 CSV (.csv) 格式'
    return
  }
  errorMsg.value = ''
  result.value = null
  file.value = f
}

async function submitImport() {
  if (!file.value || uploading.value) return
  uploading.value = true
  result.value = null
  errorMsg.value = ''

  const form = new FormData()
  form.append('file', file.value)

  try {
    const r = await api.post('/questions/import/', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = r.data
    file.value = null
  } catch (e) {
    if (e.response?.data?.error) {
      errorMsg.value = e.response.data.error
      if (e.response.data.header_found) {
        errorMsg.value += '（表头: ' + e.response.data.header_found.join(', ') + '）'
      }
    } else {
      errorMsg.value = '导入失败: ' + (e.message || '未知错误')
    }
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-light);
  font-size: 14px;
}

.upload-zone:hover, .upload-zone.drag-over {
  border-color: var(--accent-warm);
  background: rgba(255, 143, 0, 0.04);
  color: var(--text);
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.25s ease;
}

.card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-glow);
}
</style>
