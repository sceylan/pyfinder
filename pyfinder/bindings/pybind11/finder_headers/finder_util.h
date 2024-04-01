/*
 * <Finder 2, C++ Finite Fault Algorithm Using Template Matching>
 * Copyright (C) <2016>  
 *      Deborah Smith, United States Geological Survey, deborahsmith@usgs.gov
 *      Maren Böse, ETH Zurich, maren.boese@sed.ethz.ch
 *      Jennifer Andrews, California Institute of Technology, jrand@gps.caltech.edu
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the 
 * GNU General Public License as published by the Free Software Foundation, either version 3 of 
 * the License, or (at your option) any later version with the additional stipulation that you 
 * give proper reference when using or modifying this code.
 *
 * The proper references are:
 * Maren Böse, Thomas H. Heaton, and Egill Hauksson, (2012) "Real-time finite fault rupture 
 *      detector," Geophysical Journal International, Vol. 191, Issue 2, pages 803-812.
 * Maren Böse, Claude Felizardo, and Thomas H. Heaton, (2015) "Finite-fault rupture detector 
 *      (FinDer):  going real-time in Californian ShakeAlert warning system," Seismological 
 *      Research Letters, Vol. 86, Issue 6, pages 1692-1704.
 * Böse, M., D.E. Smith, C. Felizardo, M.-A. Meier, T.H. Heaton, J.F. Clinton (2018) "FinDer 
 *      v.2: Improved Real-time Ground-Motion Predictions for M2-M9 with Seismic Finite-Source 
 *      Characterization," Geophysical Journal International, Vol. 212, pages 725-742.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See 
 * the GNU General Public License for more details. You should have received a copy of the GNU 
 * General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * This software is preliminary or provisional and is subject to revision. It is being provided to 
 * meet the need for timely best science. The software has not received final approval by the U.S. 
 * Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS the U.S. 
 * Government as to the functionality of the software and related material nor shall the fact of 
 * release constitute any such warranty. The software is provided on the condition that neither 
 * the USGS nor the U.S. Government shall be held liable for any damages resulting from the 
 * authorized or unauthorized use of the software.
 *
 * This software is preliminary or provisional and is subject to revision. It is being provided to 
 * meet the need for timely best science. The software has not received final approval by ETH 
 * Zurich. No warranty, expressed or implied, is made by ETH Zurich as to the functionality of the 
 * software and related material nor shall the fact of release constitute any such warranty. The 
 * software is provided on the condition that ETH Zurich shall not be held liable for any damages 
 * resulting from the authorized or unauthorized use of the software.
 *
 * This program is provided “as is”. The California Institute of Technology disclaims all 
 * warranties, including any implied warranties of merchantability or fitness for any purpose.
 */

//
//      Finder internal structures
//
//      2015-04-07
//



#ifndef __finder_util_h__
#define __finder_util_h__


#include <assert.h>         // assert macro
#include <string.h>         // std::string
#include <vector>           // std::vector
#include <iostream>         // std::cout, std::end, ...


#define RCSID_finder_util_h "$Id: finder_util.h $"


namespace FiniteFault {

class Error {
  public:
      Error(const char* text = "Error") : _text(text) {}
      Error(const std::string& text) : _text(text) {}

      virtual const char* what() const throw() {
          return _text.c_str();
      }

  private:
      std::string _text;
}; // class Error


/////////////define a way of handling 3D vectors easily///////////////
template <typename T>
class vector3d {
public:
    vector3d(size_t d1=0, size_t d2=0, size_t d3=0, T const & t=T()) :
        d1(d1), d2(d2), d3(d3), data(d1*d2*d3, t)
    {Ndata = d1*d2*d3;}

    T & operator()(size_t i, size_t j, size_t k) {
    	assert(i*d2*d3 + j*d3 + k < d1*d2*d3);
        return data[i*d2*d3 + j*d3 + k];
    }

    T const & operator()(size_t i, size_t j, size_t k) const {
    	assert(i*d2*d3 + j*d3 + k < d1*d2*d3);
        return data[i*d2*d3 + j*d3 + k];
    }

    void resize(size_t d1_new=0, size_t d2_new=0, size_t d3_new=0) {
        d1 = d1_new;
        d2 = d2_new;
        d3 = d3_new;
        data.assign(d1*d2*d3, 0.);
        Ndata = d1*d2*d3;
    }

    void resize(size_t d1_new=0, size_t d2_new=0, size_t d3_new=0, T const & t=T()) {
        d1 = d1_new;
        d2 = d2_new;
        d3 = d3_new;
        data.assign(d1*d2*d3, t);
        Ndata = d1*d2*d3;
    }

    size_t size() { return Ndata; }

private:
    size_t d1,d2,d3, Ndata;
    std::vector<T> data;
};

///////////////////////////////////////////////////////////////////

/////////////define a way of handling 2D vectors easily///////////////

template <typename T>
class vector2d {
public:
    vector2d(size_t d1=0, size_t d2=0, T const & t=T()) :
        d1(d1), d2(d2), data(d1*d2, t)
    {Ndata = d1*d2;}

    T & operator()(size_t i, size_t j) {
    	if (i*d2 + j  >= d1*d2) { throw FiniteFault::Error(std::string("Tried to go beyond the vector2d bounds!")); }
        return data[i*d2 + j];
    }

    T const & operator()(size_t i, size_t j) const {
    	if (i*d2 + j  >= d1*d2) { throw FiniteFault::Error(std::string("Tried to go beyond the vector2d bounds!")); }
        return data[i*d2 + j];
    }

    void resize(size_t d1_new=0, size_t d2_new=0, T const & t=T()) {
	    d1 = d1_new;
	    d2 = d2_new;
	    data.resize(d1*d2,t);
	    Ndata = d1*d2;
	}
    
    size_t size() const{ return Ndata; }
	size_t size1() const { return d1; }
	size_t size2() const { return d2; }


private:
    size_t d1,d2, Ndata;
    std::vector<T> data;
};

///////////////////////////////////////////////////////////////////

std::string find_key_word(const std::string& tempbuf);
std::string config_line4string_value(const std::string& tempbuf);
std::vector<std::string> config_line4string_vect(const std::string& tempbuf);
bool is_file_exist(const char* fileName);
bool is_directory_exist( const char* pzPath );

double lat2km(const double length_lat);
double lon2km(const double length_lon, const double avlat);
double km2lat(const double length_km);
double km2lon(const double length_km, const double avlat);
double dist_deg2km(const double lat1, const double lon1, const double lat2, const double lon2);
double loc2az(const double lat1, const double lon1, const double lat2, const double lon2);

std::string get_time_now();

typedef std::pair<double, double> location; /**< Typedef containing pair of <lat, lon>*/
double isLeft(double, double, double, double, double, double);
bool inRegion(std::vector<location> polygon, double ptlat, double ptlon);
}; // end of FiniteFault namespace

#endif // __finder_util

// end of file: finder_util.h
