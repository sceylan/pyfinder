/** @file finder.h Header information for main finder classes
 * */

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

/*
 *      FINDER Processing Library API
 *
 *      2015-08-26
 */

#ifndef __finder_h__
#define __finder_h__


#include <locale>
#include "finite_fault.h"

// to permit GMT library runtime check
extern "C" {
#include "gmt_version.h"
}

#ifndef DEBUG_TRACE
#define DEBUG_TRACE \
    LOGV << __FILE__ << ":" << __LINE__ << ":" << __func__
#endif // DEBUG_TRACE

#define RCSID_finder_h "$Id: finder.h $"

////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////
// declare the FINDER Processing library API

namespace FiniteFault {

const std::string GMT_LIBRARY_VERSION = GMT_STRING;

// forward declare internal structures
class Finder_Config;
class Finder_Parameters;
class Matrix2d;
class Finder_List;

class Finder {
  public:

    static void Set_Debug_Level(const int debug_level) { Debug_Level = debug_level; } 
    static int Get_Debug_Level() { return Debug_Level; };

    static void Init(const char* config_file, const Coordinate_List& station_coord_list);
    static std::string Get_data_dir();

    static Finder_Config_Info Get_finder_config_info() { return Finder_config_info; }
    static Template_ID_List Get_template_id_list() { return Template_id_list; }

    static size_t Nfinder;
    static bool New_mask;

    size_t version;

    // constructors
    Finder(const Coordinate epicenter, const PGA_Data_List& pga_data_list, const long event_id, 
        const long hold_time);

    friend ostream& operator<< (ostream& os, Finder& f) {
        os << "[" << f.f_data << "]";
        return os;
    }

    // destructor
    ~Finder(); // deallocates internal memory

    static std::string Get_GMT_runtime_version();
    static std::string Get_alg_version();

    bool static Create_New_Mask(const Coordinate_List& station_coord_list, const Finder_List& flist, 
        std::string omask = "");

    static PGA_Data_List Associate_Time(PGA_Data_List& pga_data_list_initial);
    static PGA_Data_List Add_Station_Noise(const PGA_Data_List& pga_data_list, 
        Station_Map& station_map, Seismic_Data_Map& seismic_data, const std::string network_analyze);

    // determine if this is a new rupture or existing -- probably should return instance if existing?
    static Coordinate_List Scan_Data(PGA_Data_List& pga_data_list, const Finder_List& flist, 
        const bool offline_test = false);

    // scale data depending on phase
    void scale_data_by_phase(PGA_Data_List& pga_data_list, PGA_Data_List& scaled_pga_data_list);

    // main process function
    void process(const double timestamp, PGA_Data_List& pga_data_list);

    // prepare to stop processing this event
    void stop_processing();

    static void delete_templates();

    // accessor methods to retrieve calculated values
    long get_event_id() const { return this->f_data.get_event_id(); }
    double get_mag() const { return this->f_data.get_mag(); }
    double get_mag_FD() const { return this->f_data.get_mag_FD(); }
    double get_mag_reg() const { return this->f_data.get_mag_reg(); }
    double get_mag_uncer() const { return this->f_data.get_mag_uncer(); }
    Coordinate get_epicenter() const { return this->f_data.get_epicenter(); }
    Coordinate get_epicenter_uncer() const { return this->f_data.get_epicenter_uncer(); }
    double get_origin_time() const { return this->f_data.get_origin_time(); }
    double get_origin_time_uncer() const { return this->f_data.get_origin_time_uncer(); }
    double get_depth() const { return this->f_data.get_depth(); }
    double get_depth_uncer() const { return this->f_data.get_depth_uncer(); }
    double get_likelihood_estimate() const { return  this->f_data.get_likelihood_estimate(); }
    double get_rupture_length() const { return this->f_data.get_rupture_length(); }
    double get_rupture_azimuth() const { return this->f_data.get_rupture_azimuth(); }
    double get_azimuth_uncer() const { return this->f_data.get_azimuth_uncer(); }
    size_t get_Nstat_used() const { return this->f_data.get_Nstat_used(); }
    Finder_Centroid get_finder_centroid() const { return this->f_data.get_finder_centroid(); }
    Finder_Centroid get_finder_centroid_uncer() const { return this->f_data.get_finder_centroid_uncer(); }
    Finder_Rupture_List get_finder_rupture_list() const { return this->f_data.get_finder_rupture_list(); }
    Finder_Azimuth_List get_finder_azimuth_list() const { return this->f_data.get_finder_azimuth_list(); }
    Finder_Length_List get_finder_length_list() const { return this->f_data.get_finder_length_list(); }
    Finder_Azimuth_LLK_List get_finder_azimuth_llk_list() const { return this->f_data.get_finder_azimuth_llk_list(); }
    Finder_Length_LLK_List get_finder_length_llk_list() const { return this->f_data.get_finder_length_llk_list(); }
    LogLikelihood2D_List get_centroid_lat_pdf() const { return this->f_data.get_centroid_lat_pdf(); }
    LogLikelihood2D_List get_centroid_lon_pdf() const { return this->f_data.get_centroid_lon_pdf(); }

