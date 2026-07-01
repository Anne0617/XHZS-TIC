<template>
  <div class="assess-wrapper">
    <!-- Loading -->
    <div class="assess-card" v-if="pageState === 'loading'">
      <div class="assess-loading"><i class="fas fa-spinner fa-spin"></i><p>加载中...</p></div>
    </div>

    <!-- Error -->
    <div class="assess-card" v-else-if="pageState === 'error'">
      <div class="assess-error">
        <i class="fas fa-exclamation-circle" style="font-size:48px;color:var(--danger)"></i>
        <h2>无法开始测评</h2>
        <p>{{ errorMessage }}</p>
      </div>
    </div>

    <!-- Entry Step -->
    <div class="assess-card" v-else-if="pageState === 'entry'">
      <div class="assess-logo"><i class="fas fa-star" style="color:var(--accent);font-size:36px;"></i></div>
      <h1 class="assess-title">智善TIC人才测评体系</h1>
      <div class="assess-task-info">
        <div class="info-row"><span>测评任务</span><strong>{{ taskInfo?.name }}</strong></div>
        <div class="info-row"><span>测评模板</span><strong>{{ taskInfo?.template_name }}</strong></div>
        <div class="info-row"><span>题目数量</span><strong>{{ totalQuestions }} 题</strong></div>
        <div class="info-row"><span>预计用时</span><strong>{{ taskInfo?.duration_minutes }} 分钟</strong></div>
      </div>
      <div class="assess-divider"></div>
      <p class="assess-form-title">请填写以下信息开始测评</p>
      <form @submit.prevent="startAssessment" class="assess-form">
        <div class="form-group">
          <label>姓名 *</label>
          <input v-model="form.name" placeholder="请输入您的姓名" required />
        </div>
        <div class="form-group">
          <label>手机号 *</label>
          <input v-model="form.phone" type="tel" placeholder="请输入手机号" required />
        </div>
        <div class="form-group">
          <label>面试岗位（选填）</label>
          <input v-model="form.position" placeholder="如: 产品经理、软件开发" />
        </div>
        <div class="form-group">
          <label>邮箱（选填）</label>
          <input v-model="form.email" type="email" placeholder="请输入邮箱" />
        </div>
        <button type="submit" class="btn-start" :disabled="starting">
          {{ starting ? '正在进入...' : '开始测评' }}
        </button>
      </form>
    </div>

    <!-- Taking Step -->
    <div class="assess-card assess-card-wide" v-else-if="pageState === 'taking'">
      <div class="assess-taking-header">
        <div class="assess-progress-text">第 {{ currentQuestionIndex + 1 }} / {{ totalQuestions }} 题</div>
        <div class="assess-timer" :class="{ 'timer-warn': remainingMin < 3 }">
          <i class="fas fa-clock"></i> {{ remainingMin }}:{{ remainingSec.toString().padStart(2,'0') }}
        </div>
      </div>
      <div class="assess-progress-bar">
        <div class="assess-progress-fill" :style="{ width: ((currentQuestionIndex) / totalQuestions * 100) + '%' }"></div>
      </div>

      <div class="assess-question" v-for="(q, idx) in questions" :key="q.id" v-show="idx === currentQuestionIndex">
        <div class="q-category">{{ q.category_name || '未分类' }}</div>
        <div class="q-text">{{ q.text }}</div>
        <div class="q-description" v-if="q.description">{{ q.description }}</div>

        <!-- Likert5 / Likert7 -->
        <div class="q-options likert" v-if="q.question_type === 'likert5' || q.question_type === 'likert7'">
          <div class="likert-row" v-for="(opt, i) in (q.options || [])" :key="i">
            <input type="radio" :name="'q_' + q.id" :value="opt.label" v-model="answers[q.id]" :id="'q' + q.id + '_' + i" />
            <label :for="'q' + q.id + '_' + i">{{ opt.text }}</label>
          </div>
        </div>

        <!-- Single Choice -->
        <div class="q-options choice" v-else-if="q.question_type === 'single'">
          <div class="choice-row" v-for="opt in q.options" :key="opt.label">
            <input type="radio" :name="'q_' + q.id" :value="opt.label" v-model="answers[q.id]" :id="'q' + q.id + '_' + opt.label" />
            <label :for="'q' + q.id + '_' + opt.label">{{ opt.label }}. {{ opt.text }}</label>
          </div>
        </div>

        <!-- Multiple Choice -->
        <div class="q-options choice" v-else-if="q.question_type === 'multiple'">
          <div class="choice-row" v-for="opt in q.options" :key="opt.label">
            <input type="checkbox" :value="opt.label" :checked="(answers[q.id] || '').includes(opt.label)" @change="toggleMulti(q.id, opt.label)" :id="'q' + q.id + '_' + opt.label" />
            <label :for="'q' + q.id + '_' + opt.label">{{ opt.label }}. {{ opt.text }}</label>
          </div>
        </div>

        <div class="q-skip" v-if="!answers[q.id]">
          <i class="fas fa-circle" style="color:var(--text-muted);font-size:8px;margin-right:6px;"></i>请作答后继续
        </div>
      </div>

      <div class="assess-nav">
        <button class="btn btn-outline" @click="prevQuestion" :disabled="currentQuestionIndex === 0">上一题</button>
        <button v-if="currentQuestionIndex < totalQuestions - 1" class="btn btn-primary" @click="nextQuestion">下一题</button>
        <button v-else class="btn btn-success" @click="submitAssessment" :disabled="submitting">
          {{ submitting ? '提交中...' : '提交测评' }}
        </button>
      </div>
    </div>

    <!-- Complete Step -->
    <div class="assess-card" v-else-if="pageState === 'complete'">
      <div class="assess-complete">
        <i class="fas fa-check-circle" style="font-size:56px;color:var(--success)"></i>
        <h2>测评提交成功</h2>
        <p>感谢您的参与！您的测评结果已成功提交。</p>
        <p class="complete-note">如有疑问请联系人力资源中心。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const code = route.params.code

