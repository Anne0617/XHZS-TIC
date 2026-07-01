# 智善TIC人才测评体系 - 部署指南

## 一、准备工作

1. **注册 GitHub 账号**（如已有请跳过）
   - 打开 https://github.com 注册

2. **注册 Zeabur 账号**
   - 打开 https://zeabur.com 注册（支持 GitHub 登录）
   - 绑定 GitHub 账号

3. **安装 Git**
   - 下载安装：https://git-scm.com/downloads
   - 安装完成后，右键桌面选择"Git Bash Here"

---

## 二、将项目推送到 GitHub

在项目目录 `G:\心理测评系统` 下操作：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "初始化：智善TIC人才测评体系"

# 在 GitHub 上创建一个新仓库（不要勾选 README）
# 创建后复制仓库地址，如：https://github.com/你的用户名/tic-assessment.git

# 关联远程仓库
git remote add origin https://github.com/你的用户名/tic-assessment.git

# 推送代码
git push -u origin main
```

---

## 三、在 Zeabur 部署

### 3.1 创建项目

1. 登录 Zeabur 控制台：https://dash.zeabur.com
2. 点击 **创建项目**
3. 选择 **从 GitHub 导入**
4. 授权 Zeabur 访问你的 GitHub 仓库
5. 选择刚才创建的 `tic-assessment` 仓库

### 3.2 添加 PostgreSQL 数据库

1. 在项目页面点击 **新建服务**
2. 选择 **PostgreSQL**
3. 等待数据库就绪（约 1 分钟）
4. Zeabur 会自动生成 `DATABASE_URL` 环境变量

### 3.3 配置环境变量

在 Zeabur 项目设置的 **Environment Variables** 中添加：

| 变量名 | 值 | 说明 |
|--------|----|------|
| `DJANGO_SECRET_KEY` | 生成一个随机密钥 | Django 加密密钥，必填 |
| `DJANGO_DEBUG` | `False` | 关闭调试模式 |
| `DJANGO_ALLOWED_HOSTS` | `.zeabur.app,你的域名` | 允许访问的域名 |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://你的项目名.zeabur.app` | CSRF 信任来源 |

生成密钥的方法：在 Python 中运行：
```python
import secrets
print(secrets.token_urlsafe(50))
```

### 3.4 部署

1. 回到项目页面，点击 **部署**
2. 等待构建完成（首次部署约 2-3 分钟）
3. 部署成功后，Zeabur 会分配一个 `.zeabur.app` 域名

### 3.5 初始化数据

部署完成后，在 Zeabur 控制台中找到你的服务，点击 **Terminal**：

```bash
python manage.py seed_data
```

或通过 **一键运行** 功能执行 seed_data 命令。

---

## 四、访问系统

| 页面 | 地址 |
|------|------|
| 企业官网 | `https://你的项目名.zeabur.app` |
| 管理员登录 | `https://你的项目名.zeabur.app/login` |
| 管理后台 | `https://你的项目名.zeabur.app/dashboard` |
| Django 管理端 | `https://你的项目名.zeabur.app/admin` |

**预置账号（初始化后）：**

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
| 各分公司HR | gz_hr / yd_hr / sz_hr / hd_hr / tj_hr / cd_hr | hr123456 |

---

## 五、日常使用流程

### 管理员操作

1. 打开企业官网 → 点击 **管理员登录** → 进入管理后台
2. **添加员工** → 录入候选人或员工信息
3. **创建测评任务** → 选择模板、指定员工、设置有效期
4. **分享测评** → 在任务详情页复制链接或生成二维码发给候选人

### 候选人操作

1. 打开测评链接（或扫码）
2. 输入姓名和测评码
3. 在线完成作答
4. 提交后自动生成测评报告

### 查看结果

1. 管理员在后台 **评估报告** 页面查看所有结果
2. 可按风险等级筛选（低/中/高风险）
3. 查看各维度得分和岗位适配度

---

## 六、域名绑定（可选）

1. 在 Zeabur 项目中添加自定义域名
2. 在域名管理后台添加 CNAME 记录指向 Zeabur
3. 更新环境变量 `DJANGO_ALLOWED_HOSTS` 和 `CSRF_TRUSTED_ORIGINS`

---


## 七、Docker 部署（一键部署到任何服务器）

如果你有一台安装了 Docker 的服务器（阿里云、腾讯云、AWS 等），可以用 Docker 一键部署。

### 7.1 准备环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的配置
# 首先生成一个安全的密钥
python -c "import secrets; print(secrets.token_urlsafe(50))"
# 将输出的密钥填入 DJANGO_SECRET_KEY

# 将服务器 IP 或域名填入 DJANGO_ALLOWED_HOSTS
# 将你的域名填入 DJANGO_CSRF_TRUSTED_ORIGINS
```

### 7.2 一键启动

```bash
# 构建并后台启动所有服务（Django + PostgreSQL）
docker compose up -d

# 查看启动日志
docker compose logs -f
```

### 7.3 初始化数据

```bash
# 初始化管理员账号和示例数据
docker compose exec tic-app python manage.py seed_data
```

### 7.4 访问系统

| 页面 | 地址 |
|------|------|
| 企业官网 | `http://你的服务器IP:8000` |
| 管理员登录 | `http://你的服务器IP:8000/login` |
| 管理后台 | `http://你的服务器IP:8000/dashboard` |

**预置账号（初始化后）：**

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
| 各分公司HR | gz_hr / yd_hr / sz_hr / hd_hr / tj_hr / cd_hr | hr123456 |

### 7.5 常用命令

```bash
# 停止服务
docker compose down

# 重启服务（代码更新后重新构建）
docker compose up -d --build

# 查看日志
docker compose logs -f tic-app

# 进入容器内部
docker compose exec tic-app bash

# 创建新的管理员账号
docker compose exec tic-app python manage.py createsuperuser
```

### 7.6（可选）配置域名和 HTTPS

如果有域名，可以用 Nginx 反向代理到 `http://localhost:8000`，再用 Certbot 自动申请 HTTPS 证书：

```nginx
# /etc/nginx/sites-available/tic-assessment
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/tic-assessment /etc/nginx/sites-enabled/
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

---
## 八、本地开发

```bash
# 启动 Django 后端（端口 8000）
cd G:\心理测评系统
.venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000

# 启动 Vue 前端（端口 5173，另开一个终端）
cd G:\心理测评系统\frontend
npm run dev

# 访问 http://localhost:5173
```

---

## 九、常见问题

**Q: 部署后页面空白？**
A: 检查 `python manage.py collectstatic` 是否执行成功，确保前端 dist 文件夹已构建。

**Q: 登录提示"用户名或密码错误"？**
A: 确认已运行 `python manage.py seed_data` 初始化管理员账号。

**Q: 静态文件 404？**
A: 检查 Whitenoise 中间件是否正确配置，确保 `STATICFILES_DIRS` 包含 `frontend/dist`。



