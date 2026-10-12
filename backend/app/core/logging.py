import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Include extra contextual attributes dynamically
        exclude_keys = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename", 
            "funcName", "levelname", "levelno", "lineno", "module", "msecs", 
            "message", "msg", "name", "pathname", "process", "processName", 
            "relativeCreated", "stack_info", "thread", "threadName", "color_message"
        }
        for key, value in record.__dict__.items():
            if key not in exclude_keys:
                log_record[key] = value
                
        return json.dumps(log_record)

def setup_logging():
    """Configure structured JSON logging for the application."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "app"]:
        l = logging.getLogger(logger_name)
        l.handlers = [console_handler]
        l.propagate = False