const pageState = ref('loading')
const errorMessage = ref('')
const questions = ref([])
const totalQuestions = ref(0)
const taskInfo = ref(null)
const sessionId = ref(null)
const starting = ref(false)
const submitting = ref(false)

const currentQuestionIndex = ref(0)
const answers = reactive({})

const form = reactive({ name: '', phone: '', email: '', position: '' })

// Timer
const remainingSec = ref(0)
const remainingMin = ref(0)
let timerInterval = null

const likert5Labels = ['非常不符合', '比较不符合', '一般', '比较符合', '非常符合']
const likert7Labels = ['非常不符合', '不符合', '比较不符合', '一般', '比较符合', '符合', '非常符合']

function likertLabels(type) {
  return type === 'likert7' ? likert7Labels : likert5Labels
}

function toggleMulti(qid, label) {
  const current = answers[qid] || ''
  const parts = current ? current.split(',') : []
  const idx = parts.indexOf(label)
  if (idx >= 0) parts.splice(idx, 1)
  else parts.push(label)
  answers[qid] = parts.join(',')
}

async function loadAssessment() {
  try {
    const r = await axios.get(`/api/public/assess/${code}/`)
    if (!r.data.valid) {
      errorMessage.value = r.data.error || '无效的测评链接'
      pageState.value = 'error'
      return
    }
    questions.value = r.data.questions
    totalQuestions.value = r.data.total_questions
    taskInfo.value = r.data.task
    form.name = r.data.employee?.name || ''
    form.phone = r.data.employee?.phone || ''
    pageState.value = 'entry'
  } catch (e) {
    errorMessage.value = e.response?.data?.error || '测评链接无效或已过期'
    pageState.value = 'error'
  }
}

async function startAssessment() {
  if (!form.name || !form.phone) return
  starting.value = true
  try {
    const r = await axios.post(`/api/public/assess/${code}/start/`, { name: form.name, phone: form.phone, email: form.email, position: form.position })
    sessionId.value = r.data.session_id
    // Start timer
    const duration = (taskInfo.value?.duration_minutes || 30) * 60
    remainingSec.value = duration
    startTimer()
    pageState.value = 'taking'
  } catch (e) {
    errorMessage.value = e.response?.data?.error || '开始测评失败'
    pageState.value = 'error'
  } finally { starting.value = false }
}

function startTimer() {
  timerInterval = setInterval(() => {
    if (remainingSec.value <= 0) {
      clearInterval(timerInterval)
      submitAssessment()
      return
    }
    remainingSec.value--
    remainingMin.value = Math.floor(remainingSec.value / 60)
  }, 1000)
}

function prevQuestion() {
  if (currentQuestionIndex.value > 0) currentQuestionIndex.value--
}
function nextQuestion() {
  if (currentQuestionIndex.value < totalQuestions.value - 1) currentQuestionIndex.value++
}

