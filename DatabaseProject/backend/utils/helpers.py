import re
import uuid
from datetime import datetime
from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User

def success_response(data=None, message="操作成功", code=200):
    """统一成功响应格式"""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), code

def error_response(message="操作失败", code=400, error_code=None):
    """统一错误响应格式"""
    response = {
        "success": False,
        "message": message,
        "error_code": error_code
    }
    return jsonify(response), code

def camel_to_snake(name):
    """驼峰命名转下划线命名"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_to_camel(name):
    """下划线命名转驼峰命名"""
    components = name.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])

def convert_keys_to_camel(obj):
    """递归转换字典键名为驼峰命名"""
    if isinstance(obj, dict):
        return {snake_to_camel(k): convert_keys_to_camel(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys_to_camel(item) for item in obj]
    else:
        return obj

def convert_keys_to_snake(obj):
    """递归转换字典键名为下划线命名"""
    if isinstance(obj, dict):
        return {camel_to_snake(k): convert_keys_to_snake(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys_to_snake(item) for item in obj]
    else:
        return obj

def generate_order_number():
    """生成订单号"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"HX{timestamp}{random_str}"

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_file_extension(filename):
    """获取文件扩展名"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def generate_filename(original_filename):
    """生成唯一文件名"""
    ext = get_file_extension(original_filename)
    unique_name = str(uuid.uuid4()).replace('-', '')
    return f"{unique_name}.{ext}" if ext else unique_name

def paginate_query(query, page, per_page):
    """分页查询辅助函数"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total
    }

def jwt_required_custom(f):
    """自定义JWT验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.is_active:
                return error_response("用户不存在或已被禁用", 401, "USER_INACTIVE")
            
            # 将当前用户添加到请求上下文
            request.current_user = current_user
            return f(*args, **kwargs)
            
        except Exception as e:
            return error_response("认证失败", 401, "AUTH_FAILED")
    
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    @jwt_required_custom
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user.is_admin:
            return error_response("需要管理员权限", 403, "ADMIN_REQUIRED")
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json_data(required_fields=None):
    """验证JSON数据装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response("请求必须是JSON格式", 400, "INVALID_JSON")
            
            data = request.get_json()
            if not data:
                return error_response("请求数据不能为空", 400, "EMPTY_DATA")
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return error_response(f"缺少必需字段: {', '.join(missing_fields)}", 400, "MISSING_FIELDS")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def log_api_call(f):
    """API调用日志装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.now()
        
        # 记录请求信息
        current_app.logger.info(f"API调用: {request.method} {request.path}")
        current_app.logger.info(f"请求IP: {request.remote_addr}")
        current_app.logger.info(f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        
        try:
            result = f(*args, **kwargs)
            
            # 记录响应时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            current_app.logger.info(f"API响应时间: {duration:.3f}秒")
            
            return result
            
        except Exception as e:
            # 记录错误
            current_app.logger.error(f"API调用异常: {str(e)}")
            raise
    
    return decorated_function
