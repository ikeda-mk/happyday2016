__author__ = 'mak'

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'basic': {
            'format': '%(asctime)-6s %(levelname)-5s [%(filename)s:%(lineno)d] %(name)s - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'basic'
            }
    },
    'loggers': {
        'sqlalchemy.*': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}
