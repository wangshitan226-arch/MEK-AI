# MEK-AI Python AI 服务

企业级AI数字员工平台的Python AI服务后端，基于FastAPI + LangChain构建。

## 🚀 快速开始

### 环境准备
1. Python 3.10+
2. Redis 7.0+（用于缓存和Celery）
3. Docker & Docker Compose（可选）

### 本地开发
```bash
# 克隆项目
git clone <repository>
cd backend-python-ai

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入你的API密钥

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000