from loguru import logger
import sys
import json
from typing import Dict, Any

class CustomJSONFormatter:
    def __call__(self, record: Dict[str, Any]) -> str:
        """
        Formats the record into structured JSON for better log aggregation
        """
        log_record = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        
        if "extra" in record:
            log_record.update(record["extra"])
        
        if record["exception"]:
            log_record["exception"] = record["exception"]
            
        return json.dumps(log_record)

def setup_logging():
    """
    Configures application-wide logging
    """
    # Remove default logger
    logger.remove()
    
    # Add JSON formatter for console output
    logger.add(
        sys.stdout,
        format=CustomJSONFormatter(),
        level="INFO",
        serialize=True
    )
    
    # Add file handler for error logs
    logger.add(
        "logs/error.log",
        format=CustomJSONFormatter(),
        level="ERROR",
        rotation="500 MB",
        retention="10 days",
        compression="zip"
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        format=CustomJSONFormatter(),
        level="INFO",
        rotation="1 GB",
        retention="30 days",
        compression="zip"
    )
    
    return logger
