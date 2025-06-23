# 华轩书店 API 接口文档

## 📋 概述

华轩书店后端API提供完整的图书电商功能，包括用户管理、图书浏览、购物车、订单处理等核心功能。

**基础信息:**
- 基础URL: `http://localhost:5000/api`
- 认证方式: JWT Bearer Token
- 数据格式: JSON
- 字符编码: UTF-8

## 🔐 认证说明

大部分API需要在请求头中包含JWT令牌：

```
Authorization: Bearer <your_jwt_token>
```

## 📊 统一响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

## 👤 用户认证 API

### 1. 用户注册
**POST** `/user/register`

**请求体:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "phone": "13800138000",
  "realName": "张三",
  "gender": "male"
}
```

**响应:**
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "realName": "张三"
    }
  }
}
```

### 2. 用户登录
**POST** `/user/login`

**请求体:**
```json
{
  "email": "test@example.com",
  "password": "123456"
}
```

**响应:** 同注册接口

### 3. 获取用户资料
**GET** `/user/profile`

**需要认证:** ✅

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "realName": "张三",
    "gender": "male",
    "address": "北京市朝阳区...",
    "avatarUrl": null,
    "isActive": true
  }
}
```

### 4. 更新用户资料
**PUT** `/user/profile`

**需要认证:** ✅

**请求体:**
```json
{
  "realName": "李四",
  "phone": "13900139000",
  "gender": "female",
  "address": "上海市浦东新区..."
}
```

### 5. 修改密码
**POST** `/user/change-password`

**需要认证:** ✅

**请求体:**
```json
{
  "currentPassword": "123456",
  "newPassword": "newpassword123"
}
```

### 6. 获取用户偏好设置
**GET** `/user/preferences`

**需要认证:** ✅

**响应:**
```json
{
  "success": true,
  "data": {
    "preferredCategories": ["计算机", "文学艺术"],
    "emailNotifications": true,
    "smsNotifications": false,
    "language": "zh-CN",
    "theme": "light"
  }
}
```

### 7. 更新用户偏好设置
**PUT** `/user/preferences`

**需要认证:** ✅

**请求体:**
```json
{
  "preferredCategories": ["计算机", "经济管理"],
  "emailNotifications": false,
  "smsNotifications": true,
  "theme": "dark"
}
```

## 📚 图书管理 API

### 1. 获取图书列表
**GET** `/book/`

**查询参数:**
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 12)
- `category`: 分类筛选
- `sort_by`: 排序字段 (created_at, current_price, sales_count, rating)
- `order`: 排序方向 (asc, desc)

**响应:**
```json
{
  "success": true,
  "data": {
    "books": [
      {
        "id": 1,
        "title": "市场营销原理",
        "author": "菲利普·科特勒",
        "publisher": "清华大学出版社",
        "category": "经济管理",
        "currentPrice": 27.00,
        "originalPrice": 35.00,
        "stockQuantity": 50,
        "coverImageUrl": "/images/book-01-188x246.jpg",
        "rating": 4.5,
        "salesCount": 0
      }
    ],
    "pagination": {
      "page": 1,
      "perPage": 12,
      "total": 8,
      "totalPages": 1,
      "hasPrev": false,
      "hasNext": false
    }
  }
}
```

### 2. 获取图书详情
**GET** `/book/{book_id}`

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "市场营销原理",
    "author": "菲利普·科特勒",
    "publisher": "清华大学出版社",
    "isbn": "9787302123456",
    "category": "经济管理",
    "description": "市场营销学的经典教材...",
    "currentPrice": 27.00,
    "originalPrice": 35.00,
    "stockQuantity": 50,
    "coverImageUrl": "/images/book-01-188x246.jpg",
    "publicationDate": "2023-01-15",
    "pageCount": 456,
    "language": "中文",
    "rating": 4.5,
    "viewCount": 1,
    "salesCount": 0
  }
}
```

### 3. 搜索图书
**GET** `/book/search`

**查询参数:**
- `q`: 搜索关键词
- `category`: 分类筛选
- `min_price`: 最低价格
- `max_price`: 最高价格
- `page`: 页码
- `per_page`: 每页数量
- `sort_by`: 排序字段
- `order`: 排序方向

**响应:** 同图书列表，额外包含搜索信息

### 4. 获取图书分类
**GET** `/book/categories`

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "name": "计算机",
      "count": 4
    },
    {
      "name": "经济管理",
      "count": 3
    },
    {
      "name": "文学艺术",
      "count": 1
    }
  ]
}
```

### 5. 获取推荐图书
**GET** `/book/recommended`

**查询参数:**
- `limit`: 返回数量 (默认: 8)

### 6. 获取热门图书
**GET** `/book/hot`

**查询参数:**
- `limit`: 返回数量 (默认: 10)

### 7. 获取新书
**GET** `/book/new`

**查询参数:**
- `limit`: 返回数量 (默认: 10)

### 8. 获取个性化推荐
**GET** `/book/personalized`

**需要认证:** ✅

**查询参数:**
- `limit`: 返回数量 (默认: 10)

## 🛒 购物车 API

### 1. 获取购物车
**GET** `/order/cart`

**需要认证:** ✅

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "bookId": 1,
        "quantity": 2,
        "book": {
          "id": 1,
          "title": "市场营销原理",
          "currentPrice": 27.00,
          "coverImageUrl": "/images/book-01-188x246.jpg"
        },
        "totalPrice": 54.00
      }
    ],
    "totalAmount": 54.00,
    "itemCount": 1
  }
}
```

### 2. 添加到购物车
**POST** `/order/cart/add`

**需要认证:** ✅

**请求体:**
```json
{
  "bookId": 1,
  "quantity": 2
}
```

