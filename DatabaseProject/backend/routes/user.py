from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import bcrypt
import json

from models import db, User, UserPreferences, BrowsingHistory
from utils.helpers import (
    success_response, error_response, jwt_required_custom,
    validate_json_data, validate_email, validate_phone, log_api_call
)

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
@validate_json_data(['username', 'email', 'password'])
@log_api_call
def register():
    """用户注册"""
    data = request.get_json()

    # 验证数据格式
    if not validate_email(data['email']):
        return error_response("邮箱格式不正确", 400, "INVALID_EMAIL")

    if len(data['password']) < 6:
        return error_response("密码长度至少6位", 400, "PASSWORD_TOO_SHORT")

    if len(data['username']) < 3:
        return error_response("用户名长度至少3位", 400, "USERNAME_TOO_SHORT")

    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return error_response("用户名已存在", 400, "USERNAME_EXISTS")

    if User.query.filter_by(email=data['email']).first():
        return error_response("邮箱已被注册", 400, "EMAIL_EXISTS")

    try:
        # 创建用户
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash,
            phone=data.get('phone'),
            real_name=data.get('realName'),
            gender=data.get('gender')
        )

        db.session.add(user)
        db.session.flush()  # 获取用户ID

        # 创建用户偏好设置
        preferences = UserPreferences(user_id=user.id)
        db.session.add(preferences)

        db.session.commit()

        # 生成访问令牌
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return success_response({
            'token': access_token,
            'refreshToken': refresh_token,
            'user': user.to_dict()
        }, "注册成功")

    except Exception as e:
        db.session.rollback()
        return error_response("注册失败", 500, "REGISTRATION_FAILED")

@user_bp.route('/login', methods=['POST'])
@validate_json_data(['email', 'password'])
@log_api_call
def login():
    """用户登录"""
    data = request.get_json()

    # 查找用户（支持邮箱或用户名登录）
    user = User.query.filter(
        (User.email == data['email']) | (User.username == data['email'])
    ).first()

    if not user:
        return error_response("用户不存在", 401, "USER_NOT_FOUND")

    if not user.is_active:
        return error_response("账户已被禁用", 401, "ACCOUNT_DISABLED")

    # 验证密码
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return error_response("密码错误", 401, "INVALID_PASSWORD")

    try:
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()

        # 生成访问令牌
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return success_response({
            'token': access_token,
            'refreshToken': refresh_token,
            'user': user.to_dict()
        }, "登录成功")

    except Exception as e:
        db.session.rollback()
        return error_response("登录失败", 500, "LOGIN_FAILED")

@user_bp.route('/profile', methods=['GET'])
@jwt_required_custom
@log_api_call
def get_profile():
    """获取用户资料"""
    user = request.current_user
    return success_response(user.to_dict())

@user_bp.route('/profile', methods=['PUT'])
@jwt_required_custom
@log_api_call
def update_profile():
    """更新用户资料"""
    user = request.current_user
    data = request.get_json()

    try:
        # 更新允许修改的字段
        if 'realName' in data:
            user.real_name = data['realName']
        if 'phone' in data:
            if data['phone'] and not validate_phone(data['phone']):
                return error_response("手机号格式不正确", 400, "INVALID_PHONE")
            user.phone = data['phone']
        if 'gender' in data:
            user.gender = data['gender']
        if 'birthDate' in data:
            if data['birthDate']:
                user.birth_date = datetime.fromisoformat(data['birthDate']).date()
        if 'address' in data:
            user.address = data['address']

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(user.to_dict(), "资料更新成功")

    except Exception as e:
        db.session.rollback()
        return error_response("更新失败", 500, "UPDATE_FAILED")

