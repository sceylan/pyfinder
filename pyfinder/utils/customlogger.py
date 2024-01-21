# -*- coding: utf-8 -*-
import logging

# Colors for the different log levels
grey = "\x1b[38;20m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
bold_red = "\x1b[31;1m"
magenta = "\033[95m"
green = "\033[92m" 
reset = "\x1b[0m"

# Define a new log level (OK) that is higher than INFO
# but lower than WARNING.
OK_LOG_LEVEL = logging.INFO + 5 


class LoggingFormatter(logging.Formatter):
    log_time = "%(asctime)-s "
    log_level = "%(levelname)-8s "
    log_message = "%(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: log_time + magenta + log_level + reset + log_message,
        logging.INFO: log_time + grey + log_level + reset + log_message,
        logging.WARNING: log_time + yellow + log_level + reset + log_message,
        logging.ERROR: log_time + red + log_level + reset + log_message,
        logging.CRITICAL: log_time + bold_red + log_level + reset + log_message,
        OK_LOG_LEVEL: log_time + green + log_level + reset + log_message
        }
        
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
    
# Define a new log level name and value in the logging module
logging.addLevelName(OK_LOG_LEVEL, "OK")
# logging.OK = OK_LOG_LEVEL

# Define a new log level method in the logger object
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
        
# Create console handler and set level to debug
ch = logging.StreamHandler()

# Handle all log levels
ch.setLevel(logging.NOTSET)
        
# Create formatter
formatter = LoggingFormatter()
        
# Add formatter to ch
ch.setFormatter(formatter)
        
# Add ch to logger
logger.addHandler(ch)

# Define a custom logging method 'ok' and 'OK'
def ok(message, *args, **kwargs):
    if logger.isEnabledFor(OK_LOG_LEVEL):
        logger._log(OK_LOG_LEVEL, message, args, **kwargs)

def OK(message, *args, **kwargs):
    if logger.isEnabledFor(OK_LOG_LEVEL):
        logger._log(OK_LOG_LEVEL, message, args, **kwargs)

# Attach the custom method to the logger
logger.ok = ok
logger.OK = OK
logging.ok = ok
logging.OK = OK

if __name__ == "__main__":
    # Test the logger
    logging.info("info message")
    logging.getLogger().debug("debug message")
    logging.ok("OK message")
    logging.getLogger().ok("ok message")
    logging.warning("warning message")
    logging.error("error message")
    logging.critical("critical message")