    long get_last_message_time() const { return this->last_message_time; }
    long get_start_time() const { return this->start_time; }
    Finder_Flags get_finder_flags() const { return this->finder_flags; }
    long get_hold_time() const { return this->hold_time; }
    size_t get_version() const { return this->version; }
    PGA_Data_List get_pga_data_list() const
        { return this->pga_data_list; }
    PGA_Data_List get_rejected_stations() const
        { return this->rejected_stations; }
    PGA_Data_List get_pga_above_min_thresh() const { return this->pga_above_min_thresh; }
    static Finder_Config* get_finder_config() { return &Finder_config; };
    static Finder_Parameters* get_finder_parameters() { return &Finder_parameters; };
    std::vector<Finder_Parameters*> get_finder_parameters_list() { return fparam_list; };

    // Functions for inserting information from the Core_Info into Befores variables
    void set_last_message_time(const long last_message_time)
        { this->last_message_time = last_message_time; }
    void set_start_time(const long start_time)
        { this->start_time = start_time; }
    void set_finder_flags(const Finder_Flags finder_flags_new)
        { this->finder_flags = finder_flags_new; }
    void set_hold_time(const long hold_time) 
        { this->hold_time = hold_time; }
    void set_rejected_stations(const PGA_Data_List rejected_stations) 
        { this->rejected_stations = rejected_stations; }
    void set_pga_data_list(const PGA_Data_List pga_data_list_new) 
        { this->pga_data_list = pga_data_list_new; }
    void set_pga_above_min_thresh(const PGA_Data_List pga_above_min_thresh_new) 
        { this->pga_above_min_thresh = pga_above_min_thresh_new; }

    // variables to be taken from core_info and inserted into Befores
    Finder_Data f_data; /**< Pointer to internal Finder_Data structure */
    Finder_Internal f_data_prev; /**< Finder_Internal structure that stores the parameters sent in 
        the most recent alert message (i.e. ignores timesteps with small changes) */
    std::vector<Finder_Parameters*> fparam_list;

  private:

    static Finder_Config Finder_config;
    static Finder_Parameters Finder_parameters;
    static Matrix2d Templates;

    static std::vector<Finder_Parameters> Finder_parameters_list;
    static std::vector<Matrix2d> Templates_list;

    // enable/disable debug levels
    static int Debug_Level;

    //static vector2d <double> Template_sum;

    long start_time; /**< Finder object creation time for event */
    long last_message_time; /**< Last message processing time for event */

    // Used to determine behavior for the Finder Object
    Finder_Flags finder_flags; /**< Flags controlling processing for this Finder object*/
    long hold_time; /**< Config parameter to keep events active */

    // FinDer to BEFORES information
    //upon initialization
    static Finder_Config_Info Finder_config_info; /**< Finder config info to be passed to BEFORES */
    static Template_ID_List Template_id_list; /**< Template name list to be passed to BEFORES */

    PGA_Data_List pga_data_list; /**< Event PGA data list */
    PGA_Data_List scaled_pga_data_list; /** Event PGA data list with phase scaling */
    PGA_Data_List pga_above_min_thresh; /**< List of stations with PGA above threshold */
    PGA_Data_List rejected_stations; /**< List of statios rejected for event */
        
}; // class Finder

class Finder_List : public TemplateCollection<Finder*> {
}; // class Finder_List

}; // end of FiniteFault.h namespace

#endif // __finder_h__

// end of file: finder.h
