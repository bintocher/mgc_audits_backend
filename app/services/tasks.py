from celery_worker import celery_app


@celery_app.task
def dummy_task():
    pass

