# -*-coding: utf-8 -*-
import os
import sys

module_path = os.path.abspath(__file__)
one_up = os.path.join(module_path, '..')
one_up = os.path.abspath(one_up)
sys.path.append(one_up)
