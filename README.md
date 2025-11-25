# 约呗 YueBei - 智能聚会地点推荐小程序

## 项目简介
约呗是一款帮助朋友快速找到最方便聚会地点的微信小程序，通过智能算法计算多人位置的最优聚会点。

## 技术栈
- **前端**：微信小程序原生框架
- **后端**：Node.js + Express + TypeScript
- **数据库**：MongoDB (存储临时聚会数据)
- **缓存**：Redis (实时位置更新)
- **地图服务**：腾讯地图API

## 项目结构
```
yuebei/
├── miniprogram/        # 小程序前端
├── server/            # 后端服务
├── shared/           # 共享类型定义
└── scripts/          # 部署脚本
```

## 快速开始

### 1. 安装依赖
```bash
# 后端
cd server && npm install

# 前端
使用微信开发者工具打开 miniprogram 目录
```

### 2. 配置环境变量
复制 `.env.example` 到 `.env` 并填写配置

### 3. 启动开发服务器
```bash
cd server && npm run dev
```

## 核心功能
- ✅ 快速发起聚会（无需注册）
- ✅ 实时位置收集
- ✅ 智能地点推荐
- ✅ 微信分享邀请
- ✅ 地图可视化展示# yuebei
