# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
import redis
import uuid
import os
from services.websocket import socketio, init_app as init_socketio

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load configuration from environment variables
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', 6379)

# Celery configuration
app.config.update(
    CELERY_BROKER_URL=os.environ.get('CELERY_BROKER_URL', f'redis://{redis_host}:{redis_port}/0'),
    CELERY_RESULT_BACKEND=os.environ.get('CELERY_RESULT_BACKEND', f'redis://{redis_host}:{redis_port}/0')
)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Initialize WebSocket
init_socketio(app)

# Task status storage
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=1)

@app.route('/api/crawl', methods=['POST'])
def start_crawl():
    data = request.json
    task_id = str(uuid.uuid4())
    
    # Store initial status
    redis_client.hset(task_id, mapping={
        'status': 'pending',
        'progress': '0',
        'urls': ','.join(data['urls']),
        'depth': str(data['depth'])
    })
    
    # Start async task
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

@app.route('/api/check/url', methods=['POST'])
def check_url():
    from urllib.parse import urlparse
    import requests
    
    url = request.json.get('url')
    try:
        # Quick HEAD request check
        resp = requests.head(
            url, 
            timeout=3,
            headers={'User-Agent': 'Mozilla/5.0'},
            allow_redirects=True
        )
        return jsonify({'status': 'success', 'code': resp.status_code})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@celery.task(bind=True)
def crawl_task(self, task_id, urls, depth):
    import asyncio
    from services.websocket import ProgressReporter
    reporter = ProgressReporter(task_id)
    
    # Update task status
    redis_client.hset(task_id, 'status', 'running')
    reporter.update(10, 'running', 'Task started')
    
    try:
        # Mock crawler implementation (replace with actual implementation)
        result_count = 0
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            progress = int((i / total_urls) * 80) + 10
            reporter.update(progress, 'running', f'Processing URL: {url}')
            # Simulate work
            import time
            time.sleep(2)
            result_count += 5
        
        # Update final status
        redis_client.hset(task_id, mapping={
            'status': 'completed',
            'progress': '100',
            'result_count': str(result_count)
        })
        reporter.update(100, 'completed', 'Task completed successfully')
        
        return result_count
    except Exception as e:
        redis_client.hset(task_id, 'status', 'failed')
        reporter.update(0, 'failed', str(e))
        raise self.retry(exc=e)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)