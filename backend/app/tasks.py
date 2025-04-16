from app.celery_app import celery

@celery.task
def test_task():
    return "Task completed successfully"