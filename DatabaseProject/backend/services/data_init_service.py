# -*- coding: utf-8 -*-
"""
数据初始化服务
在服务启动时自动初始化图书数据，确保前端显示的图书与数据库完全同步
"""

from models import db, Book
from datetime import date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def init_book_data():
    """
    初始化图书数据 - 与前端首页显示完全一致
    每次启动服务时都会检查并更新图书数据
    """
    try:
        print("🔄 开始初始化图书数据...")
        
        # 前端首页显示的图书数据（必须与index.html完全一致）
        books_data = [
            {
                'id': 1,
                'title': '市场营销原理',
                'author': '菲利普·科特勒',
                'publisher': '清华大学出版社',
                'isbn': '9787302123456',
                'category': '商业管理',
                'description': '市场营销学经典教材，全面介绍现代营销理论与实践。',
                'original_price': Decimal('35.00'),
                'current_price': Decimal('27.00'),
                'stock_quantity': 80,
                'cover_image_url': 'images/book-01-188x246.jpg',
                'publication_date': date(2024, 1, 15),
                'page_count': 520,
                'rating': Decimal('4.6')
            },
            {
                'id': 2,
                'title': '领导力艺术',
                'author': '乔安妮·舒尔茨',
                'publisher': '商务印书馆',
                'isbn': '9787100123456',
                'category': '商业管理',
                'description': '关于领导力发展的经典著作，提供实用的领导技巧和管理智慧。',
                'original_price': Decimal('35.00'),
                'current_price': Decimal('25.00'),
                'stock_quantity': 50,
                'cover_image_url': 'images/book-02-188x246.jpg',
                'publication_date': date(2024, 2, 10),
                'page_count': 380,
                'rating': Decimal('4.7')
            },
            {
                'id': 3,
                'title': '网页设计基础',
                'author': '张明华',
                'publisher': '电子工业出版社',
                'isbn': '9787121234567',
                'category': '计算机技术',
                'description': '系统介绍网页设计基础知识，包括HTML、CSS、JavaScript等核心技术。',
                'original_price': Decimal('28.00'),
                'current_price': Decimal('21.00'),
                'stock_quantity': 30,
                'cover_image_url': 'images/book-03-188x246.jpg',
                'publication_date': date(2024, 3, 5),
                'page_count': 450,
                'rating': Decimal('4.5')
            },
            {
                'id': 4,
                'title': '网页设计中的网格系统',
                'author': '李华强',
                'publisher': '人民邮电出版社',
                'isbn': '9787115345678',
                'category': '计算机技术',
                'description': '深入讲解网页设计中网格系统的应用，提升设计效率和美观度。',
                'original_price': Decimal('32.00'),
                'current_price': Decimal('24.00'),
                'stock_quantity': 25,
                'cover_image_url': 'images/book-04-188x246.jpg',
                'publication_date': date(2024, 3, 20),
                'page_count': 320,
                'rating': Decimal('4.4')
            },
            {
                'id': 5,
                'title': '揭示用户放弃网站原因的工具',
                'author': '王小明',
                'publisher': '机械工业出版社',
                'isbn': '9787111456789',
                'category': '计算机技术',
                'description': '用户体验分析工具和方法，帮助网站提升用户留存率。',
                'original_price': Decimal('29.00'),
                'current_price': Decimal('22.00'),
                'stock_quantity': 35,
                'cover_image_url': 'images/book-05-188x246.jpg',
                'publication_date': date(2024, 4, 1),
                'page_count': 280,
                'rating': Decimal('4.3')
            },
            {
                'id': 6,
                'title': '糟糕客户服务的危险副作用',
                'author': '陈美丽',
                'publisher': '中信出版社',
                'isbn': '9787508567890',
                'category': '商业管理',
                'description': '分析客户服务对企业的重要影响，提供改善客户体验的策略。',
                'original_price': Decimal('26.00'),
                'current_price': Decimal('19.50'),
                'stock_quantity': 40,
                'cover_image_url': 'images/book-06-188x246.jpg',
                'publication_date': date(2024, 4, 15),
                'page_count': 240,
                'rating': Decimal('4.2')
            },
            {
                'id': 7,
                'title': '网页设计师UX评审入门指南',
                'author': '刘大伟',
                'publisher': '电子工业出版社',
                'isbn': '9787121678901',
                'category': '计算机技术',
                'description': 'UX设计评审的完整指南，帮助设计师提升用户体验设计能力。',
                'original_price': Decimal('34.00'),
                'current_price': Decimal('25.50'),
                'stock_quantity': 20,
                'cover_image_url': 'images/book-07-188x246.jpg',
                'publication_date': date(2024, 5, 1),
                'page_count': 360,
                'rating': Decimal('4.6')
            },
            {
                'id': 8,
                'title': '百年孤独',
                'author': '加西亚·马尔克斯',
                'publisher': '南海出版公司',
                'isbn': '9787544789012',
                'category': '文学艺术',
                'description': '魔幻现实主义经典作品，诺贝尔文学奖获奖作品。',
                'original_price': Decimal('42.00'),
                'current_price': Decimal('31.50'),
                'stock_quantity': 60,
                'cover_image_url': 'images/book-08-188x246.jpg',
                'publication_date': date(2024, 1, 20),
                'page_count': 480,
                'rating': Decimal('4.8')
            }
        ]
        
        # 检查是否需要初始化数据
        existing_count = Book.query.count()
        print(f"📊 当前数据库中图书数量: {existing_count}")
        
        if existing_count == 0:
            print("📚 数据库为空，开始插入图书数据...")
            insert_all_books(books_data)
        else:
            print("🔄 检查数据一致性...")
            update_books_if_needed(books_data)
        
        # 验证数据
        final_count = Book.query.count()
        print(f"✅ 图书数据初始化完成，共 {final_count} 本图书")
        
        # 显示所有图书
        books = Book.query.order_by(Book.id).all()
        print("\n📋 当前图书列表:")
        for book in books:
            print(f"  ID: {book.id} - {book.title} ({book.author}) - ¥{book.current_price} - 库存: {book.stock_quantity}")
        
        return True
        
    except Exception as e:
        logger.error(f"图书数据初始化失败: {str(e)}")
        print(f"❌ 图书数据初始化失败: {str(e)}")
        return False

