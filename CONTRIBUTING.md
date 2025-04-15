# 贡献指南

感谢您对 HappySeek 项目的关注！我们欢迎任何形式的贡献，包括但不限于：功能改进、bug修复、文档更新等。

## 开发环境设置

1. Fork 本仓库并克隆到本地：
```bash
git clone https://github.com/yourusername/happyseek.git
cd happyseek
```

2. 安装依赖：

前端：
```bash
cd frontend
npm install
```

后端：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. 启动开发服务器：

前端：
```bash
npm run dev
```

后端：
```bash
flask run
```

## 代码规范

### 前端开发规范

- 使用 TypeScript 进行类型检查
- 遵循 ESLint 和 Prettier 的代码风格
- 组件使用 Composition API 和 `<script setup>` 语法
- 保持组件职责单一，遵循 SOLID 原则
- 使用 Pinia 进行状态管理
- 编写单元测试，保持测试覆盖率

### 后端开发规范

- 使用 Python 类型注解
- 遵循 PEP 8 代码风格（使用 Black 格式化）
- 编写详细的文档字符串
- 遵循 RESTful API 设计原则
- 使用 pytest 编写测试用例
- 保持代码覆盖率在 80% 以上

## Git 工作流程

1. 创建功能分支：
```bash
git checkout -b feature/your-feature-name
```

2. 提交规范：
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式（不影响代码运行）
- refactor: 重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

示例：
```bash
git commit -m "feat: 添加用户认证功能"
```

3. 保持分支同步：
```bash
git fetch origin
git rebase origin/main
```

4. 提交 Pull Request：
- 清晰描述改动内容
- 关联相关 Issue
- 确保 CI 测试通过
- 请求代码审查

## 测试指南

### 前端测试

```bash
cd frontend
npm run test        # 运行单元测试
npm run coverage    # 生成测试覆盖率报告
```

### 后端测试

```bash
cd backend
pytest              # 运行所有测试
pytest -v --cov     # 运行测试并生成覆盖率报告
```

## 文档维护

- API 文档使用 OpenAPI (Swagger) 规范
- 组件文档使用 Storybook
- 核心功能需要编写详细的使用说明
- 更新 CHANGELOG.md 记录版本变更

## 发布流程

1. 版本号遵循语义化版本规范
2. 更新 CHANGELOG.md
3. 创建发布标签
4. 确保所有测试通过
5. 执行部署流程

## 问题反馈

如果您发现了 bug 或有新的功能建议，请：

1. 检查现有的 Issues 是否已经报告过
2. 创建新的 Issue，并提供：
   - 问题的详细描述
   - 复现步骤
   - 期望的行为
   - 实际的行为
   - 相关的日志或截图

## 安全问题

如果您发现了安全漏洞，请勿直接在 Issue 中公开，请发送邮件到：security@happyseek.com

## 行为准则

请遵循我们的行为准则，保持友善和专业的交流氛围。

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。