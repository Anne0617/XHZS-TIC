<template>
  <div>
    <!-- 欢迎区块 -->
    <div class="welcome-bar">
      <div class="welcome-text">
        <h2>数据看板</h2>
        <p>欢迎回来，{{ userName }} —— 以下是系统运行概览</p>
      </div>
      <div class="welcome-time">
        <i class="fas fa-calendar-alt"></i>
        <span>{{ today }}</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:linear-gradient(135deg,#e65100,#ff8f00)">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.total_employees }}</h3>
          <p>员工总数</p>
          <div class="stat-trend">
            <span class="trend-up"><i class="fas fa-arrow-up"></i> 本月 +{{ stats.month_assessed || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:linear-gradient(135deg,#1565c0,#1e88e5)">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.assessed_count }}</h3>
          <p>已完成评估</p>
          <div class="stat-progress">
            <div class="sp-bar">
              <div class="sp-fill" :style="{ width: assessPercent + '%' }"></div>
            </div>
            <span>{{ assessPercent }}%</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:linear-gradient(135deg,#1565c0,#0d47a1)">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.pending_count }}</h3>
          <p>待评估</p>
          <div class="stat-progress">
            <div class="sp-bar pending">
              <div class="sp-fill" :style="{ width: (100 - assessPercent) + '%' }"></div>
            </div>
            <span>{{ 100 - assessPercent }}%</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrap" style="background:linear-gradient(135deg,#c62828,#e53935)">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stats.high_risk }}</h3>
          <p>需重点关注</p>
          <div class="stat-trend">
            <span class="trend-warn"><i class="fas fa-circle"></i> 高风险人数</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部两栏 -->
    <div class="dashboard-grid-2">
      <!-- 风险分布 -->
      <div class="d-card">
        <div class="d-card-header">
          <h3><i class="fas fa-chart-bar"></i> 风险分布</h3>
        </div>
        <div class="d-card-body">
          <div class="risk-chart">
            <div class="risk-bar-row">
              <span class="risk-label">低风险</span>
              <div class="risk-bar"><div class="risk-fill low" :style="{ width: riskPercent('low') + '%' }"></div></div>
              <span class="risk-value">{{ stats.low_risk }}</span>
            </div>
            <div class="risk-bar-row">
              <span class="risk-label">中风险</span>
              <div class="risk-bar"><div class="risk-fill medium" :style="{ width: riskPercent('medium') + '%' }"></div></div>
              <span class="risk-value">{{ stats.medium_risk }}</span>
            </div>
            <div class="risk-bar-row">
              <span class="risk-label">高风险</span>
              <div class="risk-bar"><div class="risk-fill high" :style="{ width: riskPercent('high') + '%' }"></div></div>
              <span class="risk-value">{{ stats.high_risk }}</span>
            </div>
          </div>
          <div class="risk-donut">
            <div class="donut-ring">
              <svg viewBox="0 0 36 36">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.04)" stroke-width="3"/>
                <path v-if="totalRisk > 0" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#81c784" stroke-width="3" stroke-dasharray="80, 20" stroke-dashoffset="0"/>
              </svg>
            </div>
            <div class="donut-center">
              <span class="donut-num">{{ totalRisk }}</span>
              <span class="donut-label">总评估</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 任务/其他 -->
      <div class="d-card">
        <div class="d-card-header">
          <h3><i class="fas fa-tasks"></i> 任务概览</h3>
        </div>
        <div class="d-card-body">
          <div class="task-metrics">
            <div class="tm-item">
              <span class="tm-icon"><i class="fas fa-folder-open"></i></span>
              <div>
                <strong>{{ stats.total_tasks }}</strong>
                <p>总任务数</p>
              </div>
            </div>
            <div class="tm-item">
              <span class="tm-icon" style="background:rgba(33,150,243,0.12);color:#64b5f6;"><i class="fas fa-play-circle"></i></span>
              <div>
                <strong>{{ stats.active_tasks }}</strong>
                <p>进行中</p>
              </div>
            </div>
          </div>
          <div class="quick-actions">
            <h4>快捷操作</h4>
            <div class="qa-buttons">
              <router-link to="/employees" class="qa-btn"><i class="fas fa-user-plus"></i> 添加员工</router-link>
              <router-link to="/tasks" class="qa-btn"><i class="fas fa-plus-circle"></i> 创建任务</router-link>
              <router-link to="/reports" class="qa-btn"><i class="fas fa-file-search"></i> 查看报告</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"
import api from "@/api"

const auth = useAuthStore()
const userName = computed(() => auth.user?.first_name || auth.user?.username || "管理员")
const today = new Date().toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric", weekday: "long" })

const stats = ref({ total_employees:0, assessed_count:0, pending_count:0, high_risk:0, low_risk:0, medium_risk:0, total_tasks:0, active_tasks:0, month_assessed:0 })

const totalRisk = computed(() => stats.value.low_risk + stats.value.medium_risk + stats.value.high_risk)
const assessPercent = computed(() => {
  const total = stats.value.total_employees
  return total > 0 ? Math.round((stats.value.assessed_count / total) * 100) : 0
})

function riskPercent(level) {
  const t = totalRisk.value
  if (t === 0) return 0
  return Math.round((stats.value[level + "_risk"] / t) * 100)
}

onMounted(async () => {
  try {
    const r = await api.get("/dashboard/")
    stats.value = r.data
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.welcome-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 18px 22px;
  background: rgba(17, 29, 54, 0.6);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.welcome-text h2 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.welcome-text p {
  font-size: 12px;
  color: var(--text-muted);
}

.welcome-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.welcome-time i { color: var(--accent-warm); }

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 18px;
  transition: all 0.25s ease;
}

.stat-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.stat-icon-wrap {
  width: 50px;
  height: 50px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff;
  flex-shrink: 0;
}

.stat-info h3 {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.stat-info p {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.stat-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sp-bar {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
  min-width: 60px;
}

.sp-bar.pending .sp-fill {
  background: linear-gradient(90deg, #1565c0, #42a5f5);
}

.sp-fill {
  height: 100%;
  background: linear-gradient(90deg, #43a047, #81c784);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.stat-progress span {
  font-size: 11px;
  color: var(--text-muted);
  min-width: 30px;
}

.stat-trend {
  font-size: 11px;
}

.trend-up { color: #81c784; }
.trend-warn { color: var(--accent-warm-light); }

/* 双栏布局 */
.dashboard-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.d-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: all 0.25s ease;
}

.d-card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-glow);
}

.d-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.d-card-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
}

.d-card-header h3 i { color: var(--accent-warm-light); font-size: 14px; }

.d-card-body {
  padding: 20px;
}

/* 风险分布 */
.risk-chart {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
}

.risk-bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.risk-label {
  width: 50px;
  font-size: 12px;
  color: var(--text-muted);
  text-align: right;
}

.risk-bar {
  flex: 1;
  height: 10px;
  background: rgba(255,255,255,0.04);
  border-radius: 5px;
  overflow: hidden;
}

.risk-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease;
}

.risk-fill.low { background: linear-gradient(90deg, #43a047, #81c784); }
.risk-fill.medium { background: linear-gradient(90deg, #ff8f00, #ffb300); }
.risk-fill.high { background: linear-gradient(90deg, #c62828, #e53935); }

.risk-value {
  width: 30px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  text-align: right;
}

.risk-donut {
  display: none;
}

/* 任务概览 */
.task-metrics {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.tm-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}

.tm-icon {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: rgba(255,143,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-warm-light);
  font-size: 16px;
  flex-shrink: 0;
}

.tm-item strong {
  display: block;
  font-size: 20px;
  color: #fff;
  font-weight: 700;
}

.tm-item p {
  font-size: 11px;
  color: var(--text-muted);
}

.quick-actions h4 {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
  font-weight: 500;
}

.qa-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.qa-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255,143,0,0.06);
  border: 1px solid rgba(255,143,0,0.1);
  border-radius: var(--radius-sm);
  color: var(--accent-warm-light);
  font-size: 12px;
  text-decoration: none;
  transition: all 0.2s;
}

.qa-btn:hover {
  background: rgba(255,143,0,0.12);
  border-color: var(--accent-warm);
}

.qa-btn i { font-size: 12px; }

@media (max-width: 900px) {
  .dashboard-grid-2 { grid-template-columns: 1fr; }
}

@media (max-width: 600px) {
  .welcome-time { display: none; }
}
</style>
