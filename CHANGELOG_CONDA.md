# 约呗项目更新日志 - Conda 迁移

## 📅 更新日期: 2024-11-29

## 🎯 更新概述

本次更新将项目后端虚拟环境从 `venv` 迁移到 `Conda`，同时增加了对两种环境的自动检测和支持。此外，还新增了 MongoDB 安装向导和数据库连接测试工具。

---

## ✨ 主要更新

### 1. Conda 环境支持 ⭐

#### 新增文件：

| 文件 | 说明 |
|------|------|
| `environment.yml` | Conda 环境配置文件 |
| `start-conda.sh` | Conda 专用启动脚本 |
| `SETUP_CONDA.md` | Conda 环境详细配置指南 |
| `QUICK_REFERENCE.md` | 快速参考手册 |

#### 功能特性：

- ✅ 支持通过 `environment.yml` 一键创建 Conda 环境
- ✅ Python 3.11 + 所有后端依赖自动安装
- ✅ 使用 conda-forge 频道，避免 TOS 问题
- ✅ 与 venv 完全兼容，可自由切换

### 2. MongoDB 安装向导 🗄️

#### 新增文件：

| 文件 | 说明 |
|------|------|
| `setup-mongodb.sh` | MongoDB 安装交互式向导 |
| `server/test_db_connection.py` | 数据库连接测试工具 |

#### 支持的安装方式：

1. **Homebrew 本地安装** - 永久安装，性能最优
2. **Docker 容器运行** - 轻量级，易管理（推荐）
3. **MongoDB Atlas 云端** - 免费，无需本地安装

#### 测试工具功能：

- ✅ MongoDB (pymongo) 连接测试
- ✅ Motor 异步驱动测试
- ✅ Redis 连接测试（可选）
- ✅ 环境变量完整性检查
- ✅ 详细的错误诊断和解决方案

### 3. 统一启动脚本 🚀

#### 更新文件：

| 文件 | 变更 |
|------|------|
| `start.sh` | 完全重写，支持 Conda 和 venv 自动检测 |

#### 新增功能：

- ✅ 自动检测 Conda 可用性
- ✅ 自动创建/激活虚拟环境
- ✅ 智能依赖安装检查
- ✅ MongoDB/Redis 自动启动（Docker）
- ✅ 端口冲突自动处理
- ✅ 健康检查和启动验证
- ✅ 友好的错误提示和解决方案

### 4. 文档更新 📚

#### 更新的文档：

| 文档 | 变更内容 |
|------|----------|
| `README.md` | 全面重写，添加 Conda 支持说明 |
| `QUICKSTART.md` | 新增 Conda 快速开始指南 |
| `SETUP_CONDA.md` | 新增详细的 Conda 配置文档 |
| `QUICK_REFERENCE.md` | 新增快速参考手册 |

#### 文档新增内容：

- ✅ 三种启动方式的详细说明
- ✅ Conda vs venv 对比
- ✅ MongoDB 三种安装方式对比
- ✅ 常见问题排查指南
- ✅ 完整的命令参考
- ✅ 真机调试教程

---

## 📦 文件结构变化

### 新增文件

```
yuebei/
├── environment.yml              # 新增：Conda 环境配置
├── start-conda.sh               # 新增：Conda 启动脚本
├── setup-mongodb.sh             # 新增：MongoDB 安装向导
├── SETUP_CONDA.md               # 新增：Conda 配置文档
├── QUICK_REFERENCE.md           # 新增：快速参考
├── CHANGELOG_CONDA.md           # 新增：本更新日志
└── server/
    └── test_db_connection.py    # 新增：连接测试工具
```

### 修改文件

```
yuebei/
├── start.sh                     # 修改：支持 Conda 和 venv
├── README.md                    # 修改：添加 Conda 说明
└── QUICKSTART.md                # 修改：更新快速开始指南
```

### 保留文件

```
yuebei/
├── server/                      # 未修改：后端代码
├── miniprogram/                 # 未修改：小程序代码
├── docker-compose.yml           # 未修改：Docker 配置
└── venv/                        # 保留：venv 环境（可删除）
```

---

## 🔄 迁移指南

### 从 venv 迁移到 Conda

#### 方式 1：保留 venv（推荐）

```bash
# 1. 创建 Conda 环境
conda env create -f environment.yml
conda activate yuebei

# 2. 测试新环境
python server/test_db_connection.py

# 3. 启动服务
./start-conda.sh

# 4. 确认无问题后删除 venv
rm -rf venv
```

#### 方式 2：直接切换

```bash
# 1. 删除旧环境
rm -rf venv

# 2. 创建 Conda 环境
conda env create -f environment.yml

# 3. 激活并启动
conda activate yuebei
./start-conda.sh
```

