import unittest
import pylibfinder as finder
from pylibfinder.FiniteFault import Coordinate, CoordinateCollection

class TestESMClient(unittest.TestCase):
    def test_Coordinate(self):
        # Test the Coordinate class
        coord = Coordinate(10, 20)
        self.assertEqual(coord.get_lat(), 10)
        self.assertEqual(coord.get_lon(), 20)

        # test the CoordinateCollection class with two simple coordinates.
        # The CoordinateCollection class is a wrapper around a std::vector
        coord1 = Coordinate(10, 20)
        coord2 = Coordinate(30, 40)
        collection = CoordinateCollection()
        collection.push_back(coord1)
        collection.push_back(coord2)

        # Check size of the collection
        self.assertEqual(collection.size(), 2)
        
        for _coord in collection:
            print(_coord.get_lat(), _coord.get_lon())
            # self.assertEqual(_coord.get_lat(), 10)
            # self.assertEqual(_coord.get_lon(), 20)
        
        
