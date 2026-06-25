# 🧠 LearnLoop Agent

**通用垂类知识学习 Agent 平台** — 诊断→教学→练习→验证 闭环

## 核心特性

- **智能诊断**：通过 5-8 道精选题快速评估用户水平
- **苏格拉底式教学**：不直接给答案，引导思考
- **自适应练习**：根据掌握度生成针对性题目
- **闭环验证**：学习效果可量化
- **多领域支持**：编程、金融、考证、数学……
- **多模型切换**：DeepSeek / GPT-5.5 / GLM-5.2 / MiMo

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env 填入你的 LLM API Key

# 2. 一键启动
docker-compose up -d

# 3. 访问
# API: http://localhost:8000
# 前端: http://localhost:3000
# API 文档: http://localhost:8000/docs
```

### 方式二：本地开发

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 编辑填入 API Key
python seeds/seed_all.py  # 初始化数据
python main.py  # 启动 API

# 前端
cd frontend
npm install
npm run dev
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/users/register` | 注册 |
| POST | `/api/v1/users/login` | 登录 |
| GET | `/api/v1/domains` | 领域列表 |
| GET | `/api/v1/domains/{id}/concepts` | 概念列表 |
| POST | `/api/v1/learn/sessions` | 创建学习会话 |
| POST | `/api/v1/learn/sessions/{id}/diagnose/start` | 开始诊断 |
| POST | `/api/v1/learn/sessions/{id}/diagnose/answer` | 回答诊断题 |
| POST | `/api/v1/learn/sessions/{id}/teach/start` | 开始教学 |
| POST | `/api/v1/learn/sessions/{id}/teach/reply` | 教学互动 |
| POST | `/api/v1/learn/sessions/{id}/practice/generate` | 生成练习 |
| POST | `/api/v1/learn/sessions/{id}/practice/submit` | 提交答案 |
| POST | `/api/v1/learn/sessions/{id}/verify/start` | 开始验证 |
| POST | `/api/v1/learn/sessions/{id}/verify/submit` | 提交验证 |
| POST | `/api/v1/learn/sessions/{id}/plan` | 生成学习路径 |

## 项目结构

```
learnloop-agent/
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── agents/          # 5 个 Agent（诊断/教学/练习/验证/路径规划）
│   │   ├── api/             # API 路由和 Schema
│   │   ├── core/            # 配置和 LLM 客户端
│   │   ├── db/              # 数据库连接
│   │   ├── models/          # ORM 模型
│   │   ├── rag/             # RAG 检索引擎
│   │   └── utils/           # 工具函数
│   ├── seeds/               # 种子数据
│   ├── main.py              # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Next.js 前端
│   ├── src/
│   │   ├── app/             # 页面
│   │   ├── components/      # 组件
│   │   └── lib/             # 工具函数
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 技术栈

- **后端**: Python 3.12 + FastAPI + SQLAlchemy + FAISS
- **前端**: Next.js 15 + React 19 + Tailwind CSS 4
- **数据库**: MySQL 8.0（开发可用 SQLite）
- **LLM**: DeepSeek / OpenAI / 智谱 / MiMo（统一接口）

## License

MIT
