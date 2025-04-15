from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# 导入所有API路由
from .auth import *
from .crawler import *
from .task import *
from .check import *

def init_api(app):
    app.register_blueprint(api_bp)