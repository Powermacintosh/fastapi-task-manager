import logging
import json
import time
import socket

class ServiceNameFilter(logging.Filter):
    def __init__(self, service_name):
        super().__init__()
        self.service_name = service_name

    def filter(self, record):
        record.service = self.service_name
        return True


class CustomJsonFormatter(logging.Formatter):
    def format(self, record):
        # Если service не установлен фильтром, используем значение по умолчанию
        if not hasattr(record, 'service'):
            service_name = 'unknown'
        else:
            service_name = record.service
            
        log_record = {
            "timestamp": int(time.time() * 1000),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
            "thread": record.thread,
            "function": record.funcName,
            "file": record.filename,
            "line": record.lineno,
            "host": socket.gethostname(),
            "service": service_name,
            # "environment": os.getenv('ENVIRONMENT', 'development')
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, 'tags') and isinstance(record.tags, dict):
            log_record.update(record.tags)
        return json.dumps(log_record, ensure_ascii=False)


logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'core.logger.CustomJsonFormatter',
        },
    },
    'filters': {
        'crud': {
            '()': 'core.logger.ServiceNameFilter',
            'service_name': 'crud'
        },
        'uvicorn': {
            '()': 'core.logger.ServiceNameFilter',
            'service_name': 'uvicorn'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'crud_logger': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
            'filters': ['crud'],
        },
        'uvicorn': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
            'filters': ['uvicorn'],
        },
        'uvicorn.error': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
            'filters': ['uvicorn'],
        },
        'uvicorn.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
            'filters': ['uvicorn'],
        },
    },
}