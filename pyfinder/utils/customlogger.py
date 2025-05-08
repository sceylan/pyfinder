# -*- coding: utf-8 -*-
import logging
import logging.handlers

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

# This is not log level. I use this for the finder logs
FINDER_LOG_LEVEL = logging.INFO + 6

# Define new log levels in the logging module
logging.addLevelName(OK_LOG_LEVEL, "OK")
logging.addLevelName(FINDER_LOG_LEVEL, "FinDer")


class LoggingFormatter(logging.Formatter):
    """ Formatter for the console logging with colors."""
    log_time = "%(asctime)-s "
    log_level = "%(levelname)-8s "
    log_message = "%(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: log_time + magenta + log_level + reset + log_message,
        logging.INFO: log_time + grey + log_level + reset + log_message,
        logging.WARNING: log_time + yellow + log_level + reset + log_message,
        logging.ERROR: log_time + red + log_level + reset + log_message,
        logging.CRITICAL: log_time + bold_red + log_level + reset + log_message,
        OK_LOG_LEVEL: log_time + green + log_level + reset + log_message,
        FINDER_LOG_LEVEL: log_time + green + log_level + reset + log_message
        }
        
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class FileLoggingFormatter(logging.Formatter):
    """ Formatter for the file logging without colors."""
    log_time = "%(asctime)-s "
    log_level = "%(levelname)-8s "
    log_message = "%(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: log_time + log_level + log_message,
        logging.INFO: log_time + log_level + log_message,
        logging.WARNING: log_time + log_level + log_message,
        logging.ERROR: log_time + log_level + log_message,
        logging.CRITICAL: log_time + log_level + log_message,
        OK_LOG_LEVEL: log_time + log_level + log_message,
        FINDER_LOG_LEVEL: log_time + log_level + log_message
        }
        
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def console_logger():
    # Define a new log level method in the logger object
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
            
    # Define a custom logging method 'ok' and 'OK'
    def ok(message, *args, **kwargs):
        if logger.isEnabledFor(OK_LOG_LEVEL):
            logger._log(OK_LOG_LEVEL, message, args, **kwargs)

    def OK(message, *args, **kwargs):
        if logger.isEnabledFor(OK_LOG_LEVEL):
            logger._log(OK_LOG_LEVEL, message, args, **kwargs)

    def finder(message, *args, **kwargs):
        if logger.isEnabledFor(FINDER_LOG_LEVEL):
            logger._log(FINDER_LOG_LEVEL, message, args, **kwargs)

    def FINDER(message, *args, **kwargs):
        if logger.isEnabledFor(FINDER_LOG_LEVEL):
            logger._log(FINDER_LOG_LEVEL, message, args, **kwargs)

    # Attach the custom method to the logger
    logger.ok = ok
    logger.OK = OK
    logger.finder = finder
    logger.FINDER = FINDER
    
    logging.ok = ok
    logging.OK = OK
    logging.finder = finder
    logging.FINDER = FINDER

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

    return logger

def file_logger(log_file, module_name=None, overwrite=False, rotate=False, level=logging.DEBUG):
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    
        # Define a custom logging method 'ok' and 'OK'
    def ok(message, *args, **kwargs):
        if logger.isEnabledFor(OK_LOG_LEVEL):
            logger._log(OK_LOG_LEVEL, message, args, **kwargs)

    def OK(message, *args, **kwargs):
        if logger.isEnabledFor(OK_LOG_LEVEL):
            logger._log(OK_LOG_LEVEL, message, args, **kwargs)

    def finder(message, *args, **kwargs):
        if logger.isEnabledFor(FINDER_LOG_LEVEL):
            logger._log(FINDER_LOG_LEVEL, message, args, **kwargs)

    def FINDER(message, *args, **kwargs):
        if logger.isEnabledFor(FINDER_LOG_LEVEL):
            logger._log(FINDER_LOG_LEVEL, message, args, **kwargs)

    # Attach the custom method to the logger
    logger.ok = ok
    logger.OK = OK
    logger.finder = finder
    logger.FINDER = FINDER
    
    logging.ok = ok
    logging.OK = OK
    logging.finder = finder
    logging.FINDER = FINDER

    # Create file handler and set level to debug
    mode = "w+" if overwrite else "a"
    if rotate:
        try:
            fh = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=1000000, backupCount=7, 
                encoding='utf-8', mode=mode)
        except Exception as e:
            fh = logging.FileHandler(log_file, mode=mode, encoding='utf-8')
    else:
        fh = logging.FileHandler(log_file, mode=mode, encoding='utf-8')

    fh.setLevel(logging.NOTSET)
    
    # Create the formatter
    formatter = FileLoggingFormatter()
    fh.setFormatter(formatter)
    
    # Add fh to logger, but prevent duplicate handlers
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == fh.baseFilename
           for h in logger.handlers):
        logger.addHandler(fh)

    return logger


if __name__ == "__main__":
    # Test the logger
    console_logger()
    
    logging.info("info message")
    logging.getLogger().debug("debug message")
    logging.ok("OK message")
    logging.getLogger().ok("ok message")
    logging.warning("warning message")
    logging.error("error message")
    logging.critical("critical message")