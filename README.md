# WebSocket 实时聊天室

基于 Python FastAPI + WebSocket 实现的 B/S 架构实时聊天室应用。

## 功能特性

### 核心功能
- ✅ **用户登录**：用户名唯一性校验，拒绝重复账号登录
- ✅ **在线用户实时显示**：客户端同步拉取全局在线用户列表
- ✅ **消息实时发送**：单客户端输入消息瞬时推送至服务端
- ✅ **消息实时接收**：服务端推送消息客户端即时渲染展示
- ✅ **全局消息广播**：单人发送消息推送至所有在线客户端
- ✅ **聊天记录本地持久化**：客户端本地 JSON 存储历史聊天记录，刷新页面不丢失

### 扩展功能
- 🚀 一对一私聊：指定单一用户定向发送消息
- 🚀 多群组独立聊天：群组消息互不干扰
- 🚀 二进制流文件传输：支持图片、文档等小文件传输
- 🚀 表情包支持：前端嵌入表情编码，支持表情包消息收发

## 技术栈

### 后端
- **框架**：FastAPI
- **WebSocket**：asyncio + WebSocket 握手协议
- **并发**：异步处理多用户连接
- **数据存储**：内存 + 可选持久化

### 前端
- **HTML5**：WebSocket API 客户端实现
- **JavaScript**：消息处理与 UI 交互
- **LocalStorage**：本地聊天记录持久化
- **CSS**：响应式界面设计

## 项目结构

```
WebSocket/
├── backend/                    # 后端服务
│   ├── app.py                 # FastAPI 主应用
│   ├── websocket_manager.py   # WebSocket 连接管理
│   ├── user_manager.py        # 用户会话管理
│   ├── message_handler.py     # 消息转发处理
│   └── requirements.txt       # 依赖包
├── frontend/                  # 前端应用
│   ├── index.html            # 聊天界面
│   ├── css/
│   │   └── style.css         # 样式表
│   └── js/
│       └── chat.js           # 聊天逻辑
├── docs/                      # 文档
│   ├── design.md             # 设计文档
│   ├── protocol.md           # WebSocket 协议定义
│   └── test_report.md        # 测试报告
└── README.md                  # 项目说明
```

## WebSocket 握手与连接管理

本项目遵循 WebSocket 握手协议 (RFC 6455)，完成 HTTP 到 WebSocket 的升级转换：

1. **HTTP 升级请求**：客户端发送 HTTP 升级请求
2. **握手验证**：服务端验证 Sec-WebSocket-Key
3. **连接建立**：101 Switching Protocols 响应
4. **全双工通信**：建立持久连接进行双向通信
5. **连接保活**：心跳包机制保持连接活跃
6. **优雅关闭**：断开连接时的清理处理

## 快速开始

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 运行服务

```bash
python app.py
```

服务将在 `http://localhost:8000` 启动

### 打开客户端

在浏览器中打开 `frontend/index.html`

## 消息协议

### 消息格式（JSON）

```json
{
  "type": "message|login|logout|user_list",
  "username": "用户名",
  "content": "消息内容",
  "timestamp": "时间戳",
  "target_user": "目标用户（私聊时）",
  "group_id": "群组ID"
}
```

### 消息类型

- `login`：用户登录
- `logout`：用户登出
- `message`：普通消息（广播）
- `private_message`：私聊消息
- `user_list`：在线用户列表
- `group_message`：群组消息

## 运行测试

### 单用户测试
1. 打开浏览器，访问客户端界面
2. 输入用户名登录
3. 发送消息，验证消息显示

### 多用户并发测试
1. 多个浏览器标签页同时登录
2. 从不同客户端发送消息
3. 验证消息实时广播到所有在线用户
4. 检查在线用户列表实时更新

### 掉线重连测试
1. 登录后断开网络连接
2. 恢复网络连接
3. 验证历史消息加载
4. 验证能够继续收发消息

## 连接保活机制

采用心跳包 (Heartbeat) 机制保持连接活跃：

- **服务端心跳**：每 30 秒发送 ping 帧
- **客户端心跳**：接收 pong 帧响应
- **超时检测**：60 秒无响应则判断连接断开
- **自动重连**：客户端断开后自动重新连接

## 本地存储

聊天记录使用 LocalStorage 存储：

- 存储结构：JSON 数组
- 存储容量：约 5-10MB
- 清空方式：浏览器清空缓存时删除
- 数据加密：支持可选加密存储

## API 接口

### WebSocket 端点

```
ws://localhost:8000/ws/{username}
```

### REST API 端点

- `GET /api/users` - 获取在线用户列表
- `GET /api/messages` - 获取历史消息
- `POST /api/messages` - 发送消息
- `DELETE /api/sessions/{username}` - 删除会话

## 项目文档

详见 `docs/` 目录：

- **design.md** - 详细设计文档
- **protocol.md** - WebSocket 协议定义
- **test_report.md** - 运行测试结果

## 常见问题

**Q: 如何处理网络不稳定导致的连接断开？**
A: 采用自动重连机制，客户端检测到连接断开后自动重连，同时保留未发送消息的本地队列。

**Q: 消息是否支持加密？**
A: 基础版本不支持端到端加密，可在扩展功能中添加消息加密模块。

**Q: 最大支持多少并发用户？**
A: 取决于服务器配置和网络带宽，建议使用生产级服务器部署。

## 许可证

MIT License

## 作者

Zyy023577

## 最后更新

2026-06-18