async function submitAssessment() {
  var unanswered = []
  for (var i = 0; i < questions.value.length; i++) {
    var q = questions.value[i]
    if (!answers[q.id] || answers[q.id] === "") {
      unanswered.push(q)
    }
  }
  if (unanswered.length > 0) {
    currentQuestionIndex.value = questions.value.indexOf(unanswered[0])
    alert('\u8bf7\u56de\u7b54\u6240\u6709\u9898\u76ee\u540e\u518d\u63d0\u4ea4')
    submitting.value = false
    return
  }
  submitting.value = true
  clearInterval(timerInterval)
  try {
    const answersList = Object.entries(answers).map(([qid, val]) => ({
      question_id: parseInt(qid), value: val || ''
    }))
    await axios.post(`/api/public/assess/${code}/submit/`, {
      session_id: sessionId.value,
      answers: answersList
    })
    pageState.value = 'complete'
  } catch (e) {
    errorMessage.value = e.response?.data?.error || '提交失败，请重试'
    pageState.value = 'error'
  } finally { submitting.value = false }
}

onMounted(loadAssessment)
onUnmounted(() => { if (timerInterval) clearInterval(timerInterval) })
</script>

<style scoped>
.assess-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0a1628, #121e36, #1a1830);
  padding: 24px;
}
.assess-card {
  background: #121e36;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  padding: 36px;
  width: 100%;
  max-width: 480px;
  text-align: center;
}
.assess-card-wide { max-width: 640px; }
.assess-loading, .assess-error, .assess-complete { padding: 32px 0; }
.assess-loading p, .assess-error p { color: var(--text-muted); margin-top: 12px; }
.assess-error h2 { color: var(--danger); font-size: 18px; margin-top: 12px; }
.assess-complete h2 { color: var(--success); font-size: 20px; margin: 16px 0 8px; }
.assess-complete p { color: var(--text-muted); font-size: 14px; }
.complete-note { margin-top: 8px; font-size: 12px; opacity: 0.7; }

.assess-logo { margin-bottom: 12px; }
.assess-title { color: #e8eaf6; font-size: 20px; font-weight: 600; margin-bottom: 20px; }

.assess-task-info { text-align: left; margin-bottom: 16px; }
.info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.info-row span { color: var(--text-muted); font-size: 13px; }
.info-row strong { color: #e8eaf6; font-size: 13px; }

.assess-divider { height: 1px; background: rgba(255,255,255,0.08); margin: 16px 0; }
.assess-form-title { color: var(--text-light); font-size: 14px; margin-bottom: 16px; }

.assess-form { text-align: left; }
.assess-form .form-group { margin-bottom: 14px; }
.assess-form .form-group label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.assess-form .form-group input { width: 100%; padding: 10px 12px; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; background: rgba(255,255,255,0.03); color: #e8eaf6; font-size: 14px; }
.assess-form .form-group input:focus { outline: none; border-color: var(--accent); }

.btn-start { width: 100%; padding: 12px; background: var(--accent); color: #fff; border: none; border-radius: 6px; font-size: 15px; font-weight: 600; cursor: pointer; margin-top: 8px; }
.btn-start:hover { background: var(--accent-hover); }
.btn-start:disabled { opacity: 0.5; cursor: not-allowed; }

/* Taking step */
.assess-taking-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.assess-progress-text { font-size: 13px; color: var(--text-light); }
.assess-timer { font-size: 14px; color: var(--text-light); font-weight: 600; }
.assess-timer.timer-warn { color: var(--danger); animation: pulse 1s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.assess-progress-bar { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-bottom: 24px; overflow: hidden; }
.assess-progress-fill { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.3s ease; }

.assess-question { text-align: left; min-height: 320px; }
.q-category { display: inline-block; padding: 2px 8px; background: rgba(198,40,40,0.12); color: var(--accent); border-radius: 4px; font-size: 11px; font-weight: 600; margin-bottom: 12px; }
.q-text { color: #e8eaf6; font-size: 16px; line-height: 1.6; margin-bottom: 8px; font-weight: 500; }
.q-description { color: var(--text-muted); font-size: 13px; margin-bottom: 20px; }

.q-options { margin-top: 20px; }
.likert-row, .choice-row { display: flex; align-items: center; padding: 10px 12px; margin-bottom: 6px; border-radius: 6px; background: rgba(255,255,255,0.03); cursor: pointer; transition: background 0.15s; }
.likert-row:hover, .choice-row:hover { background: rgba(255,255,255,0.06); }
.likert-row input, .choice-row input { margin-right: 10px; accent-color: var(--accent); }
.likert-row label, .choice-row label { color: #e8eaf6; font-size: 14px; cursor: pointer; flex: 1; }
.choice-row label { margin-left: 4px; }

.q-skip { margin-top: 16px; font-size: 12px; color: var(--text-muted); }

.assess-nav { display: flex; justify-content: space-between; gap: 10px; margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); }
.assess-nav .btn { flex: 1; justify-content: center; }
</style>
