from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from models import CrawlerTask, db
from datetime import datetime, timedelta

class TaskAPI(Resource):
    @jwt_required()
    def get(self, task_id):
        """获取单个任务详情"""
        task = CrawlerTask.query.get_or_404(task_id)
        return task.to_dict()

class TaskListAPI(Resource):
    @jwt_required()
    def get(self):
        """获取任务列表"""
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = CrawlerTask.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
            
        tasks = query.order_by(CrawlerTask.created_at.desc())\
                    .paginate(page=page, per_page=per_page)
        
        return {
            'items': [task.to_dict() for task in tasks.items],
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': tasks.page
        }

class TaskStatsAPI(Resource):
    @jwt_required()
    def get(self):
        """获取任务统计信息"""
        user_id = get_jwt_identity()
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        
        # 总任务统计
        total_stats = db.session.query(
            CrawlerTask.status,
            db.func.count(CrawlerTask.id)
        ).filter(
            CrawlerTask.user_id == user_id
        ).group_by(CrawlerTask.status).all()
        
        # 最近一周趋势
        weekly_trend = db.session.query(
            db.func.date(CrawlerTask.created_at),
            db.func.count(CrawlerTask.id)
        ).filter(
            CrawlerTask.user_id == user_id,
            CrawlerTask.created_at >= last_week
        ).group_by(
            db.func.date(CrawlerTask.created_at)
        ).all()
        
        return {
            'total_stats': dict(total_stats),
            'weekly_trend': {
                str(date): count 
                for date, count in weekly_trend
            }
        }

class TaskActionAPI(Resource):
    @jwt_required()
    def post(self, task_id, action):
        """任务操作（暂停/恢复/取消）"""
        task = CrawlerTask.query.get_or_404(task_id)
        user_id = get_jwt_identity()
        
        if task.user_id != user_id:
            return {'error': 'Unauthorized'}, 403
            
        if action == 'pause':
            if task.status == 'running':
                task.status = 'paused'
                db.session.commit()
                return {'status': 'paused'}
        elif action == 'resume':
            if task.status == 'paused':
                task.status = 'running'
                db.session.commit()
                return {'status': 'running'}
        elif action == 'cancel':
            if task.status in ['running', 'paused', 'pending']:
                task.status = 'cancelled'
                db.session.commit()
                return {'status': 'cancelled'}
                
        return {'error': 'Invalid action'}, 400

# 注册API路由
api.add_resource(TaskAPI, '/tasks/<string:task_id>')
api.add_resource(TaskListAPI, '/tasks')
api.add_resource(TaskStatsAPI, '/tasks/stats')
api.add_resource(TaskActionAPI, '/tasks/<string:task_id>/<string:action>')