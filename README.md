# Classroom Booking System | 教室预订系统

> 基于 Flask + Vue 3 的全栈教室资源管理平台，支持教室查询、预订申请、周期预订、审批流程及数据统计。

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [API 接口](#api-接口)
- [测试](#测试)
- [部署说明](#部署说明)
- [系统截图](#系统截图)

---

## 功能特性

### 核心功能

- **用户管理**：注册、登录、JWT 鉴权、双角色（普通用户 / 管理员）
- **教室管理**：支持教室信息的新增、编辑、删除、停用维护
- **教室查询**：按日期、时段、容量、设施条件组合筛选空闲教室
- **预订申请**：选择教室与时段、填写用途提交预订，系统自动校验时段冲突
- **我的预订**：查看个人所有预订，支持修改信息、提前取消预订
- **管理员后台**：全量预订查看、强制取消、教室使用数据统计

### 扩展功能

- **预订审批流程**：普通用户提交的预订需管理员审核通过后方可生效
- **周期性预订**：按周固定时段自动生成预订，覆盖长期重复使用场景
- **冲突检测优化**：并发场景下保证同一教室同一时段不可重复预订
- **数据统计**：教室使用率统计、热门时段分布图表展示

---

## 技术栈

| 层级 | 技术选型 |
|---|---|
| **后端** | Python 3 + Flask + SQLAlchemy + Flask-JWT-Extended |
| **前端** | Vue 3 + Element Plus + Pinia + Vue Router + Vite |
| **数据库** | SQLite（开发）/ MySQL（生产） |
| **测试** | pytest + pytest-flask + factory-boy |
| **定时任务** | APScheduler |

---

## 项目结构

```
classroom-booking-backend/
├── app/
│   ├── __init__.py           # Flask 应用初始化
│   ├── config.py             # 全局配置文件
│   ├── extensions.py         # 第三方扩展初始化
│   ├── controllers/          # 接口控制层（路由）
│   │   ├── auth_controller.py
│   │   ├── classroom_controller.py
│   │   ├── reservation_controller.py
│   │   └── admin_controller.py
│   ├── models/               # 数据模型层（ORM）
│   │   ├── user.py
│   │   ├── classroom.py
│   │   ├── reservation.py
│   │   ├── approval.py
│   │   └── periodic_rule.py
│   ├── schemas/              # 请求/响应数据校验
│   ├── services/             # 业务逻辑层
│   ├── utils/                # 通用工具类
│   └── tasks/                # 定时任务
├── tests/                    # 单元测试
├── requirements.txt          # Python 依赖
├── run.py                    # 启动入口
└── seed_data.py              # 测试数据生成脚本

classroom-booking-frontend/
├── public/                   # 静态资源
├── src/
│   ├── api/                  # 接口请求封装
│   ├── router/               # 路由配置
│   ├── stores/               # Pinia 状态管理
│   ├── styles/               # 全局样式
│   ├── views/                # 页面组件
│   │   ├── auth/             # 登录注册
│   │   ├── user/             # 用户端页面
│   │   ├── admin/            # 管理后台
│   │   ├── layout/           # 布局组件
│   │   └── error/            # 错误页面
│   ├── App.vue
│   └── main.js               # 入口文件
├── package.json
├── vite.config.js
└── tsconfig.json
```

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 克隆仓库

```bash
git clone https://github.com/CappuccinoRose/ClassroomBookingSystem.git
cd ClassroomBookingSystem
```

### 2. 启动后端

```bash
cd classroom-booking-backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

后端服务默认运行在 `http://localhost:5000`

### 3. 启动前端

```bash
cd classroom-booking-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器默认运行在 `http://localhost:5173`

### 4. 生成测试数据（可选）

```bash
cd classroom-booking-backend
python seed_data.py
```

> 测试账号：`admin` / `admin123`，普通用户：`user1` ~ `user10` / `password1` ~ `password10`

---

## API 接口

### 接口规范

- 基础路径：`/api`
- 鉴权方式：JWT Bearer Token
- 响应格式：`{ "code": 200, "message": "...", "data": {} }`

### 主要接口

| 模块 | 接口路径 | 方法 | 说明 |
|---|---|---|---|
| 认证 | `/api/auth/register` | POST | 用户注册 |
| 认证 | `/api/auth/login` | POST | 用户登录 |
| 认证 | `/api/auth/userinfo` | GET | 获取当前用户信息 |
| 教室 | `/api/classrooms` | GET | 教室列表查询 |
| 教室 | `/api/classrooms/free` | GET | 空闲教室筛选 |
| 预订 | `/api/reservations/my` | GET | 我的预订列表 |
| 预订 | `/api/reservations` | POST | 提交预订申请 |
| 预订 | `/api/reservations/:id/cancel` | POST | 取消预订 |
| 周期规则 | `/api/reservations/periodic-rules` | GET/POST | 周期规则管理 |
| 管理员 | `/api/admin/reservations` | GET | 全量预订查询 |
| 管理员 | `/api/admin/approvals/pending` | GET | 待审批列表 |
| 管理员 | `/api/admin/statistics/usage` | GET | 使用率统计 |

> 完整接口文档详见源码中各 Controller 文件。

---

## 测试

```bash
cd classroom-booking-backend

# 运行全部测试
pytest

# 运行指定模块测试
pytest tests/test_auth.py
pytest tests/test_classroom.py
pytest tests/test_reservation.py
pytest tests/test_admin.py
```

---

## 部署说明

### 后端部署

1. 配置生产环境变量（`.env`）：
   - `DATABASE_URL`：MySQL 连接地址
   - `SECRET_KEY`、`JWT_SECRET_KEY`：密钥配置

2. 使用 Gunicorn 或 uWSGI 部署 Flask 应用

3. 配置 Nginx 反向代理

### 前端部署

```bash
cd classroom-booking-frontend
npm run build
```

构建产物位于 `dist/` 目录，可部署到任意静态文件服务器。

---

## 系统截图

（待补充）

---

## 开源协议

MIT License
