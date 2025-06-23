from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    real_name = db.Column(db.String(50))
    gender = db.Column(db.Enum('male', 'female', 'other', name='gender_enum'))
    birth_date = db.Column(db.Date)
    address = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('ShoppingCart', backref='user', lazy=True)
    browsing_history = db.relationship('BrowsingHistory', backref='user', lazy=True)
    forum_posts = db.relationship('ForumPost', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'realName': self.real_name,
            'gender': self.gender,
            'birthDate': self.birth_date.isoformat() if self.birth_date else None,
            'address': self.address,
            'avatarUrl': self.avatar_url,
            'registrationDate': self.registration_date.isoformat() if self.registration_date else None,
            'lastLogin': self.last_login.isoformat() if self.last_login else None,
            'isActive': self.is_active,
            'emailVerified': self.email_verified
        }

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    isbn = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    original_price = db.Column(Numeric(10, 2))
    current_price = db.Column(Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0)
    cover_image_url = db.Column(db.String(255))
    publication_date = db.Column(db.Date)
    page_count = db.Column(db.Integer)
    language = db.Column(db.String(20), default='中文')
    is_active = db.Column(db.Boolean, default=True)
    sales_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    rating = db.Column(Numeric(3, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    cart_items = db.relationship('ShoppingCart', backref='book', lazy=True)
    browsing_history = db.relationship('BrowsingHistory', backref='book', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'isbn': self.isbn,
            'category': self.category,
            'description': self.description,
            'originalPrice': float(self.original_price) if self.original_price else None,
            'currentPrice': float(self.current_price) if self.current_price else None,
            'stockQuantity': self.stock_quantity,
            'coverImageUrl': self.cover_image_url,
            'publicationDate': self.publication_date.isoformat() if self.publication_date else None,
            'pageCount': self.page_count,
            'language': self.language,
            'isActive': self.is_active,
            'salesCount': self.sales_count,
            'viewCount': self.view_count,
            'rating': float(self.rating) if self.rating else 0.0
        }

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'paid', 'shipped', 'delivered', 'cancelled', name='order_status'), default='pending')
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded', name='payment_status'), default='pending')
    delivery_method = db.Column(db.String(50), default='email')  # 新增：发送方式（email/physical）
    shipping_address = db.Column(db.Text)
    shipping_phone = db.Column(db.String(20))
    shipping_name = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)

    # 关系
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'orderNumber': self.order_number,
            'totalAmount': float(self.total_amount),
            'status': self.status,
            'paymentMethod': self.payment_method,
            'paymentStatus': self.payment_status,
            'deliveryMethod': self.delivery_method,
            'shippingAddress': self.shipping_address,
            'shippingPhone': self.shipping_phone,
            'shippingName': self.shipping_name,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'paidAt': self.paid_at.isoformat() if self.paid_at else None,
            'shippedAt': self.shipped_at.isoformat() if self.shipped_at else None,
            'deliveredAt': self.delivered_at.isoformat() if self.delivered_at else None,
            'items': [item.to_dict() for item in self.order_items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(Numeric(10, 2), nullable=False)
    total_price = db.Column(Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'bookId': self.book_id,
            'quantity': self.quantity,
            'unitPrice': float(self.unit_price),
            'totalPrice': float(self.total_price),
            'book': self.book.to_dict() if self.book else None
        }

class ShoppingCart(db.Model):
    __tablename__ = 'shopping_cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book'),)

    def to_dict(self):
        return {
            'id': self.id,
            'bookId': self.book_id,
            'quantity': self.quantity,
            'book': self.book.to_dict() if self.book else None,
            'totalPrice': float(self.book.current_price * self.quantity) if self.book and self.book.current_price else 0
        }

class BrowsingHistory(db.Model):
    __tablename__ = 'browsing_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'bookId': self.book_id,
            'viewedAt': self.viewed_at.isoformat() if self.viewed_at else None,
            'book': self.book.to_dict() if self.book else None
        }

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    preferred_categories = db.Column(db.Text)  # JSON字符串
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default='zh-CN')
    theme = db.Column(db.String(20), default='light')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'userId': self.user_id,
            'preferredCategories': json.loads(self.preferred_categories) if self.preferred_categories else [],
            'emailNotifications': self.email_notifications,
            'smsNotifications': self.sms_notifications,
            'language': self.language,
            'theme': self.theme
        }

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    last_reply_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    replies = db.relationship('ForumReply', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'isPinned': self.is_pinned,
            'isLocked': self.is_locked,
            'viewCount': self.view_count,
            'replyCount': self.reply_count,
            'lastReplyAt': self.last_reply_at.isoformat() if self.last_reply_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatarUrl': self.author.avatar_url
            } if self.author else None
        }

class ForumReply(db.Model):
    __tablename__ = 'forum_replies'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('forum_replies.id'))  # 支持回复的回复
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    author = db.relationship('User', backref='forum_replies')
    parent = db.relationship('ForumReply', remote_side=[id], backref='children')

    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.post_id,
            'content': self.content,
            'parentId': self.parent_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatarUrl': self.author.avatar_url
            } if self.author else None
        }
