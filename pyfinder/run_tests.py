#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import logging

class LoggingFormatter(logging.Formatter):
    """ 
    Colors logging entries by their level. The code is taken from
    https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """
    magenta = "\033[95m"
    reset = "\x1b[0m"
    format = "%(asctime)s  %(levelname)-8s  %(message)8s"
    
    FORMATS = {logging.INFO: magenta + format + reset}

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

if __name__ == '__main__':
    loader = unittest.TestLoader()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(LoggingFormatter())
    logger.addHandler(ch)

    logging.newline = True
    logging.getLogger().info("-"*40)
    logging.getLogger().info("Running tests for clients and parsers...")
    logging.getLogger().info("-"*40)
    suite = loader.discover('tests/clients')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