### 3. 更新购物车商品数量
**PUT** `/order/cart/update`

**需要认证:** ✅

**请求体:**
```json
{
  "itemId": 1,
  "quantity": 3
}
```

### 4. 移除购物车商品
**DELETE** `/order/cart/remove?itemId=1`

**需要认证:** ✅

### 5. 清空购物车
**DELETE** `/order/cart/clear`

**需要认证:** ✅

## 📦 订单管理 API

### 1. 创建订单
**POST** `/order/`

**需要认证:** ✅

**请求体:**
```json
{
  "items": [
    {
      "bookId": 1,
      "quantity": 2
    },
    {
      "bookId": 2,
      "quantity": 1
    }
  ],
  "shippingAddress": "北京市朝阳区xxx街道xxx号",
  "shippingPhone": "13800138000",
  "shippingName": "张三",
  "notes": "请在工作日送达"
}
```

**响应:**
```json
{
  "success": true,
  "message": "订单创建成功",
  "data": {
    "id": 1,
    "orderNumber": "HX20241128143025ABC12345",
    "totalAmount": 79.00,
    "status": "pending",
    "paymentStatus": "pending",
    "shippingAddress": "北京市朝阳区xxx街道xxx号",
    "shippingPhone": "13800138000",
    "shippingName": "张三",
    "createdAt": "2024-11-28T14:30:25.123Z",
    "items": [
      {
        "id": 1,
        "bookId": 1,
        "quantity": 2,
        "unitPrice": 27.00,
        "totalPrice": 54.00,
        "book": {
          "id": 1,
          "title": "市场营销原理",
          "coverImageUrl": "/images/book-01-188x246.jpg"
        }
      }
    ]
  }
}
```

### 2. 获取订单列表
**GET** `/order/`

**需要认证:** ✅

**查询参数:**
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 10)
- `status`: 订单状态筛选 (pending, paid, shipped, delivered, cancelled)

**响应:**
```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "id": 1,
        "orderNumber": "HX20241128143025ABC12345",
        "totalAmount": 79.00,
        "status": "pending",
        "paymentStatus": "pending",
        "createdAt": "2024-11-28T14:30:25.123Z",
        "items": [...]
      }
    ],
    "pagination": {
      "page": 1,
      "perPage": 10,
      "total": 1,
      "totalPages": 1,
      "hasPrev": false,
      "hasNext": false
    }
  }
}
```

### 3. 获取订单详情
**GET** `/order/{order_id}`

**需要认证:** ✅

**响应:** 同创建订单响应格式

### 4. 支付订单
**PUT** `/order/{order_id}/pay`

**需要认证:** ✅

**请求体:**
```json
{
  "paymentMethod": "alipay"
}
```

**响应:**
```json
{
  "success": true,
  "message": "支付成功",
  "data": {
    "id": 1,
    "status": "paid",
    "paymentStatus": "paid",
    "paymentMethod": "alipay",
    "paidAt": "2024-11-28T14:35:00.123Z"
  }
}
```

### 5. 取消订单
**PUT** `/order/{order_id}/cancel`

**需要认证:** ✅

**响应:**
```json
{
  "success": true,
  "message": "订单已取消",
  "data": {
    "id": 1,
    "status": "cancelled"
  }
}
```

## 📖 浏览历史 API

### 1. 获取浏览历史
**GET** `/user/browsing-history`

**需要认证:** ✅

**查询参数:**
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 20)

**响应:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": 1,
        "bookId": 1,
        "viewedAt": "2024-11-28T14:30:00.123Z",
        "book": {
          "id": 1,
          "title": "市场营销原理",
          "author": "菲利普·科特勒",
          "currentPrice": 27.00,
          "coverImageUrl": "/images/book-01-188x246.jpg"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "perPage": 20,
      "total": 1,
      "totalPages": 1,
      "hasPrev": false,
      "hasNext": false
    }
  }
}
```

### 2. 添加浏览历史
**POST** `/user/browsing-history`

**需要认证:** ✅

**请求体:**
```json
{
  "bookId": 1
}
```

### 3. 清空浏览历史
**DELETE** `/user/browsing-history`

**需要认证:** ✅

## 🔧 系统 API

### 1. 健康检查
**GET** `/health`

**响应:**
```json
{
  "success": true,
  "message": "服务运行正常",
  "version": "1.0.0"
}
```

## 📝 错误代码说明

| 错误代码 | 说明 |
|---------|------|
| `USERNAME_EXISTS` | 用户名已存在 |
| `EMAIL_EXISTS` | 邮箱已被注册 |
| `INVALID_EMAIL` | 邮箱格式不正确 |
| `PASSWORD_TOO_SHORT` | 密码长度不足 |
| `USER_NOT_FOUND` | 用户不存在 |
| `INVALID_PASSWORD` | 密码错误 |
| `TOKEN_EXPIRED` | 令牌已过期 |
| `TOKEN_REQUIRED` | 需要认证令牌 |
| `BOOK_NOT_FOUND` | 图书不存在 |
| `INSUFFICIENT_STOCK` | 库存不足 |
| `ORDER_NOT_FOUND` | 订单不存在 |
| `INVALID_ORDER_STATUS` | 订单状态不正确 |
| `CART_ITEM_NOT_FOUND` | 购物车商品不存在 |

## 🚀 快速开始

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python init_database.py
```

### 3. 启动服务
```bash
python app.py
```

### 4. 测试API
```bash
# 健康检查
curl http://localhost:5000/api/health

# 用户登录
curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'

# 获取图书列表
curl http://localhost:5000/api/book/
```

## 📞 技术支持

如有问题，请联系开发团队或查看项目文档。

---
**文档版本**: v1.0
**更新时间**: 2024-11-28
**维护团队**: 华轩书店开发团队
```
