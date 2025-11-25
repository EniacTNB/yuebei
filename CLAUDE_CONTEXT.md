# Claude Code 项目上下文

## 项目概述
**项目名称**：约呗（YueBei）
**描述**：智能聚会地点推荐小程序，帮助多人找到最方便的聚会地点
**开始时间**：2024-11-25

## 技术栈
- **前端**：微信小程序原生开发
- **后端**：Python FastAPI
- **数据库**：MongoDB（无认证）+ Redis（可选）
- **地图**：腾讯地图API（使用模拟数据）

## 核心功能
1. 无需注册，快速发起聚会
2. 6位邀请码分享机制
3. 收集多人位置
4. 智能算法推荐最优地点
5. 实时更新推荐结果

## 当前进度
- ✅ 项目框架搭建完成
- ✅ 后端API接口完成
- ✅ 核心算法实现
- ✅ 小程序4个页面完成
- ⏸️ MongoDB连接问题（需要本地启动MongoDB）

## 已知问题
1. **MongoDB认证错误**
   - 原因：Docker容器需要认证，本地MongoDB未启动
   - 解决：使用本地MongoDB或移除认证

2. **小程序测试**
   - 需要在app.js中修改baseUrl为实际后端地址

## 项目结构
```
yuebei/
├── miniprogram/     # 微信小程序
│   ├── pages/
│   │   ├── index/   # 首页
│   │   ├── create/  # 创建聚会
│   │   ├── join/    # 加入聚会
│   │   └── result/  # 推荐结果
│   └── app.js       # 配置baseUrl
├── server/          # Python后端
│   ├── main.py      # FastAPI入口
│   ├── api/         # API接口
│   ├── core/        # 算法模块
│   └── .env         # 环境配置
└── docker-compose.yml
```

## 快速启动命令
```bash
# 后端启动
cd server
source venv/bin/activate
uvicorn main:app --reload

# MongoDB启动（macOS）
brew services start mongodb-community
# 或
mongod --dbpath /tmp/mongodb --fork
```

## 下一步计划
1. 解决MongoDB连接问题
2. 测试完整的创建-加入-推荐流程
3. 部署到云服务器
4. 申请地图API密钥

## 给Claude的提示
当在新电脑继续开发时，可以这样说：
"我要继续开发约呗项目，这是一个智能聚会地点推荐小程序。
当前使用Python FastAPI后端，遇到MongoDB连接问题需要解决。
请先读取CLAUDE_CONTEXT.md了解项目状态。"

## 最近的对话要点
- 用户要求后端使用Python而不是Node.js
- 不需要社交登录，使用临时ID
- 快速发起，一个人就可以创建聚会
- 重点是算法推荐的准确性

---
最后更新：2024-11-25