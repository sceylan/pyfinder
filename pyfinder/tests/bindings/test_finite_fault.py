import unittest
import pylibfinder as finder
from pylibfinder.FiniteFault import (Coordinate, CoordinateCollection, 
                                     CoordinateList, PGA_Data, Finder_Centroid,
                                     Finder_Rupture, Finder_Rupture_List,
                                     Misfit, Misfit_List,
                                     Finder_Azimuth, Finder_Azimuth_List,)

class TestFinderBindings(unittest.TestCase):
    def test_FinderAzimuth(self):
        # Test the Finder_Azimuth class.
        azimuth = Finder_Azimuth(azimuth=10, misf=0.1)
        self.assertEqual(azimuth.get_value(), 10)
        self.assertEqual(azimuth.get_misf(), 0.1)

        # Test the destructor
        del azimuth

        # Test the azimuth list as well.
        azimuth_list = Finder_Azimuth_List()
        azimuth_list.push_back(Finder_Azimuth(azimuth=10, misf=0.1))
        azimuth_list.push_back(Finder_Azimuth(azimuth=10, misf=0.1))

        # Check size of the collection
        self.assertEqual(azimuth_list.size(), 2)

        # Test iteration over the collection
        for _azimuth in azimuth_list:
            self.assertEqual(_azimuth.get_value(), 10)
            self.assertEqual(_azimuth.get_misf(), 0.1)

        # Call destructor
        del azimuth_list

    def test_Misfit(self):
        misfit = Misfit(misf=0.1, value=1)
        self.assertEqual(misfit.get_misf(), 0.1)
        self.assertEqual(misfit.get_value(), 1)

        # Test the destructor
        del misfit

        # Test the misfit list as well.
        misfit_list = Misfit_List()
        misfit_list.push_back(Misfit(misf=0.1, value=1))
        misfit_list.push_back(Misfit(misf=0.1, value=1))

        # Check size of the collection
        self.assertEqual(misfit_list.size(), 2)

        # Test iteration over the collection
        for _misfit in misfit_list:
            self.assertEqual(_misfit.get_misf(), 0.1)
            self.assertEqual(_misfit.get_value(), 1)

        # Call destructor
        del misfit_list

    def test_Coordinate(self):
        # Test the Coordinate class
        coord = Coordinate(10, 20)
        self.assertEqual(coord.get_lat(), 10)
        self.assertEqual(coord.get_lon(), 20)

        # test the CoordinateCollection class with two simple coordinates.
        # The CoordinateCollection class is a wrapper around a std::vector
        # Use the same coordinate twice to check the push_back method.
        coord1 = Coordinate(10, 20)
        coord2 = Coordinate(10, 20)
        collection = CoordinateCollection()
        collection.push_back(coord1)
        collection.push_back(coord2)

        # Check size of the collection
        self.assertEqual(collection.size(), 2)

        # Test iteration over the collection
        for _coord in collection:
            self.assertEqual(_coord.get_lat(), 10)
            self.assertEqual(_coord.get_lon(), 20)

        # Test access by index
        self.assertEqual(collection[0].get_lat(), 10)
        self.assertEqual(collection[0].get_lon(), 20)
        self.assertEqual(collection[1].get_lat(), 10)
        self.assertEqual(collection[1].get_lon(), 20)

        # Test the clear method
        collection.clear()
        self.assertEqual(collection.size(), 0)
        
        # Test the CoordinateList class. This class is a wrapper around 
        # the CoordinateCollection
        coord_list = CoordinateList()
        coord_list.push_back(coord1)
        coord_list.push_back(coord2)

        # Check size of the collection
        self.assertEqual(coord_list.size(), 2)

        for _coord in coord_list:
            self.assertEqual(_coord.get_lat(), 10)
            self.assertEqual(_coord.get_lon(), 20)

        # Test the destructors
        del coord
        del coord1
        del coord2
        del collection
        del coord_list

    def test_PGAData(self):
        # Test the PGA_Data class
        pga = PGA_Data(name="PGA", network="netw", channel="chn",
                       location_code="01", location=Coordinate(10, 20), 
                       value=0.1)
        
        self.assertEqual(pga.get_name(), "PGA")
        self.assertEqual(pga.get_network(), "netw")
        self.assertEqual(pga.get_channel(), "chn")
        self.assertEqual(pga.get_location_code(), "01")
        self.assertEqual(pga.get_location().get_lat(), 10)
        self.assertEqual(pga.get_location().get_lon(), 20)
        self.assertEqual(pga.get_value(), 0.1)

        # Test the destructor
        del pga

    def test_FinderCentroid(self):
        # Test the Finder_Centroid class. This class is inherits from the
        # Coordinate class.
        centroid = Finder_Centroid(lat=10, lon=20)
        self.assertEqual(centroid.get_lat(), 10)
        self.assertEqual(centroid.get_lon(), 20)

        # Test the destructor
        del centroid

    def test_FinderRupture(self):
        # Test the Finder_Rupture class. 
        rupture = Finder_Rupture(lat=10, lon=20, depth=30)
        self.assertEqual(rupture.get_lat(), 10)
        self.assertEqual(rupture.get_lon(), 20)
        self.assertEqual(rupture.get_depth(), 30)

        # Test the destructor
        del rupture

        # Test the rupure list as well.
        rupture_list = Finder_Rupture_List()
        rupture_list.push_back(Finder_Rupture(lat=10, lon=20, depth=30))
        rupture_list.push_back(Finder_Rupture(lat=10, lon=20, depth=30))

        # Check size of the collection
        self.assertEqual(rupture_list.size(), 2)

        # Test iteration over the collection
        for _rupture in rupture_list:
            self.assertEqual(_rupture.get_lat(), 10)
            self.assertEqual(_rupture.get_lon(), 20)
            self.assertEqual(_rupture.get_depth(), 30)