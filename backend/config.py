import os
from datetime import timedelta

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET', 'jwt_dev_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.environ.get('DB_USER', 'crawler')}:{os.environ.get('DB_PASSWORD', 'password')}@{os.environ.get('DB_HOST', 'localhost')}/crawler"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis配置
    REDIS_URL = f"redis://:{os.environ.get('REDIS_PASSWORD', 'password')}@{os.environ.get('REDIS_HOST', 'localhost')}:6379/0"

    # Elasticsearch配置
    ELASTICSEARCH_URL = f"http://elastic:{os.environ.get('ES_PASSWORD', 'password')}@{os.environ.get('ES_HOST', 'localhost')}:9200"

    # Celery配置
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True
    CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
    CELERY_WORKER_PREFETCH_MULTIPLIER = 4
    CELERY_WORKER_CONCURRENCY = 4