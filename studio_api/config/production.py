from studio_api.config.base import *

DEBUG = True
RESTRICT_IPS = False

CELERY_BROKER_URL = 'sqs://{}:{}@'.format(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
BROKER_TRANSPORT_OPTIONS = {
    'region': AWS_REGION,
    'polling_interval': 20,
    'visibility_timeout': 3600,  # 1 hour
    'fifo_queues': True,
    'queue_name_prefix': 'prod-',
    'broker_connection_timeout': 30,
}
CELERY_DEFAULT_QUEUE = "sqs"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BROKER_TRANSPORT_OPTIONS = BROKER_TRANSPORT_OPTIONS
CELERY_TASK_DEFAULT_QUEUE = "sqs"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {levelname} {message}',
            'style': '{',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}
