from __future__ import absolute_import
from celery import Celery


MAIN_NAME = 'celery_demo'
app = Celery(
    MAIN_NAME,
    backend='rpc://',  # 'redis://localhost',
    # broker='amqp://kfs:kfs@kfs.pydemia.org/rabbitmq/amqp',
    # broker='amqp://kfs:kfs@kfs.pydemia.org:5672/rabbitmq/amqp/',
    broker='amqp://kfs:kfs@kfs.pydemia.org:5672',
    include=[f'{MAIN_NAME}.tasks'],
)
