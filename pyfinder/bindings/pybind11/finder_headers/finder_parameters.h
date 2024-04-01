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
//      Finder class for holding computation parameters structures
//
//      2015-04-07
//

#ifndef __finder_parameters_h__
#define __finder_parameters_h__

#include "finder_config.h"
#include "finder_util.h"
#include "finder_opencv.h"

namespace FiniteFault { // retain scoping to FiniteFault namespace

/** @struct for holding parameters for a single template
 * */
struct Template_Info {
    Template_Info(): file_template(""), file_rupture(""), length_value(0.), width_value(0.), 
        latitude_mid(0.), longitude_mid(0.), mag_value(0.), length_index(0), mag_index(0),
        depth_top_value(0.), depth_bottom_value(20.) {}
    std::string file_template; /**< template file name */
    std::string file_rupture; /**< template file name */
    double length_value; /**< template length */
    double width_value; /**< template width value */
    double latitude_mid; /**< template midpoint latitude */
    double longitude_mid; /**< template midpoint longitude */
    double mag_value; /**< template magnitude */
    size_t length_index; /**< for a template set, assign length index */
    size_t mag_index; /**< for a template set, assign mag index */
    double depth_top_value; /**< template top depth */
    double depth_bottom_value; /**< template bottom depth */
}; // Template_Info

bool CompareByLength(const Template_Info& A, const Template_Info& B);

/** @struct for holding a mask
 * */
struct Mask_Data {
    double *msklat; /**< double array of mask latitude values */
    double *msklon; /**< double array of mask longitude values */
    double *mskval; /**< double array of mask values */
    unsigned long nMask; /**< number of values in mask */
    std::string mask_file; /**< mask file name */
}; //Mask_Data


/** \class Finder_Parameters
 * \brief Holding the parameters used in template matching. There is one instance of this class per
 * template set. NOTE THAT THE COPY CONSTRUCTOR ON THIS CLASS IS NOT DEFINED AND FAILS!!
 * */
class Finder_Parameters {
  private:
    Finder_Config* finder_config; /**< pointer to Finder_Config from which Finder_Parameters was created */
    Template_Config* templ_config; /**< pointer to Template_Config from which Finder_Parameters was created */

  public:
    bool offline_notime_test; /**< if set to true, disable time checks when processing */
    std::string name; /**< name of templates */
    std::string type_of_run; /**< either "bin" or "con" depending on whether template uses binary
                            PGA threshold, or continuous values*/
    int templ_type; /**< type of templates (generic vs fault-specific) */

    Matrix2d templates; /**< templates for this Finder_Parameters instance */
    double dkm; /**< grid resolution for templates */
    size_t N_templ; /**< number of templates */
    std::vector<size_t> rows_templ; /**< number of rows in each template */
    std::vector<size_t> cols_templ; /**< number of columns in each template */
    std::vector<size_t> rows_templ2; /**< number of rows in each template after resize */
    std::vector<size_t> cols_templ2; /**< number of columns in each template after resize */
    vector2d<size_t> template_sum_all; /**< vector of values equal to sum of elements in 
                                        template matrix for all PGA thresholds and all templates */
    std::vector<size_t> template_sum_k; /**< index of templates for which template has some
                                        values above threshold */
    std::vector<Template_Info> template_infos; /**< information structure for all templates */
    std::vector<double> lat_grid; /**< latitudes for the template grid (fault-specific templates) */
    std::vector<double> lon_grid; /**< longitudes for the template grid (fault-specific templates) */
    std::vector<location> polygon; /**< closed polygon where centroids must lie to use this set */

    size_t N_degrees; /**< number of strike orientations to test */
    std::vector<double> degrees; /**< vector of strike azimuths */

    std::vector<double> log10_thresh; /**< vector of PGA thresholds */
    size_t N_thresh; /**< number of PGA thresholds */

    std::vector< Finder_Rupture_List > ruptures; /**< rupture data */

    Mask_Data mask_data; // Note that Finder_Parameters probably now is the only owner
                            // of mask arrays created with new!

//// FUNCTIONS ////

    void set_template_config(Template_Config*);
    void set_finder_config(Finder_Config*);

    Template_Config* get_template_config() const;
    Finder_Config* get_finder_config() const;

    bool finder_initialize();
    void read_templateinfo();
    void load_templates();
    bool station_within_zone(const PGA_Data&, const Coordinate&, 
                            const double&, 
                            const size_t) const;
    void set_length_index();
    void set_mag_index();

    friend ostream& operator<< (ostream& os, const Finder_Parameters& f) {
        os << std::endl << 
        "name: " << f.name << std::endl <<
        "templ_type: " << TemplTypeString[f.templ_type] << std::endl <<
        "type_of_run: " << f.type_of_run << std::endl <<
        "N_templ: " << f.N_templ << std::endl <<
        "N_degrees: " << f.N_degrees << std::endl <<
        "length lat_grid: " << f.lat_grid.size() << std::endl <<
        "length lon_grid: " << f.lon_grid.size() << std::endl <<
        "rows_templ (lats) size: " << f.rows_templ.size() << std::endl <<
        "cols_templ (lons) size: " << f.cols_templ.size() << std::endl <<
        "rows_templ2 (lats) size: " << f.rows_templ2.size() << std::endl <<
        "cols_templ2 (lons) size: " << f.cols_templ2.size() << std::endl <<
        "dkm: " << f.dkm << std::endl <<
        "template_infos size: " << f.template_infos.size() << std::endl <<
        "degrees size: " << f.degrees.size() << std::endl <<
        "log10_thresh size: " << f.log10_thresh.size() << std::endl <<
        "template_sum_all size: " << f.template_sum_all.size() << std::endl <<
        "template_sum_k size: " << f.template_sum_k.size() << std::endl;
        return os;
    }

    friend ostream& operator<< (ostream& os, Finder_Parameters& f) {
        os << std::endl << 
        "name: " << f.name << std::endl <<
        "templ_type: " << TemplTypeString[f.templ_type] << std::endl <<
        "type_of_run: " << f.type_of_run << std::endl <<
        "N_templ: " << f.N_templ << std::endl <<
        "N_degrees: " << f.N_degrees << std::endl <<
        "length lat_grid: " << f.lat_grid.size() << std::endl <<
        "length lon_grid: " << f.lon_grid.size() << std::endl <<
        "rows_templ (lats) size: " << f.rows_templ.size() << std::endl <<
        "cols_templ (lons) size: " << f.cols_templ.size() << std::endl <<
        "rows_templ2 (lats) size: " << f.rows_templ2.size() << std::endl <<
        "cols_templ2 (lons) size: " << f.cols_templ2.size() << std::endl <<
        "dkm: " << f.dkm << std::endl <<
        "template_infos size: " << f.template_infos.size() << std::endl <<
        "degrees size: " << f.degrees.size() << std::endl <<
        "log10_thresh size: " << f.log10_thresh.size() << std::endl <<
        "template_sum_all size: " << f.template_sum_all.size() << std::endl <<
        "template_sum_k size: " << f.template_sum_k.size() << std::endl;
        return os;
    }

    Finder_Parameters() : finder_config(NULL), templ_config(NULL), templ_type(0), dkm(0), 
        N_templ(0), N_degrees(0) {}

}; //end of class Finder_Parameters

}; // end of namespace FiniteFault

#endif // __finder_parameters

// end of file: finder_parameters.h