@user_bp.route('/change-password', methods=['POST'])
@jwt_required_custom
@validate_json_data(['currentPassword', 'newPassword'])
@log_api_call
def change_password():
    """修改密码"""
    user = request.current_user
    data = request.get_json()

    # 验证当前密码
    if not bcrypt.checkpw(data['currentPassword'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return error_response("当前密码错误", 400, "INVALID_CURRENT_PASSWORD")

    # 验证新密码
    if len(data['newPassword']) < 6:
        return error_response("新密码长度至少6位", 400, "PASSWORD_TOO_SHORT")

    try:
        # 更新密码
        new_password_hash = bcrypt.hashpw(data['newPassword'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = new_password_hash
        user.updated_at = datetime.utcnow()

        db.session.commit()

        return success_response(None, "密码修改成功")

    except Exception as e:
        db.session.rollback()
        return error_response("密码修改失败", 500, "PASSWORD_CHANGE_FAILED")

@user_bp.route('/preferences', methods=['GET'])
@jwt_required_custom
@log_api_call
def get_preferences():
    """获取用户偏好设置"""
    user = request.current_user
    preferences = UserPreferences.query.filter_by(user_id=user.id).first()

    if not preferences:
        # 创建默认偏好设置
        preferences = UserPreferences(user_id=user.id)
        db.session.add(preferences)
        db.session.commit()

    return success_response(preferences.to_dict())

@user_bp.route('/preferences', methods=['PUT'])
@jwt_required_custom
@log_api_call
def update_preferences():
    """更新用户偏好设置"""
    user = request.current_user
    data = request.get_json()

    preferences = UserPreferences.query.filter_by(user_id=user.id).first()
    if not preferences:
        preferences = UserPreferences(user_id=user.id)
        db.session.add(preferences)

    try:
        # 更新偏好设置
        if 'preferredCategories' in data:
            preferences.preferred_categories = json.dumps(data['preferredCategories'])
        if 'emailNotifications' in data:
            preferences.email_notifications = data['emailNotifications']
        if 'smsNotifications' in data:
            preferences.sms_notifications = data['smsNotifications']
        if 'language' in data:
            preferences.language = data['language']
        if 'theme' in data:
            preferences.theme = data['theme']

        preferences.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(preferences.to_dict(), "偏好设置更新成功")

    except Exception as e:
        db.session.rollback()
        return error_response("更新失败", 500, "PREFERENCES_UPDATE_FAILED")

@user_bp.route('/browsing-history', methods=['GET'])
@jwt_required_custom
@log_api_call
def get_browsing_history():
    """获取浏览历史"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    history_query = BrowsingHistory.query.filter_by(user_id=user.id)\
        .order_by(BrowsingHistory.viewed_at.desc())

    from utils.helpers import paginate_query
    result = paginate_query(history_query, page, per_page)

    return success_response({
        'history': [item.to_dict() for item in result['items']],
        'pagination': {
            'page': result['page'],
            'perPage': result['per_page'],
            'total': result['total'],
            'totalPages': result['pages'],
            'hasPrev': result['has_prev'],
            'hasNext': result['has_next']
        }
    })

@user_bp.route('/browsing-history', methods=['POST'])
@jwt_required_custom
@validate_json_data(['bookId'])
@log_api_call
def add_browsing_history():
    """添加浏览历史"""
    user = request.current_user
    data = request.get_json()

    try:
        # 检查是否已存在相同的浏览记录
        existing = BrowsingHistory.query.filter_by(
            user_id=user.id,
            book_id=data['bookId']
        ).first()

        if existing:
            # 更新浏览时间
            existing.viewed_at = datetime.utcnow()
        else:
            # 创建新的浏览记录
            history = BrowsingHistory(
                user_id=user.id,
                book_id=data['bookId']
            )
            db.session.add(history)

        db.session.commit()

        return success_response(None, "浏览历史已记录")

    except Exception as e:
        db.session.rollback()
        return error_response("记录失败", 500, "HISTORY_ADD_FAILED")

@user_bp.route('/browsing-history', methods=['DELETE'])
@jwt_required_custom
@log_api_call
def clear_browsing_history():
    """清空浏览历史"""
    user = request.current_user

    try:
        BrowsingHistory.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        return success_response(None, "浏览历史已清空")

    except Exception as e:
        db.session.rollback()
        return error_response("清空失败", 500, "HISTORY_CLEAR_FAILED")
