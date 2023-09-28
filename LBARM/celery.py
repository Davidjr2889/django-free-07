import os
import socket

from django.core.mail import mail_admins

from celery import Celery
from celery.signals import task_failure


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LBARM.settings')

app = Celery('LBARM')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@task_failure.connect()
def celery_task_failure_email(**kwargs):
    """ celery 4.0 onward has no method to send emails on failed tasks
        so this event handler is intended to replace it
    """
    subject = "[Django][{queue_name}@{host}] Error: Task {sender.name} ({task_id}): {exception}".format(
        queue_name='celery',  # `sender.queue` doesn't exist in 4.1?
        host=socket.gethostname(),
        **kwargs
    )
    message = u"""Task {sender.name} with id {task_id} raised exception:
{exception!r}

Task was called with args: {args} kwargs: {kwargs}.
The contents of the full traceback was:
{einfo}
    """.format(
        **kwargs
    )
    mail_admins(subject, message)