def insert_all_books(books_data):
    """插入所有图书数据"""
    try:
        for book_data in books_data:
            book = Book(**book_data)
            db.session.add(book)
        
        db.session.commit()
        print(f"✅ 成功插入 {len(books_data)} 本图书")
        
    except Exception as e:
        db.session.rollback()
        raise e

def update_books_if_needed(books_data):
    """检查并更新图书数据（如果需要）"""
    try:
        updated_count = 0
        
        for book_data in books_data:
            existing_book = Book.query.filter_by(id=book_data['id']).first()
            
            if existing_book:
                # 检查是否需要更新
                needs_update = False
                for key, value in book_data.items():
                    if key != 'id' and getattr(existing_book, key) != value:
                        needs_update = True
                        setattr(existing_book, key, value)
                
                if needs_update:
                    updated_count += 1
                    print(f"🔄 更新图书: {existing_book.title}")
            else:
                # 插入新图书
                new_book = Book(**book_data)
                db.session.add(new_book)
                updated_count += 1
                print(f"➕ 添加新图书: {book_data['title']}")
        
        if updated_count > 0:
            db.session.commit()
            print(f"✅ 更新了 {updated_count} 本图书的数据")
        else:
            print("✅ 图书数据已是最新，无需更新")
            
    except Exception as e:
        db.session.rollback()
        raise e

def clear_invalid_cart_items():
    """清理无效的购物车项目"""
    try:
        from models import CartItem
        
        # 查找引用不存在图书的购物车项目
        invalid_items = db.session.query(CartItem).filter(
            ~CartItem.book_id.in_(db.session.query(Book.id))
        ).all()
        
        if invalid_items:
            print(f"🗑️ 发现 {len(invalid_items)} 个无效购物车项目，正在清理...")
            for item in invalid_items:
                db.session.delete(item)
            db.session.commit()
            print("✅ 无效购物车项目清理完成")
        else:
            print("✅ 购物车数据正常")
            
    except Exception as e:
        logger.error(f"清理购物车失败: {str(e)}")
        print(f"❌ 清理购物车失败: {str(e)}")

if __name__ == '__main__':
    # 测试数据初始化
    from app import create_app
    
    app = create_app()
    with app.app_context():
        init_book_data()
        clear_invalid_cart_items()
