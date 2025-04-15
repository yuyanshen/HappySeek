# backend/app.py
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from celery import Celery
from dotenv import load_dotenv
import os
import redis
from models import db, init_db
from api import init_api
from services.websocket import socketio, init_app as init_socketio
from middleware.performance import init_performance_monitoring
from monitoring import init_monitoring
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging.config

# 加载环境变量和日志配置
load_dotenv()
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # 初始化性能监控
    init_performance_monitoring(app)

    # 初始化Sentry错误追踪
    if os.getenv('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=os.getenv('FLASK_ENV', 'production')
        )

    # 安全配置
    Talisman(app,
        force_https=True,
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy={
            'default-src': "'self'",
            'img-src': '*',
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"]
        }
    )

    # CORS配置
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # 速率限制
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=os.getenv('REDIS_URL', "redis://redis:6379/0"),
        strategy="fixed-window-elastic-expiry"
    )

    # 全局限制
    limiter.limit("200/minute")(app)

    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@mysql/crawler')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Redis配置
    app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    app.redis = redis.from_url(
        app.config['REDIS_URL'],
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )

    # JWT配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

    # Celery配置
    app.config.update(
        CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
        CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TIMEZONE='Asia/Shanghai',
        CELERY_ENABLE_UTC=True,
        CELERY_WORKER_MAX_TASKS_PER_CHILD=1000,
        CELERY_WORKER_PREFETCH_MULTIPLIER=4,
        CELERY_TASK_ACKS_LATE=True
    )

    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)
    init_socketio(app)
    init_api(app)
    metrics = init_monitoring(app)

    # 创建数据库表
    with app.app_context():
        init_db()

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 error: {request.url}")
        return {'error': 'Not found', 'code': 'NOT_FOUND'}, 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"500 error: {error}")
        return {'error': 'Internal server error', 'code': 'SERVER_ERROR'}, 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        logger.warning(f"Rate limit exceeded for {request.remote_addr}")
        return {'error': 'Rate limit exceeded', 'code': 'RATE_LIMIT_EXCEEDED'}, 429

    # 健康检查
    @app.route('/health')
    @limiter.exempt
    def health_check():
        app.logger.debug("Health check request received")
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            # 检查Redis连接
            app.redis.ping()

            checks = {
                'status': 'healthy',
                'version': os.getenv('APP_VERSION', '1.0.0'),
                'database': 'connected',
                'redis': 'connected'
            }
            return checks, 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }, 503

    return app

def create_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f'Task {task_id} failed: {exc}')
            super().on_failure(exc, task_id, args, kwargs, einfo)

    celery.Task = ContextTask
    return celery

app = create_app()
celery = create_celery(app)

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development',
        use_reloader=os.getenv('FLASK_ENV') == 'development'
    )