#!/usr/bin/env python3
"""
华轩书店数据库初始化脚本
"""

import os
import sys
from decimal import Decimal
from datetime import datetime, date
import bcrypt

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Book, UserPreferences

def init_database():
    """初始化数据库"""
    app = create_app('development')

    with app.app_context():
        print("正在创建数据库表...")

        # 删除所有表（如果存在）
        db.drop_all()

        # 创建所有表
        db.create_all()

        print("数据库表创建成功！")

        # 插入初始数据
        insert_sample_data()

        print("数据库初始化完成！")

def insert_sample_data():
    """插入示例数据"""

    # 创建管理员用户
    admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_user = User(
        username='admin',
        email='admin@huaxuan.com',
        password_hash=admin_password,
        real_name='管理员',
        is_active=True,
        email_verified=True
    )
    db.session.add(admin_user)

    # 创建测试用户
    test_password = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    test_user = User(
        username='testuser',
        email='test@example.com',
        password_hash=test_password,
        real_name='测试用户',
        phone='13800138000',
        gender='male',
        is_active=True,
        email_verified=True
    )
    db.session.add(test_user)

    db.session.flush()  # 获取用户ID

    # 为测试用户创建偏好设置
    test_preferences = UserPreferences(user_id=test_user.id)
    db.session.add(test_preferences)

    # 插入丰富的图书数据
    books_data = [
        # 经典文学
        {
            'title': '红楼梦',
            'author': '曹雪芹',
            'publisher': '人民文学出版社',
            'isbn': '9787020002207',
            'category': '文学艺术',
            'description': '中国古典四大名著之一，描写贾宝玉、林黛玉等人的爱情悲剧。',
            'original_price': Decimal('35.00'),
            'current_price': Decimal('29.80'),
            'stock_quantity': 150,
            'cover_image_url': '/images/book-01-188x246.jpg',
            'publication_date': date(2023, 1, 15),
            'page_count': 1200,
            'rating': Decimal('4.8')
        },
        {
            'title': '西游记',
            'author': '吴承恩',
            'publisher': '中华书局',
            'isbn': '9787101003963',
            'category': '文学艺术',
            'description': '经典神话小说，讲述孙悟空等人西天取经的故事。',
            'original_price': Decimal('42.00'),
            'current_price': Decimal('35.60'),
            'stock_quantity': 120,
            'cover_image_url': '/images/book-02-188x246.jpg',
            'publication_date': date(2023, 2, 20),
            'page_count': 980,
            'rating': Decimal('4.7')
        },
        {
            'title': '三国演义',
            'author': '罗贯中',
            'publisher': '岳麓书社',
            'isbn': '9787553900123',
            'category': '文学艺术',
            'description': '中国古典历史小说，描写三国时期的政治军事斗争。',
            'original_price': Decimal('48.00'),
            'current_price': Decimal('42.00'),
            'stock_quantity': 100,
            'cover_image_url': '/images/book-03-188x246.jpg',
            'publication_date': date(2023, 3, 10),
            'page_count': 1100,
            'rating': Decimal('4.6')
        },
        {
            'title': '水浒传',
            'author': '施耐庵',
            'publisher': '人民文学出版社',
            'isbn': '9787020002214',
            'category': '文学艺术',
            'description': '描写108位梁山好汉的英雄传奇故事。',
            'original_price': Decimal('45.00'),
            'current_price': Decimal('38.50'),
            'stock_quantity': 80,
            'cover_image_url': '/images/book-04-188x246.jpg',
            'publication_date': date(2023, 4, 5),
            'page_count': 1050,
            'rating': Decimal('4.5')
        },
        # 计算机技术
        {
            'title': 'Python编程：从入门到实践',
            'author': 'Eric Matthes',
            'publisher': '人民邮电出版社',
            'isbn': '9787115428028',
            'category': '计算机',
            'description': 'Python编程入门经典教程，适合初学者学习。',
            'original_price': Decimal('99.00'),
            'current_price': Decimal('89.00'),
            'stock_quantity': 200,
            'cover_image_url': '/images/book-05-188x246.jpg',
            'publication_date': date(2023, 5, 12),
            'page_count': 650,
            'rating': Decimal('4.9')
        },
        {
            'title': 'JavaScript高级程序设计',
            'author': 'Nicholas C. Zakas',
            'publisher': '人民邮电出版社',
            'isbn': '9787115275790',
            'category': '计算机',
            'description': 'JavaScript权威指南，深入讲解JavaScript核心概念。',
            'original_price': Decimal('109.00'),
            'current_price': Decimal('99.00'),
            'stock_quantity': 150,
            'cover_image_url': '/images/book-06-188x246.jpg',
            'publication_date': date(2023, 6, 8),
            'page_count': 800,
            'rating': Decimal('4.8')
        },
        {
            'title': '算法导论',
            'author': 'Thomas H. Cormen',
            'publisher': '机械工业出版社',
            'isbn': '9787111407010',
            'category': '计算机',
            'description': '计算机算法经典教材，计算机科学必读书籍。',
            'original_price': Decimal('139.00'),
            'current_price': Decimal('128.00'),
            'stock_quantity': 80,
            'cover_image_url': '/images/book-07-188x246.jpg',
            'publication_date': date(2023, 7, 15),
            'page_count': 1200,
            'rating': Decimal('4.7')
        },
        {
            'title': '深入理解计算机系统',
            'author': 'Randal E. Bryant',
            'publisher': '机械工业出版社',
            'isbn': '9787111544937',
            'category': '计算机',
            'description': '计算机系统底层原理详解，程序员进阶必读。',
            'original_price': Decimal('149.00'),
            'current_price': Decimal('139.00'),
            'stock_quantity': 60,
            'cover_image_url': '/images/book-08-188x246.jpg',
            'publication_date': date(2023, 8, 20),
            'page_count': 900,
            'rating': Decimal('4.6')
        },
        # 经济管理
        {
            'title': '经济学原理',
            'author': 'N. Gregory Mankiw',
            'publisher': '北京大学出版社',
            'isbn': '9787301208281',
            'category': '经济管理',
            'description': '经济学入门经典教材，诺贝尔经济学奖得主推荐。',
            'original_price': Decimal('98.00'),
            'current_price': Decimal('88.00'),
            'stock_quantity': 120,
            'cover_image_url': '/images/book-09-188x246.jpg',
            'publication_date': date(2023, 9, 10),
            'page_count': 750,
            'rating': Decimal('4.5')
        },
        {
            'title': '管理学',
            'author': 'Stephen P. Robbins',
            'publisher': '中国人民大学出版社',
            'isbn': '9787300089904',
            'category': '经济管理',
            'description': '管理学经典教材，MBA必读书籍。',
            'original_price': Decimal('85.00'),
            'current_price': Decimal('75.00'),
            'stock_quantity': 100,
            'cover_image_url': '/images/book-10-188x246.jpg',
            'publication_date': date(2023, 10, 5),
            'page_count': 600,
            'rating': Decimal('4.4')
        },
        # 教育考试
        {
            'title': '高等数学',
            'author': '同济大学数学系',
            'publisher': '高等教育出版社',
            'isbn': '9787040396621',
            'category': '教育考试',
            'description': '高等数学经典教材，大学数学必修课程。',
            'original_price': Decimal('62.00'),
            'current_price': Decimal('56.20'),
            'stock_quantity': 300,
            'cover_image_url': '/images/book-11-188x246.jpg',
            'publication_date': date(2023, 11, 15),
            'page_count': 520,
            'rating': Decimal('4.3')
        },
        {
            'title': '线性代数',
            'author': '同济大学数学系',
            'publisher': '高等教育出版社',
            'isbn': '9787040396638',
            'category': '教育考试',
            'description': '线性代数标准教材，工科学生必修课程。',
            'original_price': Decimal('38.00'),
            'current_price': Decimal('32.80'),
            'stock_quantity': 250,
            'cover_image_url': '/images/book-12-188x246.jpg',
            'publication_date': date(2023, 12, 1),
            'page_count': 280,
            'rating': Decimal('4.2')
        },
        # 历史传记
        {
            'title': '史记',
            'author': '司马迁',
            'publisher': '中华书局',
            'isbn': '9787101003970',
            'category': '历史传记',
            'description': '中国第一部纪传体通史，史学经典著作。',
            'original_price': Decimal('78.00'),
            'current_price': Decimal('68.00'),
            'stock_quantity': 90,
            'cover_image_url': '/images/book-13-188x246.jpg',
            'publication_date': date(2024, 1, 10),
            'page_count': 1500,
            'rating': Decimal('4.9')
        },
        {
            'title': '万历十五年',
            'author': '黄仁宇',
            'publisher': '中华书局',
            'isbn': '9787101025323',
            'category': '历史传记',
            'description': '以万历十五年为切入点，分析明朝政治制度。',
            'original_price': Decimal('42.00'),
            'current_price': Decimal('36.00'),
            'stock_quantity': 110,
            'cover_image_url': '/images/book-14-188x246.jpg',
            'publication_date': date(2024, 2, 20),
            'page_count': 350,
            'rating': Decimal('4.6')
        },
        # 艺术设计
        {
            'title': '设计心理学',
            'author': 'Donald A. Norman',
            'publisher': '中信出版社',
            'isbn': '9787508663326',
            'category': '艺术设计',
            'description': '设计师必读经典，用户体验设计指南。',
            'original_price': Decimal('55.00'),
            'current_price': Decimal('49.00'),
            'stock_quantity': 80,
            'cover_image_url': '/images/book-15-188x246.jpg',
            'publication_date': date(2024, 3, 15),
            'page_count': 320,
            'rating': Decimal('4.7')
        }
    ]

    # 插入图书数据
    for book_data in books_data:
        book = Book(**book_data)
        db.session.add(book)

    # 提交所有更改
    try:
        db.session.commit()
        print(f"成功插入 {len(books_data)} 本图书")
        print("示例数据插入完成！")

        # 打印测试账号信息
        print("\n=== 测试账号信息 ===")
        print("管理员账号:")
        print("  用户名: admin")
        print("  邮箱: admin@huaxuan.com")
        print("  密码: admin123")
        print("\n普通用户账号:")
        print("  用户名: testuser")
        print("  邮箱: test@example.com")
        print("  密码: 123456")

    except Exception as e:
        db.session.rollback()
        print(f"数据插入失败: {str(e)}")
        raise

if __name__ == '__main__':
    print("华轩书店数据库初始化")
    print("=" * 50)

    try:
        init_database()
        print("\n✅ 数据库初始化成功！")
        print("\n🚀 现在可以启动后端服务:")
        print("   python app.py")

    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {str(e)}")
        sys.exit(1)