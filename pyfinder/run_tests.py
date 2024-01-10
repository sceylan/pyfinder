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
    format = "%(asctime)s  %(message)8s"
    
    FORMATS = {logging.INFO: magenta + format + reset}

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def load_tests_from_folders(*folders):
    loader = unittest.TestLoader()
    

    for folder in folders:
        suite.addTests(loader.discover(folder, pattern='test*.py'))

    return suite

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
                   'tests/clients']

    # Messages to be displayed before each test group.
    messages = ["Testing parsers ...", 
                "Testing web service clients ..."]

    # Collect the results of the tests.
    results = []
    for grp, msg in zip(test_groups, messages):
        # Provide a header
        logging.info(msg)
        
        # Run the tests.
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(verbosity=2)
        suite = loader.discover(grp)
        results.append(runner.run(suite))
    
    # Final report
    logging.info("="*50)
    logging.info("Test Results:")
    for grp, result in zip(test_groups, results):
        error = len(result.errors)
        failure = len(result.failures)
        skipped = len(result.skipped)
        succeeded = result.testsRun - error - failure - skipped
        logging.info(
            f"{grp}: {result.testsRun} tests run ({succeeded} succeeded, {failure} failed, {error} with error, {skipped} skipped)")
    logging.info("="*50)