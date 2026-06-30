from celery_app import celery_app




@celery_app.task(name="tasks.poll_and_evaluate")
def poll_and_evaulate():
    print("poll_and_evaluate called")
    return "ok"