### 继续使用 venv

如果你不想使用 Conda，可以继续使用 venv：

```bash
# start.sh 会自动检测并使用 venv
./start.sh
```

---

## 🚀 快速开始（新用户）

### 推荐流程

```bash
# 1. 克隆项目
cd yuebei

# 2. 安装 MongoDB
./setup-mongodb.sh
# 选择 [2] Docker

# 3. 创建 Conda 环境
conda env create -f environment.yml
conda activate yuebei

# 4. 测试连接
python server/test_db_connection.py

# 5. 启动服务
./start-conda.sh

# 6. 打开浏览器
# http://localhost:8000/docs
```

### 一键启动

```bash
# 自动检测环境，自动安装依赖
./start.sh
```

---

## 📝 配置变更

### 无需修改的配置

- `server/.env` - 环境变量配置保持不变
- `miniprogram/app.js` - 小程序配置保持不变
- `docker-compose.yml` - Docker 配置保持不变

### 新增配置

- `environment.yml` - Conda 环境定义
- `~/.condarc` - Conda 频道配置（自动生成）

---

## 🔧 命令对比

| 操作 | venv | Conda |
|------|------|-------|
| 创建环境 | `python3 -m venv venv` | `conda env create -f environment.yml` |
| 激活环境 | `source venv/bin/activate` | `conda activate yuebei` |
| 退出环境 | `deactivate` | `conda deactivate` |
| 安装依赖 | `pip install -r requirements.txt` | 自动安装 |
| 查看环境 | `which python` | `conda env list` |
| 删除环境 | `rm -rf venv` | `conda env remove -n yuebei` |

---

## 🆕 新增命令

### Conda 环境管理

```bash
# 查看所有环境
conda env list

# 导出环境
conda env export > environment-backup.yml

# 更新环境
conda env update -f environment.yml --prune

# 克隆环境
conda create --name yuebei-dev --clone yuebei
```

### MongoDB 管理

```bash
# 安装向导
./setup-mongodb.sh

# 连接测试
python server/test_db_connection.py

# Docker 管理
docker start yuebei-mongo
docker stop yuebei-mongo
docker logs yuebei-mongo

# Homebrew 管理
brew services start mongodb-community@7.0
brew services stop mongodb-community@7.0
```

---

## ⚠️ 已知问题和解决方案

### 1. Conda TOS 问题

**问题：**
```
CondaToSNonInteractiveError: Terms of Service have not been accepted
```

**解决：**
已在 `start.sh` 和 `start-conda.sh` 中自动处理，使用 `conda-forge` 频道避免此问题。

### 2. MongoDB 权限问题（Docker）

**问题：**
MongoDB 容器启动后连接被拒绝

**解决：**
等待 2-3 秒让容器完全启动，脚本已自动处理等待时间。

### 3. 端口冲突

**问题：**
8000 或 27017 端口被占用

**解决：**
`start.sh` 会自动检测并提示清理占用进程。

---

## 📊 性能对比

| 指标 | venv | Conda |
|------|------|-------|
| 环境创建速度 | 快 (10s) | 中等 (30-60s) |
| 包管理 | pip only | conda + pip |
| 依赖解析 | 基础 | 高级 |
| 隔离性 | 好 | 极好 |
| 跨平台 | 好 | 极好 |
| 科学计算支持 | 需手动安装 | 内置 |

---

## 🎯 推荐使用场景

### 使用 Conda（推荐）

- ✅ 数据科学/机器学习项目
- ✅ 需要复杂依赖管理
- ✅ 团队协作统一环境
- ✅ 跨平台开发

### 使用 venv

- ✅ 简单 Web 应用
- ✅ 纯 Python 项目
- ✅ 快速原型开发
- ✅ CI/CD 流水线

---

## 📚 相关文档

- [README.md](README.md) - 项目总览
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [SETUP_CONDA.md](SETUP_CONDA.md) - Conda 详细配置
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考

---

## 🤝 贡献

如果你在使用过程中遇到问题或有改进建议，欢迎：

- 提交 Issue
- 发起 Pull Request
- 完善文档

---

## ✅ 验证清单

升级后请验证以下项目：

- [ ] Conda 环境创建成功
- [ ] MongoDB 连接正常
- [ ] 后端服务启动成功
- [ ] API 文档可访问 (http://localhost:8000/docs)
- [ ] 小程序连接正常
- [ ] 所有依赖包安装正确

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 [QUICKSTART.md](QUICKSTART.md) 常见问题部分
2. 运行 `python server/test_db_connection.py` 诊断
3. 查看 [SETUP_CONDA.md](SETUP_CONDA.md) 详细配置
4. 提交 Issue 到项目仓库

---

**更新完成！享受更好的开发体验！** 🎉
