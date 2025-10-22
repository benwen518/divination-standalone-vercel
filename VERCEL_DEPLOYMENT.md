# 易经算卦项目 - Vercel 部署指南

## 项目概述

这是一个基于易经的在线算卦应用，支持铜钱占卜和AI智能解读。项目已经过优化，完全适配Vercel平台部署。

## 功能特性

- 🪙 **铜钱占卜**：传统三枚铜钱占卜方式
- 🤖 **AI解读**：基于硅基流动API的智能卦象解读
- 📱 **响应式设计**：支持桌面和移动设备
- ⚡ **现代化界面**：流畅的动画效果和用户体验
- 🔒 **安全部署**：环境变量管理API密钥

## 项目结构

```
divination-standalone/
├── api/                    # Vercel API端点
│   ├── divine.py          # 铜钱占卜API
│   ├── ai.py              # AI解读API
│   ├── hex.py             # 卦象详情API
│   └── index.py           # 主页API
├── static/                # 静态资源
│   ├── index.html         # 主页面
│   ├── script.js          # 前端逻辑
│   ├── styles.css         # 样式文件
│   ├── animate.js         # 动画效果
│   └── public/            # 图片资源
│       └── img/
│           ├── head.webp  # 铜钱正面
│           └── tail.webp  # 铜钱反面
├── data/                  # 易经数据
│   └── iching_basic.json  # 卦象数据库
├── vercel.json            # Vercel配置文件
├── requirements.txt       # Python依赖
└── VERCEL_DEPLOYMENT.md   # 部署说明（本文件）
```

## 部署步骤

### 1. 准备工作

1. **注册Vercel账号**：访问 [vercel.com](https://vercel.com) 注册账号
2. **获取API密钥**：在硅基流动平台获取API密钥
3. **准备代码**：确保项目代码已上传到GitHub仓库

### 2. 部署到Vercel

#### 方法一：通过Vercel Dashboard（推荐）

1. 登录Vercel Dashboard
2. 点击 "New Project"
3. 选择你的GitHub仓库
4. 选择 `divination-standalone` 目录作为根目录
5. 在环境变量设置中添加：
   - `SILICONFLOW_API_KEY`: 你的硅基流动API密钥
6. 点击 "Deploy" 开始部署

#### 方法二：通过Vercel CLI

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录Vercel
vercel login

# 在项目目录下部署
cd divination-standalone
vercel

# 设置环境变量
vercel env add SILICONFLOW_API_KEY
```

### 3. 环境变量配置

在Vercel项目设置中添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|----|----|
| `SILICONFLOW_API_KEY` | 你的API密钥 | 硅基流动平台的API密钥 |

### 4. 自定义域名（可选）

1. 在Vercel Dashboard中进入项目设置
2. 点击 "Domains" 标签
3. 添加你的自定义域名
4. 按照提示配置DNS记录

## API端点说明

### 铜钱占卜 API
- **路径**：`/api/divine/coin`
- **方法**：POST
- **参数**：`{"question": "你的问题"}`
- **返回**：卦象信息和占卜结果

### AI解读 API
- **路径**：`/api/ai`
- **方法**：POST
- **参数**：
  ```json
  {
    "question": "你的问题",
    "hexagram": {
      "code": 1,
      "name": "乾",
      "lines": ["阳", "阳", "阳", "阳", "阳", "阳"]
    },
    "model": "Qwen/QwQ-32B"
  }
  ```
- **返回**：AI解读结果

### 卦象详情 API
- **路径**：`/api/hex/{code}`
- **方法**：GET
- **参数**：卦象编号（1-64）
- **返回**：卦象详细信息

## 技术特点

### Vercel适配优化

1. **无服务器架构**：每个API端点都是独立的无服务器函数
2. **静态资源优化**：静态文件通过Vercel CDN加速
3. **环境变量管理**：安全的API密钥管理
4. **自动HTTPS**：Vercel自动提供SSL证书
5. **全球CDN**：自动部署到全球边缘节点

### 性能优化

- 轻量级依赖：移除了FastAPI等重型框架
- 缓存机制：易经数据库采用内存缓存
- 响应式设计：适配各种设备屏幕
- 异步处理：API调用采用异步模式

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查环境变量是否正确设置
   - 确认API密钥是否有效
   - 查看Vercel函数日志

2. **静态资源404**
   - 确认文件路径是否正确
   - 检查vercel.json路由配置

3. **部署失败**
   - 检查项目结构是否正确
   - 确认vercel.json配置无误
   - 查看构建日志错误信息

### 调试方法

1. **查看函数日志**：在Vercel Dashboard的Functions标签页查看日志
2. **本地测试**：使用 `vercel dev` 在本地测试
3. **检查配置**：确认vercel.json和环境变量配置

## 成本说明

### Vercel免费额度

- **函数调用**：每月100GB-小时
- **带宽**：每月100GB
- **构建时间**：每月6000分钟
- **域名**：免费的.vercel.app子域名

### 硅基流动API成本

- 根据实际API调用量计费
- 建议设置合理的使用限制

## 更新部署

### 自动部署

连接GitHub仓库后，每次推送代码到主分支都会自动触发部署。

### 手动部署

```bash
# 重新部署
vercel --prod

# 部署到预览环境
vercel
```

## 支持与反馈

如果在部署过程中遇到问题，可以：

1. 查看Vercel官方文档
2. 检查项目GitHub Issues
3. 联系项目维护者

---

**祝您部署顺利！愿易经智慧为您指引方向。** 🌟