# HappySeek 智能网页元素采集系统

🌐 基于 Vue 3 + Flask 的现代化网页爬虫系统，支持智能识别、异步采集和实时监控。

## 特性

- 🚀 基于 Playwright 的智能网页采集
- 🎯 支持登录态保持和动态渲染页面
- 📊 实时数据可视化和任务监控
- 🔄 异步任务队列和分布式部署
- 🛡️ 完善的用户权限和审批流程
- 🌈 现代化的暗色主题UI设计

## 技术栈

### 前端
- Vue 3.4.19
- Vite 5.1.3
- Element Plus 2.5.6
- Pinia 2.1.7
- ECharts 5.5.0
- Socket.IO Client 4.7.4

### 后端
- Flask 3.0.2
- Flask-SocketIO 5.3.6
- SQLAlchemy 2.0.27
- Celery 5.3.6
- Playwright 1.41.2
- Redis 5.0.1

## 快速开始

### 使用 Docker Compose（推荐）

1. 克隆项目：
```bash
git clone https://github.com/yourusername/happyseek.git
cd happyseek
```

2. 启动服务：
```bash
docker-compose up -d
```

服务将在以下端口启动：
- 前端: http://localhost:80
- 后端 API: http://localhost:5000
- Redis: localhost:6379

### 手动部署

#### 前端
```bash
cd frontend
npm install
npm run dev    # 开发环境
npm run build  # 生产环境
```

#### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
flask run
```

#### Celery Worker
```bash
cd backend
celery -A app.celery worker --loglevel=info
```

## 环境要求

- Node.js >= 18.0.0
- Python >= 3.12
- Redis >= 7.0
- MySQL >= 8.0

## 配置说明

### 前端配置
在 `.env` 文件中配置：
```
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000
```

### 后端配置
在 `.env` 文件中配置：
```
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
```

## 项目结构

```
.
├── frontend/              # Vue 3 前端代码
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   ├── stores/       # Pinia 状态管理
│   │   └── utils/        # 工具函数
│   └── ...
├── backend/              # Flask 后端代码
│   ├── api/             # API 路由
│   ├── crawler/         # 爬虫核心逻辑
│   ├── services/        # 业务服务
│   └── tasks/           # Celery 异步任务
└── docker-compose.yml   # Docker 编排配置
```

## 贡献指南

1. Fork 该仓库
2. 创建新的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 作者

pisy - pis_yu@outlook.com

## 更新日志

### v1.0.0 (2024-04-15)
- ✨ 初始版本发布
- 🚀 支持智能网页采集
- 📊 实时数据可视化
- 🔒 用户权限管理
