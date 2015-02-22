from celery import Celery
import django
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'
django.setup()

# The command for controlling Celery workers.
CELERY_COMMAND = 'celery'

app = Celery('testproject', backend='amqp')

# Modules that we don't include in INSTALLED_APPS, but contain Celery tasks.
app.conf.CELERY_IMPORTS = (
    'tests',
)
