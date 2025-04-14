from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def permission_required(permission, logical='AND'):
    """支持权限组合检查 (AND/OR)"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            if not isinstance(permission, list):
                required_perms = [permission]
            else:
                required_perms = permission
                
            user_perms = claims.get('permissions', [])
            
            # 权限逻辑判断
            if logical == 'AND':
                satisfied = all(p in user_perms for p in required_perms)
            else:  # OR
                satisfied = any(p in user_perms for p in required_perms)
                
            if not satisfied:
                return jsonify({
                    "error": "forbidden",
                    "required": required_perms,
                    "possessed": user_perms
                }), 403
                
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 数据权限过滤
def data_scope_filter(model, alias='id'):
    """根据部门数据权限过滤查询"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            query = f(*args, **kwargs)
            
            # 管理员跳过过滤
            if 'admin' in claims.get('roles', []):
                return query
                
            # 添加部门过滤条件
            if 'dept_ids' in claims:
                return query.filter(
                    getattr(model, 'department_id').in_(claims['dept_ids'])
                    
            return query
        return wrapper
    return decorator