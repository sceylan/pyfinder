import unittest
from pylibfinder.FiniteFault import (Coordinate, Coordinate_List, 
                                     PGA_Data, PGA_Data_List, Finder_Centroid,
                                     Finder_Rupture, Finder_Rupture_List,
                                     Misfit, Misfit_List,
                                     Finder_Azimuth, Finder_Azimuth_List,
                                     Finder_Length, Finder_Length_List,
                                     LogLikelihood, LogLikelihood_List,)

class TestFinderBindings(unittest.TestCase):
    def test_LogLikelihood(self):
        # Test the LogLikelihood class.
        loglike = LogLikelihood(llk=0.1, value=1)
        self.assertEqual(loglike.get_llk(), 0.1)
        self.assertEqual(loglike.get_value(), 1)

        # Test the destructor
        del loglike

        # Test the loglikelihood list as well.
        loglike_list = LogLikelihood_List()
        loglike_list.push_back(LogLikelihood(llk=0.1, value=1))
        loglike_list.push_back(LogLikelihood(llk=0.1, value=1))

        # Check size of the collection
        self.assertEqual(loglike_list.size(), 2)

        # Test iteration over the collection
        for _loglike in loglike_list:
            self.assertEqual(_loglike.get_llk(), 0.1)
            self.assertEqual(_loglike.get_value(), 1)

        # Call destructor
        del loglike_list

    def test_FinderLength(self):
        # Test the Finder_Length class.
        length = Finder_Length(length=10, misf=0.1)
        self.assertEqual(length.get_value(), 10)
        self.assertEqual(length.get_misf(), 0.1)

        # Test the destructor
        del length

        # Test the length list as well.
        length_list = Finder_Length_List()
        length_list.push_back(Finder_Length(length=10, misf=0.1))
        length_list.push_back(Finder_Length(length=10, misf=0.1))

        # Check size of the collection
        self.assertEqual(length_list.size(), 2)

        # Test iteration over the collection
        for _length in length_list:
            self.assertEqual(_length.get_value(), 10)
            self.assertEqual(_length.get_misf(), 0.1)

        # Call destructor
        del length_list

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

        # test the Coordinate_List class with two simple coordinates.
        # The CoordinateCollection class is a wrapper around a std::vector
        # Use the same coordinate twice to check the push_back method.
        coord1 = Coordinate(10, 20)
        coord2 = Coordinate(10, 20)
                
        # Test the Coordinate_List class. 
        coord_list = Coordinate_List()
        coord_list.push_back(coord1)
        coord_list.push_back(coord2)

        # Check the size of the collection
        self.assertEqual(coord_list.size(), 2)

        for _coord in coord_list:
            self.assertEqual(_coord.get_lat(), 10)
            self.assertEqual(_coord.get_lon(), 20)

        # Test access by index
        self.assertEqual(coord_list[0].get_lat(), 10)
        self.assertEqual(coord_list[0].get_lon(), 20)
        self.assertEqual(coord_list[1].get_lat(), 10)
        self.assertEqual(coord_list[1].get_lon(), 20)

        # Test clear method
        coord_list.clear()
        self.assertEqual(coord_list.size(), 0)
        
        # Test the destructors
        del coord
        del coord1
        del coord2
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

    def test_PGADataList(self):
        # Test the PGA_Data_List class
        pga_list = PGA_Data_List()
        pga_list.push_back(PGA_Data(name="PGA", network="netw", channel="chn",
                                    location_code="01", location=Coordinate(10, 20), 
                                    value=0.1))
        pga_list.push_back(PGA_Data(name="PGA", network="netw", channel="chn",
                                    location_code="01", location=Coordinate(10, 20), 
                                    value=0.1))
        
        # Check the size of the collection
        self.assertEqual(pga_list.size(), 2)

        # Test iteration over the collection
        for _pga in pga_list:
            self.assertEqual(_pga.get_name(), "PGA")
            self.assertEqual(_pga.get_network(), "netw")
            self.assertEqual(_pga.get_channel(), "chn")
            self.assertEqual(_pga.get_location_code(), "01")
            self.assertEqual(_pga.get_location().get_lat(), 10)
            self.assertEqual(_pga.get_location().get_lon(), 20)
            self.assertEqual(_pga.get_value(), 0.1)

        # Test clear method
        pga_list.clear()
        self.assertEqual(pga_list.size(), 0)
        

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

        # Check clear method
        rupture_list.clear()
        self.assertEqual(rupture_list.size(), 0)
