from app.extensions import celery
import app.tasks

if __name__ == '__main__':
    celery.start()
