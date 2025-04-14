from flask_socketio import SocketIO, emit
import json

socketio = SocketIO(cors_allowed_origins="*")

class ProgressReporter:
    def __init__(self, task_id):
        self.task_id = task_id
    
    def update(self, progress, status, message=""):
        """推送进度更新"""
        socketio.emit('task_progress', {
            'task_id': self.task_id,
            'progress': progress,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=self.task_id)

# 在Flask初始化时附加
def init_app(app):
    socketio.init_app(app)