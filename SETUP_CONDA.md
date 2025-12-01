# 约呗 (YueBei) - Conda 环境安装指南

本指南帮助你使用 Conda 虚拟环境配置约呗项目后端。

## 📋 前置要求

- ✅ Anaconda 或 Miniconda 已安装
- ✅ Python 3.11+
- ✅ MongoDB 数据库（可选择多种安装方式）

---

## 🚀 快速开始 (推荐)

### 1️⃣ 安装 MongoDB

MongoDB 没有运行。请先安装并启动 MongoDB：

```bash
# 运行 MongoDB 安装脚本（提供3种安装方式）
./setup-mongodb.sh
```

**三种安装方式：**

- **选项 1**: Homebrew 本地安装（推荐，永久安装）
- **选项 2**: Docker 运行（轻量，易管理）
- **选项 3**: MongoDB Atlas 云端（无需本地安装）

### 2️⃣ 创建 Conda 环境

```bash
# 使用 environment.yml 创建环境
conda env create -f environment.yml

# 或者手动创建
conda create -n yuebei python=3.11 -y
```

### 3️⃣ 激活环境并安装依赖

```bash
# 激活 yuebei 环境
conda activate yuebei

# 安装后端依赖
cd server
pip install -r requirements.txt
cd ..
```

### 4️⃣ 测试数据库连接

```bash
# 确保 conda 环境已激活
conda activate yuebei

# 运行数据库连接测试
python server/test_db_connection.py
```

### 5️⃣ 启动后端服务

```bash
# 方式1: 使用自动化脚本（推荐）
./start-conda.sh

# 方式2: 手动启动
conda activate yuebei
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📁 新增文件说明

### 1. `environment.yml`
Conda 环境配置文件，定义了所有 Python 依赖包。

### 2. `start-conda.sh`
自动化启动脚本，包含：
- 检查并创建 conda 环境
- 安装依赖
- 检查 MongoDB 连接
- 启动后端服务

### 3. `setup-mongodb.sh`
MongoDB 安装配置脚本，支持：
- Homebrew 本地安装
- Docker 容器运行
- MongoDB Atlas 云端配置指南

### 4. `server/test_db_connection.py`
数据库连接测试工具，测试：
- MongoDB (pymongo) 连接
- Motor 异步驱动
- Redis 连接（可选）
- 环境变量配置

---

## 🔧 常用命令

### Conda 环境管理

```bash
# 查看所有环境
conda env list

# 激活 yuebei 环境
conda activate yuebei

# 退出环境
conda deactivate

# 删除环境（如需重建）
conda env remove -n yuebei

# 更新环境
conda env update -f environment.yml
```

### MongoDB 管理

**Homebrew 安装的 MongoDB:**
```bash
# 启动服务
brew services start mongodb-community@7.0

# 停止服务
brew services stop mongodb-community@7.0

# 重启服务
brew services restart mongodb-community@7.0

# 连接数据库
mongosh
```

**Docker 运行的 MongoDB:**
```bash
# 启动容器
docker start yuebei-mongo

# 停止容器
docker stop yuebei-mongo

# 查看日志
docker logs yuebei-mongo

# 进入容器
docker exec -it yuebei-mongo mongosh
```

### 后端服务

```bash
# 启动开发服务器（热重载）
cd server
uvicorn main:app --reload --port 8000

# 查看 API 文档
# 浏览器访问: http://localhost:8000/docs

# 健康检查
curl http://localhost:8000/api/health
```

---

## 🧪 测试流程

### 完整测试步骤

```bash
# 1. 确保 MongoDB 运行
ps aux | grep mongod

# 2. 激活 conda 环境
conda activate yuebei

# 3. 测试数据库连接
python server/test_db_connection.py

# 4. 启动后端服务
cd server
uvicorn main:app --reload

# 5. 测试 API 接口
curl http://localhost:8000/api/health
```

---

## ❓ 常见问题

### Q1: conda 命令不存在？

**解决方案:**
```bash
# 初始化 conda
source $(conda info --base)/etc/profile.d/conda.sh

# 或者重新打开终端
# 确保 ~/.zshrc 或 ~/.bash_profile 中包含 conda 初始化代码
```

### Q2: MongoDB 连接失败？

**检查步骤:**
```bash
# 1. 检查 MongoDB 是否运行
ps aux | grep mongod
lsof -i :27017

# 2. 查看服务状态
brew services list | grep mongodb

# 3. 检查配置文件
cat server/.env | grep MONGODB_URL

# 4. 手动测试连接
mongosh mongodb://localhost:27017
```

### Q3: 端口 8000 被占用？

**解决方案:**
```bash
# 查找占用进程
lsof -i :8000

# 结束进程
kill -9 <PID>

# 或使用其他端口
uvicorn main:app --port 8001
```

### Q4: 包安装失败？

**解决方案:**
```bash
# 清理 conda 缓存
conda clean --all

# 重新创建环境
conda env remove -n yuebei
conda env create -f environment.yml

# 或单独安装失败的包
conda activate yuebei
pip install <package-name>
```

---

## 📊 环境检查清单

运行以下命令验证环境配置：

```bash
# ✅ Conda 环境
conda --version
conda env list | grep yuebei

# ✅ Python 版本
python --version

# ✅ MongoDB
mongod --version
lsof -i :27017

# ✅ 关键包
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import motor; print('Motor:', motor.version)"
python -c "import pymongo; print('PyMongo:', pymongo.__version__)"

# ✅ 后端服务
curl http://localhost:8000/api/health
```

---

## 🔄 从 venv 迁移到 conda

如果你之前使用 venv，可以这样迁移：

```bash
# 1. 删除旧的 venv 环境
rm -rf venv

# 2. 创建 conda 环境
conda env create -f environment.yml

# 3. 激活新环境
conda activate yuebei

# 4. 验证安装
python server/test_db_connection.py

# 5. 启动服务
./start-conda.sh
```

---

## 📝 配置文件位置

- **Conda 环境配置**: `environment.yml`
- **后端环境变量**: `server/.env`
- **启动脚本**: `start-conda.sh`
- **MongoDB 安装**: `setup-mongodb.sh`
- **连接测试**: `server/test_db_connection.py`

---

## 🆘 获取帮助

遇到问题？尝试以下步骤：

1. 查看日志文件
2. 运行 `python server/test_db_connection.py` 诊断
3. 检查 `server/.env` 配置
4. 查看 MongoDB 日志
5. 提交 Issue 到项目仓库

---

## 🎯 下一步

环境配置完成后：

1. ✅ 测试数据库连接: `python server/test_db_connection.py`
2. ✅ 启动后端服务: `./start-conda.sh`
3. ✅ 打开 API 文档: http://localhost:8000/docs
4. ✅ 配置小程序: 使用微信开发者工具打开 `miniprogram` 目录

Happy Coding! 🚀
