from functools import wraps
import time
from flask import request, g
import logging
from prometheus_client import Histogram, Counter
import threading
import psutil
import os

logger = logging.getLogger(__name__)

# 性能指标定义
REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

REQUEST_COUNT = Counter(
    'request_count_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

MEMORY_USAGE = Histogram(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['type']
)

CPU_USAGE = Histogram(
    'cpu_usage_percent',
    'CPU usage percentage',
    ['type']
)

class PerformanceMiddleware:
    def __init__(self, app):
        self.app = app
        self.process = psutil.Process(os.getpid())
        self._start_resource_monitoring()

    def _start_resource_monitoring(self):
        """启动资源监控线程"""
        def monitor_resources():
            while True:
                try:
                    # 监控内存使用
                    memory = self.process.memory_info()
                    MEMORY_USAGE.labels('rss').observe(memory.rss)
                    MEMORY_USAGE.labels('vms').observe(memory.vms)

                    # 监控CPU使用
                    cpu_percent = self.process.cpu_percent(interval=1)
                    CPU_USAGE.labels('process').observe(cpu_percent)

                    time.sleep(5)  # 每5秒采集一次
                except Exception as e:
                    logger.error(f"Resource monitoring error: {e}")

        thread = threading.Thread(target=monitor_resources, daemon=True)
        thread.start()

    def __call__(self, environ, start_response):
        # 请求开始时间
        request_start = time.time()

        def _start_response(status, headers, *args):
            # 请求结束时计算耗时
            request_duration = time.time() - request_start

            # 记录请求延迟
            REQUEST_LATENCY.labels(
                method=environ.get('REQUEST_METHOD', ''),
                endpoint=environ.get('PATH_INFO', '')
            ).observe(request_duration)

            # 记录请求计数
            REQUEST_COUNT.labels(
                method=environ.get('REQUEST_METHOD', ''),
                endpoint=environ.get('PATH_INFO', ''),
                status=status.split()[0]
            ).inc()

            # 记录慢请求
            if request_duration > 1.0:  # 超过1秒的请求
                logger.warning(
                    f"Slow request detected: {environ.get('PATH_INFO')} "
                    f"took {request_duration:.2f}s"
                )

            return start_response(status, headers, *args)

        return self.app(environ, _start_response)

def track_performance(name=None):
    """用于跟踪函数性能的装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            func_name = name or f.__name__
            start_time = time.time()

            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time

                # 记录函数执行时间
                Histogram(
                    'function_duration_seconds',
                    'Function execution time in seconds',
                    ['function']
                ).labels(func_name).observe(duration)

                # 记录慢函数
                if duration > 0.5:  # 超过0.5秒的函数调用
                    logger.warning(
                        f"Slow function detected: {func_name} "
                        f"took {duration:.2f}s"
                    )

                return result
            except Exception as e:
                # 记录函数错误
                Counter(
                    'function_errors_total',
                    'Total function errors',
                    ['function', 'error_type']
                ).labels(func_name, type(e).__name__).inc()
                raise

        return wrapped
    return decorator

def init_performance_monitoring(app):
    """初始化性能监控"""
    app.wsgi_app = PerformanceMiddleware(app.wsgi_app)

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.cpu_percent = psutil.cpu_percent()
        g.memory_start = psutil.Process().memory_info().rss

    @app.after_request
    def after_request(response):
        # 计算请求处理时间
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = str(duration)

        # 计算内存使用变化
        if hasattr(g, 'memory_start'):
            memory_end = psutil.Process().memory_info().rss
            memory_diff = memory_end - g.memory_start
            if memory_diff > 1024 * 1024:  # 如果内存增加超过1MB
                logger.warning(
                    f"High memory usage in request: {request.path} "
                    f"increased by {memory_diff / 1024 / 1024:.2f}MB"
                )

        return response

    return app