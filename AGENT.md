# 星河智善人才测评 — AGENT.md

## 项目概述

企业级入职员工人才评估系统，支持多级权限管理（超管 → 分公司HR管理员 → 员工），
涵盖题库管理、评估任务下发、在线作答、自动评分、报告生成、数据看板全流程。

**品牌名称：** 星河智善人才测评
**品牌色：** 深蓝 #0a1628 / #121e36 + 红色强调 #c62828
**定位：** 商务人才评估平台（非心理测评系统，已去除所有敏感词）

---

## 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 后端框架 | Django | 6.0.6 |
| 数据库 | SQLite | 内置 |
| API | Django REST Framework + SimpleJWT | - |
| 前端框架(SPA) | Vue 3 + Vite | Vite 5 |
| 状态管理 | Pinia | - |
| 路由 | Vue Router 4 | - |
| HTTP 客户端 | Axios | - |
| 模板引擎 | Django Templates (备份) | - |
| Python | 3.12.10 | 虚拟环境 .venv |
| Node.js | 20 LTS | 前端构建 |

---

## 目录结构

```
心理测评系统/
├── .venv/                          # Python 虚拟环境
├── accounts/                       # 用户/权限模块
│   ├── models.py                   # Branch, User(自定义), OperationLog
│   └── admin.py
├── assessment/                     # 核心业务模块
│   ├── models.py                   # 全部数据模型
│   ├── views.py                    # 公开首页视图
│   ├── views_dashboard.py          # 后台管理视图
│   ├── views_employee.py           # 员工作答端视图
│   ├── views_api.py                # REST API 视图
│   ├── serializers.py              # DRF 序列化器
│   ├── urls.py / urls_dashboard.py / urls_api.py
│   └── management/commands/seed_data.py
├── config/                         # Django 项目配置
│   ├── settings.py
│   └── urls.py
├── frontend/                       # Vue 3 SPA
│   ├── index.html / vite.config.js / package.json
│   ├── dist/                       # 构建产物
│   └── src/
│       ├── main.js / App.vue
│       ├── api/index.js
│       ├── router/index.js
│       ├── stores/auth.js
│       └── views/LoginView.vue, DashboardView.vue
├── templates/                      # Django 模板
│   ├── base.html                   # 公开前台
│   └── dashboard/                  # 后台管理 (13个模板)
├── assessment/templates/assessment/ # 员工作答 (home/access/take/result)
├── manage.py
└── db.sqlite3
```

---

## 数据模型

### accounts
- **Branch** — 分公司 (6个: 广州/粤东/深圳/华东/天津/成都)
- **User** — 自定义用户 (super_admin / hr_admin)，关联 branch，权限细分
- **OperationLog** — 操作日志

### assessment
- **QuestionCategory** — 评估维度 (7个: 职业适应力/压力管理/职业倾向/个性特征/情绪智力/团队协作/职业风险)
- **Question** — 题目 (likert5 量表，支持反向计分)
- **QuestionOption** — 选项
- **AssessmentTemplate** — 评估模板 (4个: 通用/销售/技术/管理)
- **TemplateQuestion** — 模板-题目关联
- **Employee** — 员工信息
- **AssessmentTask** — 评估任务
- **TaskAssignment** — 任务分配 (含评估码)
- **AssessmentSession** — 作答会话 (异常检测)
- **Answer** — 答案
- **AssessmentResult** — 评估结果 (维度得分/风险/适配度)
- **AssessmentReport** — 报告缓存
- **SystemConfig** — 系统配置

---

## URL 路由

| 路径 | 说明 | 认证 |
|------|------|------|
| `/` | 公开首页 | 无 |
| `/assessment/` | 员工评估入口 | 评估码 |
| `/assessment/take/<code>/` | 在线作答 | 评估码 |
| `/assessment/submit/<code>/` | 提交答案 | 评估码 |
| `/assessment/result/<code>/` | 查看结果 | 评估码 |
| `/admin/` | Django 管理端 | 管理员 |
| `/dashboard/` | 管理后台 | 管理员 |
| `/api/token/` | 获取 JWT | POST |
| `/api/me/` | 用户信息 | JWT |
| `/api/dashboard/` | 仪表盘 | JWT |
| `/api/employees/` | 员工 CRUD | JWT |
| `/api/questions/` | 题目 CRUD | JWT |
| `/api/tasks/` | 任务 CRUD | JWT |
| `/api/results/` | 结果 CRUD | JWT |

---

## 预置账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
| 广州HR | gz_hr | hr123456 |
| 粤东HR | yd_hr | hr123456 |
| 深圳HR | sz_hr | hr123456 |
| 华东HR | hd_hr | hr123456 |
| 天津HR | tj_hr | hr123456 |
| 成都HR | cd_hr | hr123456 |

---

## 启动方式

### Django 后端 (端口 8000)
```powershell
.venv/Scripts/Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

### Vue 开发服务器 (端口 5173, 需先启动 Django)
```powershell
cd frontend
npm run dev
```

### 构建 Vue
```powershell
cd frontend
npm run build
```

### 重置种子数据
```powershell
python manage.py seed_data
```

---

## 关键设计决策

1. **双重前端**：Django Templates (功能完整) + Vue 3 SPA (新架构推进中)
2. **数据隔离**：HR 管理员自动限定到其分公司，超管可看全量
3. **评估码**：员工凭码作答无需注册，格式 PSMMDDXXXX
4. **自动评分**：支持反向计分，维度百分比，风险标签，异常检测 (<60秒标记异常)
5. **品牌安全**：全站无"心理"敏感词，使用"人才评估/职业发展"表述
6. **JWT**：Access Token 8小时，Refresh Token 7天
7. **主题**：深蓝商务暗色主题，CSS变量集中管理

## 开发规范

- 编码: UTF-8
- Python: 3.12.10 (.venv)
- Node.js: 20 LTS
- 模型变更: makemigrations + migrate (自定义User需清库重来)
- API: 前缀 /api/，DRF ViewSet
- Vue: script setup + Pinia
