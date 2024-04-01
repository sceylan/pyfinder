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

#ifndef __finder_internal_h__
#define __finder_internal_h__

#include <sys/time.h>

#include "finder.h"
#include "finder_util.h"    // internal utility functions
#include "finder_config.h"
#include "finder_parameters.h"

extern "C" {
#include "gmt.h"
#include "gmt_resources.h"
#include "gmt_version.h"
}

#ifndef DEBUG_TRACE
#define DEBUG_TRACE \
    LOGV << __FILE__ << ":" << __LINE__ << ":" << __func__
#endif // DEBUG_TRACE

#define RCSID_finder_internal_h "$Id: finder_internal.h $"

using namespace cv;

// use anonymous namespace instead of #define statements for global constants
namespace FiniteFault {

/** \class PGA_Trigger
 * \brief Class to collect the actions of triggering on a PGA_Data_List. 
 * This is only a start to separate the triggering functions, such as determine_trigger, checking 
 * noisy and rejected stations, and calculate_trigrad.
 * */
class PGA_Trigger {
  private:

  public:
    PGA_Data_List raw_pga_data_list; /**< Complete pga_data_list incoming from ffd2 */
    PGA_Data_List pga_data_list; /**< Data in pga_data_list above station_thresh */
    Finder_Config* finder_config; /**< Pointer to finder_config instance used in processing */
    Finder_Parameters* finder_params; /**< Pointer to finder_parameters instance used in processing */
    Finder_Data* fdata; /**< Pointer to Finder instance used to obtain parameters */

//// FUNCTIONS /// 
    //ctor
    PGA_Trigger(PGA_Data_List& in_pga_data_list, Finder_Config* in_finder_config, 
            Finder_Parameters* in_finder_parameters, Finder_Data* in_fdata) {
        raw_pga_data_list = in_pga_data_list;
        finder_config = in_finder_config;
        finder_params = in_finder_parameters;
        fdata = in_fdata; 
    };
   
    void set_raw_pga_data_list(PGA_Data_List& in_pga_data_list) { 
        raw_pga_data_list.clear(); 
        raw_pga_data_list = in_pga_data_list; 
    }
    void set_pga_data_list(PGA_Data_List& in_pga_data_list) { 
        pga_data_list.clear(); 
        pga_data_list = in_pga_data_list; 
    }
    PGA_Data_List& get_pga_data_list() { return pga_data_list; }

    Coordinate_List chk_trigger(const Finder_List&, const size_t, PGA_Data_List&, const size_t); 
    Coordinate_List determine_trigger(const Finder_List&, const size_t, const size_t version = 0);
    int check_pga_threshold(PGA_Data_List&, const Finder_List*);
    void calculate_trigrad(PGA_Data_List&, std::map<std::string, double>&);
    size_t check_station_thresh();
    size_t remove_noisy_stations();
    void save_rejected_stations(PGA_Data_List&);
    void remove_rejected_stations(PGA_Data_List&);
    void check_trig_moveout(PGA_Data_List&);
    size_t check_connections(PGA_Data_List&, bool bMedianCheck = true);

}; // class PGA_Trigger


void load_mask(const Finder_Config& finder_config, std::vector<Finder_Parameters>& finder_parameters_list);
bool old_or_new_file(int days, const string calculatedMask);
void calculate_and_save_mask(const double dkm, const Coordinate_List& station_coord_list, const Finder_Config& finder_config, std::string omask = "");

}; // end of FiniteFault namespace

#endif // __finder_internal

// end of file: finder_internal.h
