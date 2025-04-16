from celery import Celery

def create_celery_app(app=None):
    celery = Celery(
        'happyseek',
        include=['app.tasks']
    )

    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery

celery = create_celery_app()