import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler

def create_app(config_name=None):
    app = Flask(__name__)

    # 配置
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    if config_name == 'development':
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config import Config
        app.config.from_object(Config)

    # 初始化扩展
    from models import db
    db.init_app(app)

    # 初始化邮件服务
    from services.email_service import email_service
    email_service.init_app(app)

    # CORS配置 - 允许所有来源（开发环境）
    CORS(app,
         origins=['*'],  # 开发环境允许所有来源
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)

    # JWT配置
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': '令牌已过期',
            'error_code': 'TOKEN_EXPIRED'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': '无效的令牌',
            'error_code': 'INVALID_TOKEN'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': '需要认证令牌',
            'error_code': 'TOKEN_REQUIRED'
        }), 401

    # 注册蓝图
    from routes.user import user_bp
    from routes.book import book_bp
    from routes.order import order_bp

    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(book_bp, url_prefix='/api/book')
    app.register_blueprint(order_bp, url_prefix='/api/order')

    # 健康检查端点
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'success': True,
            'message': '服务运行正常',
            'version': '1.0.0'
        })

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '接口不存在',
            'error_code': 'NOT_FOUND'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error_code': 'INTERNAL_ERROR'
        }), 500

    # 日志配置
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/bookstore.log',
                                         maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('华轩书店后端启动')

    # 创建数据库表并初始化数据
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('数据库表创建成功')

            # 初始化图书数据
            from services.data_init_service import init_book_data, clear_invalid_cart_items
            init_book_data()
            clear_invalid_cart_items()
            app.logger.info('图书数据初始化完成')

        except Exception as e:
            app.logger.error(f'数据库初始化失败: {str(e)}')

    return app

if __name__ == '__main__':
    print("🚀 华轩书店后端服务启动中...")
    print("=" * 50)

    # 检查环境
    env = os.environ.get('FLASK_ENV', 'development')
    print(f"📊 运行环境: {env}")

    # 创建应用
    app = create_app(env)

    # 启动配置
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = env == 'development'

    print(f"🌐 服务地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"📚 API文档: http://{host}:{port}/api/health")
    print("=" * 50)
    print("✅ 服务启动成功！按 Ctrl+C 停止服务")

    try:
        # 启动服务
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {str(e)}")
        import sys
        sys.exit(1)
