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

#ifndef __finder_config_h__
#define __finder_config_h__

#include "finite_fault.h" // Finder_Config_Info and Template_ID

#define RCSID_finder_config_h "$Id: finder_config.h $"

namespace FiniteFault {

// template set type
enum Templ_Type {
    INVALID,
    GENERIC,
    SPECIFIC
}; // template set type

const string TemplTypeString[] =  { "INVALID", "GENERIC", "SPECIFIC"};

///////////////////////////////////////////////////////////////////
/** \struct Template_Config
 * \brief Structure for holding the configuration parameters for a template set
 * */
struct Template_Config {
    Template_Config() : name(""), dir(""), longitude_file(""), latitude_file(""), 
                    template_info_file(""), type(0), dkm(0), dD(0), minD(0), maxD(0), minL(0), 
                    maxL(0), minMag(0), maxMag(0), dip(90.), 
                    fastSearchMagRange(1.), fastSearchLatLonRange(1.) {}
    std::string name; /**< name of template set */
    std::string dir; /**< path from current directory to folder containing the templates */
    std::string longitude_file; /**< file containing the longitude co-ords of the templates */
    std::string latitude_file; /**< file containing the latitude co-ords of the templates */
    std::string template_info_file; /**< file containing info such as length, width, centroid, and 
                                    filenames of templates */
    int type; /**< enumeration for generic or specific */
    double dkm; /**< km resolution of template both lat and lon */
    double dD; /**< strike resolution in degrees */
    double minD; /**< minimum strike in degrees */
    double maxD; /**< maximum strike in degrees */
    double minL; /**< minimum rupture length in km */
    double maxL; /**< maximum rupture length in km */
    double minMag; /**< minimum magnitude above which the magnitude must be to use set */
    double maxMag; /**< maximum magnitude below which the magnitude must be to use set */
    double dip; /**< fault dip */
    double fastSearchMagRange; /**< templates with +- this range will be tested */
    double fastSearchLatLonRange; /**< templates with +- this range will be tested */
    std::vector<std::pair<double, double> > polygon; /**< polygon where centroid must fall to use set */
};

/** \class Finder_Config
 * \brief Class for handling configuration file reading and storing parameters read from file
 * */
class Finder_Config {
  public:
    const char* config_file; /**< config file, used to fill this class */

// gmt parameters
    std::string gmt_prefix; /**< some versions of GMT require a prefix before gmt commands */
    std::string gmt_api_option; /**< use of API rather than system calls */

// triggering parameters
    PGA_Data_List station_thresh; /**< PGA data list storing per-station thresholds 
                                    (in place of PGA)*/
    size_t N_thresh; /**< positive integer denoting number of ground-motion thresholds */
    std::vector<double> thresh; /**< PGA threshold levels in cm/s/s */
    size_t min_trigger_stations; /**< minimum number of stations above PGA threshold for 
        trigger */ 
    double trigger_radius;  /**< maximum distance between trigger stations for them to count
        towards event triggering */
    double max_station_trigrad; /**< max value (km) for station specific triggering radius*/
    std::string use_fixed_trigrad; /**< yes/no switch for using station specific triggering radius*/
    size_t N_network; /**< number of secondary networks, which are excluded from triggering */
    std::vector<std::string> secondary_networks; /**< network codes for secondary networks, which are
        excluded from triggering */
    std::string station_config; /**< optional file that contains specific station thresholds for
        triggering */

// magnitude parameters
    double mag_regression_thresh; /**< Maximum magnitude for which magnitude threshold
        method will be used, otherwise use Finder rupture-based magnitude */

// mask parameters
    std::string regional_mask; /**< path from current directory folder containing mask */
    double mask_station_distance; /**< minimum distance between stations when calculating a
        mask */

// rupture parameters
    std::vector<std::string> template_sets_files; /**< list of template configuration filenames */
    std::vector<Template_Config> list_template_sets; /**< vector of template sets */
    std::string template_dir; /**< path from current directory to folder containing the templates */
    std::string template_id_file; /**< file containing list of template ids */
    Template_ID_List template_id_list; /**< template id information for all templates */
    double dD; /**< strike resolution in degrees */
    double minD; /**< minimum strike in degrees */
    double maxD; /**< maximum strike in degrees */
    double minL; /**< minimum rupture length in km */
    double maxL; /**< maximum rupture length in km */
    double default_depth; /**< default depth used in epicenter info */
    double default_depth_uncer; /**< default depth uncertainty */
    double border_degrees;  /**< minimum lat/lon padding in degrees around station extent */
    double tension; /**< tension factor for gmt surface interpolation */
    size_t image_pixels; /**< minimum number of image pixels that must be above PGA threshold
        for solution to be calculated */
    size_t max_image_pixels; /**< number of image pixels that must be above PGA threshold to 
        use that PGA threshold (highest PGA = faster computation) */
    double resize_fraction; /**< how to resize the image and templates */
    double min_log10PGA; /**< value used for border values in image */
    double max_misfit; /**< maximum misfit to choose a higher PGA threshold */
    double sigma_length; /**< related to misfit/probability calculation */
    double sigma_azimuth; /**< related to misfit/probability calculation */
    double sigma_latlon; /**< related to misfit/probability calculation */
    double stop_len_pc; /**< stop the process if the fault estimate shrinks by more than this % */
    double restart_len_pc; /**< restart the process if the fault estimate grows by more than this % */
    double epi_fault_dist_thresh; /**< threshold for distance (km) between epicenter and fault 
        before new event declared */
    size_t mag_option; /**< determines the empirical relationship between estimated fault 
        length and magnitude: 0) Use Template_Info mag, 1) Wells & Coppersmith, 2) Blaser */
    size_t max_ruptures; /**< maximum number of rupture points */
    std::string include_continuous; /**< inclusion of continuous template/image */
    std::string run_speed; /**< select either "fast" or "complete" to switch between divide and
        conquer and exhaustive search of strike and rupture length solutions */
    int uncertainty_method; /**< switch for uncertainty calculation methods */

// output/plotting parameters
    std::string color_scale; /**< path from current directory to the color scale file used by
        GMT plots */
    std::string fault_definitions; /**< path from current directory to file containing list of 
        faults for the region to be used in GMT plots*/
    std::string display_windows; /**< boolean for window display */
    std::string gmt_plot; /**< option to produce GMT plots */
    std::string gmt_folder; /**< path from current directory to where standard GMT plotting files */
    std::string data_folder; /**< path from current directory to directory for temporary
        output files */
    double min_likelihood_estimate_for_message; /**< minimum likelihood value to send alert message
        and update version number */

    void Init(const char* config_file);
    void set_config_file(const char* in_config_file) { config_file = in_config_file; }
    void read_config_file(const char* in_config_file);
    void read_config_file();
    void copyTo(Finder_Config_Info* finder_config_info);
    void read_template_ID_file();
    void read_template_set_file(std::string config_file);
    void load_station_thresh();

}; //Finder_Config

}; // end namespace FiniteFault

#endif // __finder_config

// end of file: finder_config.h
