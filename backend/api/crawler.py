from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from services.task_queue import celery
from models import CrawlerTask, db
from crawler.engine import SmartCrawler
import uuid

class CrawlerAPI(Resource):
    @jwt_required()
    def post(self):
        """创建新的爬虫任务"""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证输入
        if not data or 'urls' not in data:
            return {'error': 'Missing required fields'}, 400
            
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task = CrawlerTask(
            id=task_id,
            user_id=user_id,
            urls=data['urls'],
            depth=data.get('depth', 2),
            status='pending',
            settings=data.get('settings', {})
        )
        db.session.add(task)
        db.session.commit()
        
        # 启动异步任务
        celery.send_task(
            'tasks.crawl_task',
            args=[task_id, data['urls'], data.get('depth', 2)],
            kwargs={'settings': data.get('settings', {})}
        )
        
        return {'task_id': task_id}, 201

class CrawlerConfigAPI(Resource):
    @jwt_required()
    def get(self):
        """获取爬虫配置选项"""
        return {
            'maxDepth': 5,
            'supportedFeatures': [
                'login_detection',
                'smart_extraction',
                'anti_detection'
            ],
            'defaultSettings': {
                'useProxy': True,
                'respectRobots': True,
                'delay': 1.0,
                'maxRetries': 3
            }
        }

class LoginDetectionAPI(Resource):
    @jwt_required()
    def post(self):
        """检测页面是否需要登录"""
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return {'error': 'URL is required'}, 400
            
        crawler = SmartCrawler(None)
        requires_login = crawler.detect_login_requirement(url)
        
        return {
            'url': url,
            'requiresLogin': requires_login,
            'loginFormDetected': requires_login
        }

# 注册API路由
api.add_resource(CrawlerAPI, '/crawler')
api.add_resource(CrawlerConfigAPI, '/crawler/config')
api.add_resource(LoginDetectionAPI, '/crawler/check-login')