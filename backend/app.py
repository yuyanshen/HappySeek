# backend/app.py
from flask import Flask, request, jsonify
from celery import Celery
import redis
import uuid

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

# Celery配置
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# 任务状态存储
redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)

@app.route('/api/crawl', methods=['POST'])
def start_crawl():
    data = request.json
    task_id = str(uuid.uuid4())
    
    # 存储初始状态
    redis_client.hset(task_id, mapping={
        'status': 'pending',
        'progress': '0',
        'urls': ','.join(data['urls']),
        'depth': str(data['depth'])
    })
    
    # 启动异步任务
    crawl_task.delay(task_id, data['urls'], data['depth'])
    
    return jsonify({'task_id': task_id})

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task_data = redis_client.hgetall(task_id)
    if not task_data:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({
        'status': task_data.get(b'status', b'').decode(),
        'progress': int(task_data.get(b'progress', b'0')),
        'result_count': int(task_data.get(b'result_count', b'0'))
    })

@celery.task(bind=True)
def crawl_task(self, task_id, urls, depth):
    from .crawler import AdvancedCrawler
    crawler = AdvancedCrawler(task_id)
    
    # 更新任务状态
    redis_client.hset(task_id, 'status', 'running')
    
    try:
        # 执行爬取（伪代码）
        result_count = asyncio.run(crawler.run(urls, depth))
        redis_client.hset(task_id, mapping={
            'status': 'completed',
            'progress': '100',
            'result_count': str(result_count)
        })
    except Exception as e:
        redis_client.hset(task_id, 'status', 'failed')
        raise self.retry(exc=e)