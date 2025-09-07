import sys
from loguru import logger
import os

# Remove default handler
logger.remove()

# Add custom handler with privacy filtering
def privacy_filter(record):
    """Filter out potential PII from logs"""
    message = record["message"]
    # Redact potential emails, phone numbers, names patterns
    import re
    message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', message)
    message = re.sub(r'\b\d{2}[-.\s]?\d{2}[-.\s]?\d{2}[-.\s]?\d{2}[-.\s]?\d{2}\b', '[PHONE]', message)
    record["message"] = message
    return True

# Configure logger
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.add(
    sys.stderr,
    level=log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    filter=privacy_filter
)

# Export configured logger
__all__ = ["logger"]
