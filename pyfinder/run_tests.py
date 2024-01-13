#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import logging

class LoggingFormatter(logging.Formatter):
    """ 
    Colors logging entries by their level. The code is taken from
    https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """
    yellow = "\x1b[33;20m"
    bold_gray_bg = "\x1b[0;100m"
    reset = "\x1b[0m"
    format = "%(message)8s"
    
    FORMATS = {
        logging.INFO: yellow + format + reset,
        logging.WARNING: bold_gray_bg + format + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

if __name__ == '__main__':
    # Just for printing some messages in color in a 
    # proper logging style.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(LoggingFormatter())
    logger.addHandler(ch)

    # Folders containing the tests.
    test_groups = ['tests/parsers', 
                   'tests/services',
                   'tests/clients',
                   'tests/cpp_library']

    # Messages to be displayed before each test group.
    test_desc = ['Parsers', 
                 'Web service clients', 
                 'Client encapsulation', 
                 'C++ library loader']

    # Collect the results of the tests.
    results = []
    for grp, msg in zip(test_groups, test_desc):
        # Provide a header
        logging.info("\n" + msg)
        
        # Run the tests.
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(verbosity=2)
        suite = loader.discover(grp)
        results.append(runner.run(suite))
    
    # Final report
    logging.info("="*23 + " Test results " + "="*23)
        
    for grp, result in zip(test_desc, results):
        error = len(result.errors)
        failure = len(result.failures)
        skipped = len(result.skipped)
        succeeded = result.testsRun - error - failure - skipped
        
        logging.warning(
            "{:20s}: Total {:2d} tests ({:2d} succeeded, {:2d}"
            " failed, {:2d} error(s), {:2d} skipped)".format(
                grp, result.testsRun, succeeded, failure, error, skipped))
    logging.info("="*60)
