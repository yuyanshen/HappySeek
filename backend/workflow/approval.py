# backend/workflow/approval.py
from flask import current_app
from .models import db, ApprovalRequest

class ApprovalSystem:
    @staticmethod
    def create_request(user_id, request_type, data):
        """创建审批请求"""
        req = ApprovalRequest(
            user_id=user_id,
            request_type=request_type,
            data=data,
            status='pending'
        )
        db.session.add(req)
        db.session.commit()
        
        # 发送通知给审批人
        current_app.extensions['socketio'].emit(
            'new_approval', 
            {'request_id': req.id},
            room='approvers'
        )
        return req

    @staticmethod
    def process_request(request_id, action, approver_id):
        """处理审批请求"""
        req = ApprovalRequest.query.get(request_id)
        req.status = 'approved' if action else 'rejected'
        req.approver_id = approver_id
        db.session.commit()
        
        # 触发后续动作
        if req.status == 'approved':
            if req.request_type == 'task_create':
                task = CrawlTask(**req.data)
                db.session.add(task)
                db.session.commit()