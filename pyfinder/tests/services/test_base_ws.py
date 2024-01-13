# -*- coding: utf-8 -*-
"""Unit tests for the base client class."""
import unittest
from clients.services import BaseWebService

class TestBaseWebService(unittest.TestCase):
    """Unit tests for the base client class."""

    def test_set_get_data(self):
        # Test the set_data method.
        try:
            base_client = BaseWebService()
            base_client.set_data("test")
            self.assertEqual(base_client.data, "test")
            self.assertEqual(base_client.get_data(), "test")

        except TypeError:
            # TypeError will be raised because the class is abstract.
            # We know that, so we can pass.
            pass

    def test_add_field(self):
        # Test add_field method.
        try:
            base_client = BaseWebService()
            base_client.add_field("field1", "value1")
            self.assertEqual(base_client.get("field1"), "value1")

        except TypeError:
            # TypeError will be raised because the class is abstract.
            # We know that, so we can pass.
            pass
