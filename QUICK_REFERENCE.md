# 约呗 (YueBei) - 快速参考

## 🚀 一键启动（推荐）

```bash
# 1. 安装 MongoDB（首次运行）
./setup-mongodb.sh

# 2. 启动项目
./start-conda.sh
```

---

## 📝 分步操作

### 步骤 1: 安装 MongoDB

```bash
./setup-mongodb.sh
# 选择安装方式：
# [1] Homebrew（永久安装）
# [2] Docker（推荐）
# [3] MongoDB Atlas（云端）
```

### 步骤 2: 创建 Conda 环境

```bash
conda env create -f environment.yml
conda activate yuebei
```

### 步骤 3: 测试连接

```bash
python server/test_db_connection.py
```

### 步骤 4: 启动服务

```bash
./start-conda.sh
```

---

## 🔍 检查命令

```bash
# MongoDB 状态
ps aux | grep mongod
lsof -i :27017

# Conda 环境
conda env list
conda activate yuebei

# 后端服务
curl http://localhost:8000/api/health
```

---

## 🛠️ 常用命令

| 操作 | 命令 |
|------|------|
| 激活环境 | `conda activate yuebei` |
| 测试数据库 | `python server/test_db_connection.py` |
| 启动后端 | `./start-conda.sh` |
| API 文档 | http://localhost:8000/docs |
| 停止服务 | `Ctrl+C` |
| 退出环境 | `conda deactivate` |

---

## 📂 项目文件

| 文件 | 说明 |
|------|------|
| `environment.yml` | Conda 环境配置 |
| `start-conda.sh` | 启动脚本 |
| `setup-mongodb.sh` | MongoDB 安装 |
| `server/test_db_connection.py` | 连接测试 |
| `server/.env` | 环境变量 |

---

## ⚡ 快捷方式

```bash
# 完整流程（从零开始）
./setup-mongodb.sh           # 选择 [2] Docker
conda env create -f environment.yml
conda activate yuebei
python server/test_db_connection.py
./start-conda.sh

# 日常开发
conda activate yuebei
./start-conda.sh
```
