# 易经算卦 - 在线占卜应用

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fbenwen518%2Fdivination-standalone&env=SILICONFLOW_API_KEY&envDescription=硅基流动API密钥&envLink=https%3A%2F%2Fsiliconflow.cn%2F)

一个基于易经的现代化在线算卦应用，支持传统铜钱占卜和AI智能解读。

## ✨ 功能特性

- 🪙 **传统铜钱占卜** - 三枚铜钱投掷占卜，遵循古法
- 🤖 **AI智能解读** - 基于硅基流动API的专业卦象解读
- 📱 **响应式设计** - 完美适配桌面和移动设备
- ⚡ **现代化界面** - 流畅的动画效果和优雅的用户体验
- 🚀 **一键部署** - 完全适配Vercel平台，支持一键部署

## 🎯 在线体验

[点击这里体验在线版本](https://divination-standalone.vercel.app)

## 🚀 快速部署

### 方法一：一键部署到Vercel（推荐）

点击下面的按钮，一键部署到Vercel：

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fbenwen518%2Fdivination-standalone&env=SILICONFLOW_API_KEY&envDescription=硅基流动API密钥&envLink=https%3A%2F%2Fsiliconflow.cn%2F)

部署时需要设置环境变量：
- `SILICONFLOW_API_KEY`: 在[硅基流动](https://siliconflow.cn/)获取API密钥

### 方法二：手动部署

1. **克隆仓库**
   ```bash
   git clone https://github.com/benwen518/divination-standalone.git
   cd divination-standalone
   ```

2. **部署到Vercel**
   - 访问 [vercel.com](https://vercel.com)
   - 导入GitHub仓库
   - 设置环境变量 `SILICONFLOW_API_KEY`
   - 点击部署

## 🛠️ 本地开发

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **设置环境变量**
   ```bash
   export SILICONFLOW_API_KEY="your_api_key_here"
   ```

3. **启动服务**
   ```bash
   python app.py
   ```

4. **访问应用**
   打开浏览器访问 `http://localhost:8080`

## 📁 项目结构

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
│   └── public/            # 图片资源
├── data/                  # 易经数据
│   └── iching_basic.json  # 卦象数据库
├── vercel.json            # Vercel配置
└── README.md              # 项目说明
```

## 🔧 API接口

### 铜钱占卜
```
POST /api/divine/coin
Content-Type: application/json

{
  "question": "今天运势如何？"
}
```

### AI解读
```
POST /api/ai
Content-Type: application/json

{
  "question": "今天运势如何？",
  "hexagram": {
    "code": 1,
    "name": "乾",
    "lines": ["阳", "阳", "阳", "阳", "阳", "阳"]
  }
}
```

### 卦象详情
```
GET /api/hex/{code}
```

## 🌟 技术特点

- **无服务器架构** - 基于Vercel的无服务器函数
- **全球CDN加速** - 静态资源全球分发
- **自动HTTPS** - 安全的HTTPS连接
- **环境变量管理** - 安全的API密钥管理
- **响应式设计** - 适配各种设备

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**愿易经智慧为您指引方向** 🌟