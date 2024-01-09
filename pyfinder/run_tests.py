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
    format = "%(asctime)s  %(levelname)s  %(message)8s"
    
    FORMATS = {logging.INFO: magenta + format + reset}

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

if __name__ == '__main__':
    # Just for printing some messages in color in a proper 
    # logging style.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(LoggingFormatter())
    logger.addHandler(ch)

    # Folders containing the tests.
    test_groups = ['tests/clients']

    # Messages to be displayed before each test group.
    messages = ["Testing web service clients and parsers..."]

    for grp, msg in zip(test_groups, messages):
        # Provide a header
        logging.info(msg)
        
        # Run the tests.
        loader = unittest.TestLoader()
        suite = loader.discover(grp)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    
    logging.info("-"*50)
    logging.info("Tests are completed. Check the status above.")
    logging.info("-"*50)