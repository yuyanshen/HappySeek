import pyotp
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from ..models import User, LoginLog
from .. import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': '用户名或密码错误'}), 401
        
    if user.is_2fa_enabled:
        return jsonify({
            'require_2fa': True,
            'user_id': user.id
        }), 200
    
    access_token = create_access_token(identity=user.id)
    log_login(user.id, request.remote_addr)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    user = User.query.get(data.get('user_id'))
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
        
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(data.get('code')):
        return jsonify({'message': '验证码无效'}), 401
    
    access_token = create_access_token(identity=user.id)
    log_login(user.id, request.remote_addr)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/setup-2fa', methods=['POST'])
@jwt_required()
def setup_2fa():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    qr_code = totp.provisioning_uri(
        user.email,
        issuer_name="HappySeek"
    )
    
    user.totp_secret = secret
    db.session.commit()
    
    return jsonify({
        'secret': secret,
        'qr_code': qr_code
    })

@auth_bp.route('/enable-2fa', methods=['POST'])
@jwt_required()
def enable_2fa():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(data.get('code')):
        return jsonify({'message': '验证码无效'}), 401
    
    user.is_2fa_enabled = True
    db.session.commit()
    
    return jsonify({'message': '2FA已启用'})

def log_login(user_id, ip_address):
    """记录登录日志"""
    log = LoginLog(user_id=user_id, ip_address=ip_address)
    db.session.add(log)
    db.session.commit()