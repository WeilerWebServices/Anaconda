import os
import logging
from logging.config import dictConfig


_log_dict_config = dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            'simple': {'format':
                           '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
                       }
        },
        handlers={
            'console': {'class': 'logging.StreamHandler',
                        'formatter': 'simple',
                        'stream': 'ext://sys.stdout'},
            'file': {'class': 'logging.FileHandler',
                     'formatter': 'simple',
                     'filename': 'airgap.log'}
        },
        root={
            'level': logging.INFO,
            'handlers': ['console', 'file']
        },
    )


def initialize_log(log_level):
    _log_dict_config['root']['level'] = log_level
    dictConfig(_log_dict_config)
