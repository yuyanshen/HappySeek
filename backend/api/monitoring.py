from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required
from prometheus_client import generate_latest
import psutil
import time
from datetime import datetime, timedelta
from middleware.performance import REQUEST_LATENCY, REQUEST_COUNT, MEMORY_USAGE, CPU_USAGE
from utils.log_analyzer import get_analyzer
import os

bp = Blueprint('monitoring', __name__)

# 初始化日志分析器
log_analyzer = get_analyzer(os.path.join(os.path.dirname(__file__), '../logs/app.log'))

@bp.route('/metrics')
@jwt_required()
def metrics():
    """返回 Prometheus 格式的监控指标"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4'}

@bp.route('/stats')
@jwt_required()
def system_stats():
    """返回系统状态统计信息"""
    process = psutil.Process()

    # 计算平均响应时间
    response_times = [
        sample[1] for sample in REQUEST_LATENCY._samples()
        if time.time() - sample[2] < 3600  # 最近1小时
    ]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    # 计算错误率
    total_requests = sum(s[1] for s in REQUEST_COUNT._samples())
    error_requests = sum(
        s[1] for s in REQUEST_COUNT._samples()
        if s[0].labels.get('status', '').startswith('5')
    )
    error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0

    stats = {
        'system': {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        },
        'process': {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'threads': len(process.threads()),
            'open_files': len(process.open_files()),
            'connections': len(process.connections())
        },
        'application': {
            'avg_response_time': round(avg_response_time * 1000, 2),  # 转换为毫秒
            'requests_per_second': total_requests / 3600,  # 最近1小时的平均值
            'error_rate': round(error_rate, 2),
            'version': current_app.config.get('VERSION', '1.0.0')
        }
    }

    # 添加日志分析结果
    log_analysis = log_analyzer.analyze_logs(hours=1)
    stats['logs'] = {
        'error_count': log_analysis['error_count'],
        'warning_count': log_analysis['warning_count'],
        'critical_count': log_analysis['critical_count'],
        'errors_by_type': dict(log_analysis['errors_by_type']),
        'recent_exceptions': log_analysis['recent_exceptions'][:5]
    }

    return jsonify(stats)

@bp.route('/errors')
@jwt_required()
def error_stats():
    """返回错误统计信息"""
    one_hour_ago = time.time() - 3600

    # 获取错误请求数据
    error_data = []
    for sample in REQUEST_COUNT._samples():
        if sample[0].labels.get('status', '').startswith(('4', '5')):
            timestamp = sample[2]
            if timestamp >= one_hour_ago:
                error_data.append({
                    'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                    'endpoint': sample[0].labels.get('endpoint'),
                    'method': sample[0].labels.get('method'),
                    'status': sample[0].labels.get('status'),
                    'count': sample[1]
                })

    # 添加日志分析的错误信息
    log_analysis = log_analyzer.analyze_logs(hours=24)
    error_data.extend([{
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'count': count,
        'type': 'log_error'
    } for endpoint, count in log_analysis['errors_by_endpoint'].items()])

    return jsonify(error_data)

@bp.route('/performance')
@jwt_required()
def performance_stats():
    """返回性能统计信息"""
    # 获取最近1小时的响应时间数据点
    one_hour_ago = time.time() - 3600

    response_time_data = []
    request_rate_data = []

    # 收集响应时间数据
    for sample in REQUEST_LATENCY._samples():
        timestamp = sample[2]
        if timestamp >= one_hour_ago:
            response_time_data.append({
                'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                'value': sample[1] * 1000,  # 转换为毫秒
                'endpoint': sample[0].labels.get('endpoint'),
                'method': sample[0].labels.get('method')
            })

    # 按分钟统计请求率
    now = datetime.now()
    minutes = {}
    for sample in REQUEST_COUNT._samples():
        timestamp = datetime.fromtimestamp(sample[2])
        if timestamp >= now - timedelta(hours=1):
            minute_key = timestamp.replace(second=0).isoformat()
            minutes[minute_key] = minutes.get(minute_key, 0) + sample[1]

    for minute, count in minutes.items():
        request_rate_data.append({
            'timestamp': minute,
            'value': count
        })

    # 收集资源使用数据
    resource_data = {
        'cpu': [s[1] for s in CPU_USAGE._samples()],
        'memory': [s[1] for s in MEMORY_USAGE._samples()]
    }

    # 添加日志分析的性能指标
    log_metrics = log_analyzer.get_performance_metrics(hours=24)
    performance_data = {
        'response_times': response_time_data,
        'request_rates': request_rate_data,
        'resources': resource_data,
        'log_analysis': {
            'avg_response_time': log_metrics.get('avg_response_time', 0),
            'max_response_time': log_metrics.get('max_response_time', 0),
            'slow_endpoints': log_metrics.get('slow_endpoints', {}),
            'request_rates': log_metrics.get('request_rates', {}),
            'error_rates': log_metrics.get('error_rates', {})
        }
    }

    return jsonify(performance_data)

@bp.route('/logs/analysis')
@jwt_required()
def log_analysis():
    """返回详细的日志分析结果"""
    hours = request.args.get('hours', default=24, type=int)
    analysis = log_analyzer.analyze_logs(hours=hours)
    return jsonify(analysis)

@bp.route('/logs/trends')
@jwt_required()
def log_trends():
    """返回日志趋势分析"""
    days = request.args.get('days', default=7, type=int)
    trends = log_analyzer.get_error_trends(days=days)
    return jsonify(trends)

@bp.route('/logs/export')
@jwt_required()
def export_log_analysis():
    """导出日志分析报告"""
    try:
        output_path = os.path.join(
            os.path.dirname(__file__),
            '../reports',
            f'log_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        log_analyzer.export_report(output_path)

        return jsonify({
            'status': 'success',
            'message': '报告导出成功',
            'path': output_path
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/health/detailed')
@jwt_required()
def detailed_health():
    """返回详细的健康检查信息"""
    checks = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': current_app.config.get('VERSION', '1.0.0'),
        'components': {}
    }

    # 检查数据库连接
    try:
        from models import db
        db.session.execute('SELECT 1')
        checks['components']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        checks['components']['database'] = {
            'status': 'unhealthy',
            'message': str(e)
        }
        checks['status'] = 'unhealthy'

    # 检查Redis连接
    try:
        current_app.redis.ping()
        checks['components']['redis'] = {
            'status': 'healthy',
            'message': 'Redis connection successful'
        }
    except Exception as e:
        checks['components']['redis'] = {
            'status': 'unhealthy',
            'message': str(e)
        }
        checks['status'] = 'unhealthy'

    # 检查系统资源
    system_resources = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }

    # 添加资源警告
    checks['components']['system'] = {
        'status': 'healthy',
        'metrics': system_resources
    }

    if system_resources['cpu_percent'] > 80:
        checks['components']['system']['status'] = 'warning'
        checks['components']['system']['message'] = 'High CPU usage'

    if system_resources['memory_percent'] > 80:
        checks['components']['system']['status'] = 'warning'
        checks['components']['system']['message'] = 'High memory usage'

    if system_resources['disk_percent'] > 80:
        checks['components']['system']['status'] = 'warning'
        checks['components']['system']['message'] = 'High disk usage'

    # 添加日志健康检查
    try:
        log_analysis = log_analyzer.analyze_logs(hours=1)
        checks['components']['logs'] = {
            'status': 'healthy',
            'metrics': {
                'error_count': log_analysis['error_count'],
                'critical_count': log_analysis['critical_count']
            }
        }

        # 如果最近有严重错误，标记为警告
        if log_analysis['critical_count'] > 0:
            checks['components']['logs']['status'] = 'warning'
            checks['components']['logs']['message'] = f"发现 {log_analysis['critical_count']} 个严重错误"

    except Exception as e:
        checks['components']['logs'] = {
            'status': 'unhealthy',
            'message': str(e)
        }

    return jsonify(checks)

def init_app(app):
    """初始化监控模块"""
    # 确保日志目录存在
    log_dir = os.path.join(os.path.dirname(__file__), '../logs')
    os.makedirs(log_dir, exist_ok=True)

    app.register_blueprint(bp, url_prefix='/api/monitoring')