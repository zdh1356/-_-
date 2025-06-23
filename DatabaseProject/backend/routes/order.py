from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal
from models import db, Order, OrderItem, Book, ShoppingCart
from utils.helpers import (
    success_response, error_response, jwt_required_custom,
    validate_json_data, paginate_query, generate_order_number, log_api_call
)
from services.email_service import email_service

order_bp = Blueprint('order', __name__)

@order_bp.route('/', methods=['POST'])
@jwt_required_custom
@validate_json_data(['items'])
@log_api_call
def create_order():
    """创建订单"""
    user = request.current_user
    data = request.get_json()

    items = data['items']  # [{'bookId': 1, 'quantity': 2}, ...]

    if not items:
        return error_response("订单商品不能为空", 400, "EMPTY_ORDER_ITEMS")

    try:
        # 验证商品库存和计算总价
        total_amount = Decimal('0.00')
        order_items_data = []

        for item in items:
            book = Book.query.filter_by(id=item['bookId'], is_active=True).first()
            if not book:
                return error_response(f"图书ID {item['bookId']} 不存在", 400, "BOOK_NOT_FOUND")

            quantity = item['quantity']
            if quantity <= 0:
                return error_response("商品数量必须大于0", 400, "INVALID_QUANTITY")

            if book.stock_quantity < quantity:
                return error_response(f"图书《{book.title}》库存不足", 400, "INSUFFICIENT_STOCK")

            unit_price = book.current_price
            total_price = unit_price * quantity
            total_amount += total_price

            order_items_data.append({
                'book': book,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            })

        # 创建订单 - 邮件发送模式
        order = Order(
            user_id=user.id,
            order_number=generate_order_number(),
            total_amount=total_amount,
            shipping_address='邮件发送',  # 标记为邮件发送
            shipping_phone=user.phone or '无',
            shipping_name=user.username,
            notes=data.get('notes', '订单将通过邮件发送到用户邮箱'),
            payment_method=data.get('paymentMethod', 'alipay'),
            delivery_method=data.get('deliveryMethod', 'email')
        )

        db.session.add(order)
        db.session.flush()  # 获取订单ID

        # 创建订单项并更新库存
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                book_id=item_data['book'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(order_item)

            # 减少库存
            old_stock = item_data['book'].stock_quantity
            item_data['book'].stock_quantity -= item_data['quantity']
            item_data['book'].sales_count += item_data['quantity']  # 增加销量

            print(f"📦 库存扣减 - 图书《{item_data['book'].title}》: {old_stock} → {item_data['book'].stock_quantity} (扣减{item_data['quantity']}本)")

        # 清空购物车中的相关商品
        book_ids = [item['bookId'] for item in items]
        ShoppingCart.query.filter(
            ShoppingCart.user_id == user.id,
            ShoppingCart.book_id.in_(book_ids)
        ).delete(synchronize_session=False)

        db.session.commit()

        # 发送订单确认邮件
        email_sent = False  # 初始化邮件发送状态
        try:
            print(f"📧 开始发送订单确认邮件到: {user.email}")

            # 准备邮件数据 - 邮件发送模式
            order_data = {
                'order_number': order.order_number,
                'total_amount': float(order.total_amount),
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'user_name': user.username,
                'user_email': user.email,
                'payment_method': order.payment_method or 'alipay',
                'delivery_method': '邮件发送',
                'items': []
            }

            # 添加订单商品信息
            for item_data in order_items_data:
                order_data['items'].append({
                    'title': item_data['book'].title,
                    'author': item_data['book'].author,
                    'publisher': item_data['book'].publisher,
                    'isbn': item_data['book'].isbn,
                    'quantity': item_data['quantity'],
                    'unit_price': float(item_data['unit_price']),
                    'total_price': float(item_data['total_price'])
                })

            print(f"📦 邮件数据准备完成，包含 {len(order_data['items'])} 个商品")

            # 发送邮件
            email_sent = email_service.send_order_confirmation(
                user.email,
                user.username,
                order_data
            )

            if email_sent:
                print(f"✅ 订单确认邮件已发送到: {user.email}")
            else:
                print(f"⚠️ 订单确认邮件发送失败: {user.email}")

        except Exception as e:
            print(f"❌ 发送订单确认邮件时出错: {e}")
            import traceback
            print(f"📋 错误详情: {traceback.format_exc()}")
            # 邮件发送失败不影响订单创建
            email_sent = False

        # 返回订单信息，包含邮件发送状态
        order_dict = order.to_dict()
        order_dict['emailSent'] = email_sent
        order_dict['deliveryMethod'] = 'email'

        message = "订单创建成功，详情已发送到您的邮箱" if email_sent else "订单创建成功，邮件发送失败，请联系客服"
        return success_response(order_dict, message)

    except Exception as e:
        db.session.rollback()
        return error_response("订单创建失败", 500, "ORDER_CREATE_FAILED")

@order_bp.route('/', methods=['GET'])
@jwt_required_custom
@log_api_call
def get_orders():
    """获取用户订单列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')

    # 构建查询
    query = Order.query.filter_by(user_id=user.id)

    if status:
        query = query.filter(Order.status == status)

    query = query.order_by(Order.created_at.desc())

    # 分页
    result = paginate_query(query, page, per_page)

    return success_response({
        'orders': [order.to_dict() for order in result['items']],
        'pagination': {
            'page': result['page'],
            'perPage': result['per_page'],
            'total': result['total'],
            'totalPages': result['pages'],
            'hasPrev': result['has_prev'],
            'hasNext': result['has_next']
        }
    })

@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required_custom
@log_api_call
def get_order_detail(order_id):
    """获取订单详情"""
    user = request.current_user
    order = Order.query.filter_by(id=order_id, user_id=user.id).first()

    if not order:
        return error_response("订单不存在", 404, "ORDER_NOT_FOUND")

    return success_response(order.to_dict())

@order_bp.route('/<int:order_id>/pay', methods=['PUT'])
@jwt_required_custom
@validate_json_data(['paymentMethod'])
@log_api_call
def pay_order(order_id):
    """支付订单"""
    user = request.current_user
    data = request.get_json()

    order = Order.query.filter_by(id=order_id, user_id=user.id).first()

    if not order:
        return error_response("订单不存在", 404, "ORDER_NOT_FOUND")

    if order.status != 'pending':
        return error_response("订单状态不允许支付", 400, "INVALID_ORDER_STATUS")

    try:
        # 更新订单状态
        order.status = 'paid'
        order.payment_status = 'paid'
        order.payment_method = data['paymentMethod']
        order.paid_at = datetime.utcnow()

        # 更新图书销量
        for item in order.order_items:
            item.book.sales_count += item.quantity

        db.session.commit()

        return success_response(order.to_dict(), "支付成功")

    except Exception as e:
        db.session.rollback()
        return error_response("支付失败", 500, "PAYMENT_FAILED")

@order_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required_custom
@log_api_call
def cancel_order(order_id):
    """取消订单"""
    user = request.current_user
    order = Order.query.filter_by(id=order_id, user_id=user.id).first()

    if not order:
        return error_response("订单不存在", 404, "ORDER_NOT_FOUND")

    if order.status not in ['pending', 'paid']:
        return error_response("订单状态不允许取消", 400, "INVALID_ORDER_STATUS")

    try:
        # 恢复库存
        for item in order.order_items:
            item.book.stock_quantity += item.quantity
            # 如果订单已支付，需要恢复销量
            if order.status == 'paid':
                item.book.sales_count -= item.quantity

        # 更新订单状态
        order.status = 'cancelled'

        db.session.commit()

        return success_response(order.to_dict(), "订单已取消")

    except Exception as e:
        db.session.rollback()
        return error_response("取消订单失败", 500, "ORDER_CANCEL_FAILED")

# 购物车相关路由
@order_bp.route('/cart', methods=['GET'])
@jwt_required_custom
@log_api_call
def get_cart():
    """获取购物车"""
    user = request.current_user

    cart_items = ShoppingCart.query.filter_by(user_id=user.id)\
        .join(Book).filter(Book.is_active == True).all()

    total_amount = sum(item.book.current_price * item.quantity for item in cart_items)

    return success_response({
        'items': [item.to_dict() for item in cart_items],
        'totalAmount': float(total_amount),
        'itemCount': len(cart_items)
    })

@order_bp.route('/cart/add', methods=['POST'])
@jwt_required_custom
@validate_json_data(['bookId', 'quantity'])
@log_api_call
def add_to_cart():
    """添加到购物车"""
    user = request.current_user
    data = request.get_json()

    book_id = data['bookId']
    quantity = data['quantity']

    if quantity <= 0:
        return error_response("数量必须大于0", 400, "INVALID_QUANTITY")

    # 检查图书是否存在
    book = Book.query.filter_by(id=book_id, is_active=True).first()
    if not book:
        return error_response("图书不存在", 404, "BOOK_NOT_FOUND")

    if book.stock_quantity < quantity:
        return error_response("库存不足", 400, "INSUFFICIENT_STOCK")

    try:
        # 检查购物车中是否已存在该商品
        existing_item = ShoppingCart.query.filter_by(
            user_id=user.id,
            book_id=book_id
        ).first()

        if existing_item:
            # 更新数量
            new_quantity = existing_item.quantity + quantity
            if book.stock_quantity < new_quantity:
                return error_response("库存不足", 400, "INSUFFICIENT_STOCK")

            existing_item.quantity = new_quantity
            existing_item.updated_at = datetime.utcnow()
        else:
            # 添加新商品
            cart_item = ShoppingCart(
                user_id=user.id,
                book_id=book_id,
                quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()

        return success_response(None, "已添加到购物车")

    except Exception as e:
        db.session.rollback()
        return error_response("添加失败", 500, "CART_ADD_FAILED")

@order_bp.route('/cart/update', methods=['PUT'])
@jwt_required_custom
@validate_json_data(['itemId', 'quantity'])
@log_api_call
def update_cart_item():
    """更新购物车商品数量"""
    user = request.current_user
    data = request.get_json()

    item_id = data['itemId']
    quantity = data['quantity']

    if quantity <= 0:
        return error_response("数量必须大于0", 400, "INVALID_QUANTITY")

    cart_item = ShoppingCart.query.filter_by(
        id=item_id,
        user_id=user.id
    ).first()

    if not cart_item:
        return error_response("购物车商品不存在", 404, "CART_ITEM_NOT_FOUND")

    if cart_item.book.stock_quantity < quantity:
        return error_response("库存不足", 400, "INSUFFICIENT_STOCK")

    try:
        cart_item.quantity = quantity
        cart_item.updated_at = datetime.utcnow()

        db.session.commit()

        return success_response(cart_item.to_dict(), "购物车已更新")

    except Exception as e:
        db.session.rollback()
        return error_response("更新失败", 500, "CART_UPDATE_FAILED")

@order_bp.route('/cart/remove', methods=['DELETE'])
@jwt_required_custom
@log_api_call
def remove_from_cart():
    """从购物车移除商品"""
    user = request.current_user
    item_id = request.args.get('itemId', type=int)

    if not item_id:
        return error_response("缺少商品ID", 400, "MISSING_ITEM_ID")

    cart_item = ShoppingCart.query.filter_by(
        id=item_id,
        user_id=user.id
    ).first()

    if not cart_item:
        return error_response("购物车商品不存在", 404, "CART_ITEM_NOT_FOUND")

    try:
        db.session.delete(cart_item)
        db.session.commit()

        return success_response(None, "商品已移除")

    except Exception as e:
        db.session.rollback()
        return error_response("移除失败", 500, "CART_REMOVE_FAILED")

@order_bp.route('/cart/clear', methods=['DELETE'])
@jwt_required_custom
@log_api_call
def clear_cart():
    """清空购物车"""
    user = request.current_user

    try:
        ShoppingCart.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        return success_response(None, "购物车已清空")

    except Exception as e:
        db.session.rollback()
        return error_response("清空失败", 500, "CART_CLEAR_FAILED")