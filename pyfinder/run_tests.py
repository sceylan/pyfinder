#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import logging
from utils import customlogger

if __name__ == '__main__':
    # Initialize the logger for a small report at the end.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    

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
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(verbosity=2)
        suite = loader.discover(grp)
        results.append(runner.run(suite))
    
    # Final report
    logging.getLogger().info("="*23 + " Test results " + "="*23)
        
    for grp, result in zip(test_desc, results):
        error = len(result.errors)
        failure = len(result.failures)
        skipped = len(result.skipped)
        succeeded = result.testsRun - error - failure - skipped
        
        if error > 0 or failure > 0:
            logging.getLogger().error(
                "{:20s}: Total {:2d} tests ({:2d} succeeded, {:2d}"
                " failed, {:2d} error(s), {:2d} skipped)".format(
                    grp, result.testsRun, succeeded, failure, error, skipped))
        elif skipped > 0:
            logging.getLogger().warning(
            "{:20s}: Total {:2d} tests ({:2d} succeeded, {:2d}"
            " failed, {:2d} error(s), {:2d} skipped)".format(
                grp, result.testsRun, succeeded, failure, error, skipped))
        else:
            logging.getLogger().ok(
            "{:20s}: Total {:2d} tests ({:2d} succeeded, {:2d}"
            " failed, {:2d} error(s), {:2d} skipped)".format(
                grp, result.testsRun, succeeded, failure, error, skipped))
    logging.getLogger().info("="*60)
