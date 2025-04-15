from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 带审计功能的基类
class AuditMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(db.Model, AuditMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    totp_secret = db.Column(db.String(32))  # 存储2FA密钥
    last_login = db.Column(db.DateTime)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    role = db.Column(db.String(20), default='user')
    
    # 关系
    roles = db.relationship('Role', secondary='user_roles')
    login_logs = db.relationship('LoginLog', backref='user')
    operations = db.relationship('OperationLog', backref='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_2fa_enabled': self.is_2fa_enabled,
            'department_id': self.department_id,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }

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

def init_db():
    db.create_all()
    
    # 创建默认管理员账户
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()