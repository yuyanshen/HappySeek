from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # 加载配置
    app.config.from_object('config.Config')

    # 初始化扩展
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    # 注册蓝图
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    # 健康检查端点
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}, 200

    return app