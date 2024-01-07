#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('unittests')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
