from prometheus_flask_exporter import PrometheusMetrics
from flask import request
import time
import functools
import logging
from logging.config import fileConfig
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
import os

# 初始化日志
fileConfig('logging.conf')
logger = logging.getLogger(__name__)

def init_monitoring(app):
    # 初始化Prometheus监控
    metrics = PrometheusMetrics(app)

    # 请求计数器
    request_counter = metrics.counter(
        'happyseek_requests_total',
        'Total number of requests by endpoint and method',
        labels={'endpoint': lambda: request.endpoint, 'method': lambda: request.method}
    )

    # 响应时间直方图
    request_latency = metrics.histogram(
        'happyseek_request_latency_seconds',
        'Request latency in seconds',
        labels={'endpoint': lambda: request.endpoint}
    )

    # SQL查询计数器
    db_query_counter = metrics.counter(
        'happyseek_db_queries_total',
        'Total number of database queries'
    )

    # 爬虫任务监控
    crawler_tasks = metrics.gauge(
        'happyseek_crawler_tasks',
        'Number of crawler tasks by status',
        labels={'status': lambda: request.args.get('status', 'unknown')}
    )

    # 性能监控装饰器
    def monitor_performance(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                endpoint = request.endpoint or 'unknown'
                logger.info(f'Request to {endpoint} took {duration:.2f} seconds')
                request_latency.labels(endpoint=endpoint).observe(duration)
        return wrapper

    # 初始化Sentry错误追踪
    if os.getenv('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[
                FlaskIntegration(),
                CeleryIntegration()
            ],
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            environment=os.getenv('FLASK_ENV', 'production'),
            send_default_pii=False,
            before_send=lambda event, hint: event if os.getenv('FLASK_ENV') == 'production' else None
        )

    # 注册通用指标
    @app.before_request
    def before_request():
        request._start_time = time.time()
        request_counter.labels(
            endpoint=request.endpoint,
            method=request.method
        ).inc()

    @app.after_request
    def after_request(response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            request_latency.labels(
                endpoint=request.endpoint
            ).observe(duration)
        return response

    # 监控API端点
    @app.route('/metrics')
    @metrics.do_not_track()
    def metrics():
        return metrics.generate_latest()

    @app.route('/health')
    @metrics.do_not_track()
    def health():
        # 基础健康检查
        checks = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': os.getenv('APP_VERSION', '1.0.0')
        }
        return checks

    return metrics, monitor_performance