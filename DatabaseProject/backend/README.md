# 华轩书店后端 API

## 📋 项目简介

华轩书店后端API系统，基于Flask框架开发，提供完整的图书电商功能，包括用户管理、图书浏览、购物车、订单处理等核心功能。

## 🏗️ 技术栈

- **框架**: Flask 2.3.3
- **数据库**: MySQL + SQLAlchemy ORM
- **认证**: JWT (Flask-JWT-Extended)
- **跨域**: Flask-CORS
- **密码加密**: bcrypt
- **缓存**: Redis (可选)
- **部署**: Gunicorn + Nginx (生产环境)

## 📁 项目结构

```
backend/
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── models.py             # 数据模型
├── requirements.txt      # 依赖包列表
├── init_database.py      # 数据库初始化脚本
├── start.py             # 启动脚本
├── .env.example         # 环境变量示例
├── routes/              # 路由模块
│   ├── __init__.py
│   ├── user.py          # 用户相关路由
│   ├── book.py          # 图书相关路由
│   └── order.py         # 订单相关路由
├── utils/               # 工具函数
│   ├── __init__.py
│   └── helpers.py       # 辅助函数
├── services/            # 业务服务
│   └── email_service.py # 邮件服务
└── logs/               # 日志文件 (运行时生成)
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+ 或 8.0+
- Redis (可选，用于缓存)

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件，修改数据库连接等信息
nano .env
```

### 4. 初始化数据库

```bash
# 创建数据库 (MySQL)
mysql -u root -p
CREATE DATABASE books CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 初始化数据库表和示例数据
python init_database.py
```

### 5. 启动服务

```bash
# 开发环境启动
python start.py

# 或者直接运行
python app.py
```

服务将在 `http://localhost:5000` 启动

## 📚 API 文档

详细的API接口文档请参考 [API接口文档.md](../API接口文档.md)

### 主要接口概览

#### 用户认证
- `POST /api/user/register` - 用户注册
- `POST /api/user/login` - 用户登录
- `GET /api/user/profile` - 获取用户资料
- `PUT /api/user/profile` - 更新用户资料

#### 图书管理
- `GET /api/book/` - 获取图书列表
- `GET /api/book/{id}` - 获取图书详情
- `GET /api/book/search` - 搜索图书
- `GET /api/book/categories` - 获取分类

#### 购物车
- `GET /api/order/cart` - 获取购物车
- `POST /api/order/cart/add` - 添加到购物车
- `PUT /api/order/cart/update` - 更新购物车
- `DELETE /api/order/cart/remove` - 移除商品

#### 订单管理
- `POST /api/order/` - 创建订单
- `GET /api/order/` - 获取订单列表
- `GET /api/order/{id}` - 获取订单详情
- `PUT /api/order/{id}/pay` - 支付订单

## 🗄️ 数据库设计

### 主要数据表

- `users` - 用户信息
- `books` - 图书信息
- `orders` - 订单信息
- `order_items` - 订单项
- `shopping_cart` - 购物车
- `browsing_history` - 浏览历史
- `user_preferences` - 用户偏好
- `forum_posts` - 论坛帖子
- `forum_replies` - 论坛回复

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | 运行环境 | development |
| `SECRET_KEY` | Flask密钥 | - |
| `JWT_SECRET_KEY` | JWT密钥 | - |
| `DATABASE_URL` | 数据库连接 | - |
| `REDIS_URL` | Redis连接 | redis://localhost:6379/0 |
| `MAIL_SERVER` | 邮件服务器 | smtp.qq.com |

### 数据库配置

```python
# MySQL 连接示例
DATABASE_URL = 'mysql+mysqlconnector://username:password@localhost/database_name'
```

## 🧪 测试

### 运行测试

```bash
# 单元测试
python -m pytest tests/

# API测试
python -m pytest tests/test_api.py
```

### 手动测试

```bash
# 健康检查
curl http://localhost:5000/api/health

# 用户登录
curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```

## 📦 部署

### 生产环境部署

1. **使用 Gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **使用 Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

3. **Nginx 配置**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 安全考虑

- JWT token 认证
- 密码 bcrypt 加密
- SQL 注入防护
- CORS 跨域控制
- 输入数据验证
- 错误信息脱敏

## 📝 开发规范

- 遵循 PEP 8 代码规范
- 使用类型提示
- 编写单元测试
- 添加接口文档
- 记录变更日志

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务状态
   - 确认连接配置正确
   - 检查防火墙设置

2. **JWT 认证失败**
   - 检查 token 格式
   - 确认密钥配置
   - 验证 token 有效期

3. **CORS 错误**
   - 检查前端域名配置
   - 确认 CORS 中间件设置

## 📞 技术支持

如有问题，请：
1. 查看日志文件 `logs/bookstore.log`
2. 检查 API 接口文档
3. 参考故障排除指南
4. 联系开发团队

## 📄 许可证

MIT License

---
**版本**: v1.0  
**更新时间**: 2024-11-28  
**维护团队**: 华轩书店开发团队
