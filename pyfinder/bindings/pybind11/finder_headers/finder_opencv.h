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

#ifndef __finder_opencv_h__
#define __finder_opencv_h__

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

using namespace cv;

namespace FiniteFault { // retain the scope of these functions to namespace FiniteFault

/////////////define a way of handling 2D and 3D Matrices easily///////////////

/** \class Matrix2d
 * \brief Extending the opencv Mat class for easier use.
 * Matrix2d contains a pointer to a Mat structure, and provides access functions based on 
 * indices and index arithmetic. Note that standard operations have had to be overloaded to
 * allow valid use of this class for example in = and push_back to vector. 
 */
class Matrix2d {
  public:

    Matrix2d() : d1(0), d2(0), Ndata(0), Matdata(NULL) {};

    Matrix2d(size_t d1_new, size_t d2_new) : d1(d1_new), d2(d2_new) {
        Ndata = d1*d2;
        this->Matdata = new Mat[Ndata];
    }

    ~Matrix2d() {
        if (Matdata != NULL) {
            d1 = 0;
            d2 = 0;
            Ndata = 0;
            delete [] Matdata;
            Matdata = NULL;
        }
    }

    Matrix2d(const Matrix2d & in) {
        if (this != &in) {
            Mat* new_matdata = new Mat[in.Ndata];
            for (size_t i=0; i<in.Ndata; i++) {
                in.Matdata[i].copyTo(new_matdata[i]);
            }
            Matdata = new_matdata;
            d1 = in.d1;
            d2 = in.d2;
            Ndata = in.Ndata;
        }
    }

    Mat * assign_size(size_t d1_new, size_t d2_new) {
        d1 = d1_new; d2 = d2_new;
        Ndata = d1*d2;
        return this->Matdata = new Mat[Ndata];
    }

    Mat & operator()(size_t i, size_t j) {
        assert(i*d2 + j < d1*d2);
        return Matdata[i*d2 + j];
    }

    Mat const & operator()(size_t i, size_t j) const {
        assert(i*d2 + j < d1*d2);
        return Matdata[i*d2 + j];
    }

    Matrix2d & operator=(const Matrix2d& in) {
        if (this != &in) {
            Mat* new_matdata = new Mat[in.Ndata];
            for (size_t i=0; i<in.Ndata; i++) {
                in.Matdata[i].copyTo(new_matdata[i]);
            }
            Matdata = new_matdata;
            d1 = in.d1;
            d2 = in.d2;
            Ndata = in.Ndata;
        }
        return *this;
    }

    size_t size() const { return Ndata; }

    size_t size() { return Ndata; }

    friend ostream& operator<< (ostream& os, const Matrix2d& f) {
        os << std::endl << 
        "Ndata: " << f.Ndata << std::endl <<
        "d1: " << f.d1 << std::endl <<
        "d2: " << f.d2 << std::endl <<
        "size: " << f.size() << std::endl <<
        "data pointer: " << f.Matdata << std::endl <<
        "data Mat: " << f.Matdata->dims << " " << f.Matdata->cols << " " << f.Matdata->rows << " " 
            << f.Matdata->size() << std::endl;
        return os;
    }

  private:
    size_t d1,d2, Ndata;
    Mat* Matdata;
};

/** \class Matrix3d
 * \brief Extending the opencv Mat class for easier use.
 * Matrix3d contains a pointer to a Mat structure, and provides access functions based on 
 * indices and index arithmetic. NOTE THAT THIS CLASS IS INCOMPLETE AND WILL FAIL ON 
 * ASSUMED OPERATIONS SUCH AS = AND PUSH_BACK. SEE Matrix2d CLASS FOR EXAMPLES. */
class Matrix3d {
public:

    Matrix3d() {};

    Matrix3d(size_t d1_new, size_t d2_new, size_t d3_new) :
        d1(d1_new), d2(d2_new), d3(d3_new)
        {  Ndata = d1*d2*d3;  this->Matdata = new Mat[Ndata];}

    Mat * assign_size(size_t d1_new, size_t d2_new, size_t d3_new)  
         {  d1 = d1_new; d2 = d2_new; d3 = d3_new;
            Ndata = d1*d2*d3;  return this->Matdata = new Mat[Ndata];}      
        
    ~Matrix3d()   { 
    	if (Matdata != NULL) {delete[] Matdata; Matdata = NULL; } 
    }
	
    Mat & operator()(size_t i, size_t j, size_t k) {
    	assert(i*d2*d3 + j*d3 + k < d1*d2*d3);
        return Matdata[i*d2*d3 + j*d3 + k];
    }
    
    Mat const & operator()(size_t i, size_t j, size_t k) const {
    	assert(i*d2*d3 + j*d3 + k < d1*d2*d3);
        return Matdata[i*d2*d3 + j*d3 + k];
    }

	size_t size() { return Ndata; }

private:
    size_t d1,d2,d3, Ndata;
    Mat* Matdata;
};

}; // end of namespace FiniteFault

///////////////////////////////////////////////////////////////////

#endif // __finder_opencv

// end of file: finder_opencv.h
