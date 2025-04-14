from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON

db = SQLAlchemy()

# 带审计功能的基类
class AuditMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(db.Model, AuditMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(256))  # 支持更安全的哈希
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    
    # 关系
    roles = db.relationship('Role', secondary='user_roles')
    login_logs = db.relationship('LoginLog', backref='user')
    operations = db.relationship('OperationLog', backref='user')

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    children = db.relationship("Department")

class CrawlTask(db.Model, AuditMixin):
    __tablename__ = 'crawl_tasks'
    id = db.Column(db.String(36), primary_key=True)
    config = db.Column(JSON)  # 包含爬取策略、代理设置等
    result_stats = db.Column(JSON)  # 存储统计信息
    schedule = db.Column(db.String(50))  # 支持定时任务
    
    # 新增字段
    is_approved = db.Column(db.Boolean, default=False)  # 审批流程
    priority = db.Column(db.Integer, default=1)  # 任务优先级