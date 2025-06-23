from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_, desc, asc
from models import db, Book, BrowsingHistory
from utils.helpers import (
    success_response, error_response, jwt_required_custom,
    paginate_query, log_api_call
)

book_bp = Blueprint('book', __name__)

@book_bp.route('/', methods=['GET'])
@log_api_call
def get_books():
    """获取图书列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category')
    sort_by = request.args.get('sort_by', 'created_at')  # created_at, price, sales_count, rating
    order = request.args.get('order', 'desc')  # asc, desc

    # 构建查询
    query = Book.query.filter_by(is_active=True)

    # 分类筛选
    if category:
        query = query.filter(Book.category == category)

    # 排序
    sort_column = getattr(Book, sort_by, Book.created_at)
    if order == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # 分页
    result = paginate_query(query, page, per_page)

    return success_response({
        'books': [book.to_dict() for book in result['items']],
        'pagination': {
            'page': result['page'],
            'perPage': result['per_page'],
            'total': result['total'],
            'totalPages': result['pages'],
            'hasPrev': result['has_prev'],
            'hasNext': result['has_next']
        }
    })

@book_bp.route('/<int:book_id>', methods=['GET'])
@log_api_call
def get_book_detail(book_id):
    """获取图书详情"""
    book = Book.query.filter_by(id=book_id, is_active=True).first()

    if not book:
        return error_response("图书不存在", 404, "BOOK_NOT_FOUND")

    try:
        # 增加浏览次数
        book.view_count += 1
        db.session.commit()

        return success_response(book.to_dict())

    except Exception as e:
        db.session.rollback()
        return success_response(book.to_dict())  # 即使更新浏览次数失败也返回图书信息

@book_bp.route('/search', methods=['GET'])
@log_api_call
def search_books():
    """搜索图书"""
    q = request.args.get('q', '').strip()
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

    # 构建查询
    query = Book.query.filter_by(is_active=True)

    # 关键词搜索
    if q:
        search_filter = or_(
            Book.title.contains(q),
            Book.author.contains(q),
            Book.publisher.contains(q),
            Book.description.contains(q)
        )
        query = query.filter(search_filter)

    # 分类筛选
    if category:
        query = query.filter(Book.category == category)

    # 价格筛选
    if min_price is not None:
        query = query.filter(Book.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Book.current_price <= max_price)

    # 排序
    sort_column = getattr(Book, sort_by, Book.created_at)
    if order == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # 分页
    result = paginate_query(query, page, per_page)

    return success_response({
        'books': [book.to_dict() for book in result['items']],
        'pagination': {
            'page': result['page'],
            'perPage': result['per_page'],
            'total': result['total'],
            'totalPages': result['pages'],
            'hasPrev': result['has_prev'],
            'hasNext': result['has_next']
        },
        'searchQuery': q,
        'filters': {
            'category': category,
            'minPrice': min_price,
            'maxPrice': max_price
        }
    })

@book_bp.route('/categories', methods=['GET'])
@log_api_call
def get_categories():
    """获取图书分类列表"""
    try:
        # 获取所有有效图书的分类
        categories = db.session.query(Book.category)\
            .filter(Book.is_active == True, Book.category.isnot(None))\
            .distinct().all()

        category_list = [category[0] for category in categories if category[0]]

        # 获取每个分类的图书数量
        category_counts = []
        for category in category_list:
            count = Book.query.filter_by(category=category, is_active=True).count()
            category_counts.append({
                'name': category,
                'count': count
            })

        # 按图书数量排序
        category_counts.sort(key=lambda x: x['count'], reverse=True)

        return success_response(category_counts)

    except Exception as e:
        return error_response("获取分类失败", 500, "CATEGORIES_FETCH_FAILED")

@book_bp.route('/recommended', methods=['GET'])
@log_api_call
def get_recommended_books():
    """获取推荐图书"""
    limit = request.args.get('limit', 8, type=int)

    try:
        # 简单的推荐算法：按销量和评分排序
        recommended_books = Book.query.filter_by(is_active=True)\
            .order_by(desc(Book.sales_count), desc(Book.rating))\
            .limit(limit).all()

        return success_response([book.to_dict() for book in recommended_books])

    except Exception as e:
        return error_response("获取推荐失败", 500, "RECOMMENDATIONS_FETCH_FAILED")

@book_bp.route('/hot', methods=['GET'])
@log_api_call
def get_hot_books():
    """获取热门图书"""
    limit = request.args.get('limit', 10, type=int)

    try:
        # 热门图书：按浏览量和销量排序
        hot_books = Book.query.filter_by(is_active=True)\
            .order_by(desc(Book.view_count), desc(Book.sales_count))\
            .limit(limit).all()

        return success_response([book.to_dict() for book in hot_books])

    except Exception as e:
        return error_response("获取热门图书失败", 500, "HOT_BOOKS_FETCH_FAILED")

@book_bp.route('/new', methods=['GET'])
@log_api_call
def get_new_books():
    """获取新书"""
    limit = request.args.get('limit', 10, type=int)

    try:
        # 新书：按创建时间排序
        new_books = Book.query.filter_by(is_active=True)\
            .order_by(desc(Book.created_at))\
            .limit(limit).all()

        return success_response([book.to_dict() for book in new_books])

    except Exception as e:
        return error_response("获取新书失败", 500, "NEW_BOOKS_FETCH_FAILED")

@book_bp.route('/personalized', methods=['GET'])
@jwt_required_custom
@log_api_call
def get_personalized_recommendations():
    """获取个性化推荐"""
    user = request.current_user
    limit = request.args.get('limit', 10, type=int)

    try:
        # 基于用户浏览历史的简单推荐算法
        # 1. 获取用户浏览过的图书分类
        browsed_categories = db.session.query(Book.category)\
            .join(BrowsingHistory, Book.id == BrowsingHistory.book_id)\
            .filter(BrowsingHistory.user_id == user.id)\
            .distinct().all()

        if not browsed_categories:
            # 如果没有浏览历史，返回热门图书
            return get_hot_books()

        category_list = [cat[0] for cat in browsed_categories if cat[0]]

        # 2. 推荐相同分类的高评分图书
        recommended_books = Book.query.filter(
            Book.is_active == True,
            Book.category.in_(category_list)
        ).order_by(desc(Book.rating), desc(Book.sales_count))\
         .limit(limit).all()

        return success_response([book.to_dict() for book in recommended_books])

    except Exception as e:
        return error_response("获取个性化推荐失败", 500, "PERSONALIZED_RECOMMENDATIONS_FAILED")