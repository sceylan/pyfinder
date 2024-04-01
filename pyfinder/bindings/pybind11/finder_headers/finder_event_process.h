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
//      Finder processing ground motion images
//
//      2019-02-28
//

#ifndef __finder_event_process_h__
#define __finder_event_process_h__

#include <sys/time.h>

#include "finder_internal.h"

extern "C" {
#include "gmt.h"
#include "gmt_resources.h"
#include "gmt_version.h"
}

#define RCSID_finder_event_process_h "$Id: finder_event_process.h $"

using namespace cv;

// use anonymous namespace instead of #define statements for global constants
namespace FiniteFault {

/* Struct for image dimensions and resolution
 * */
struct ImageParams {
    double minLon;
    double maxLon;
    double minLat;
    double maxLat;
    size_t NLat;
    size_t NLon;
    double dLat;
    double dLon;
};

/* Class for processing a finder event, taking it from incoming PGA data to finding best estimate
 * source parameters
 */
class Finder_Event_Process {
  private:
    // event pause/restart parameters
    double STOP_PERCENTAGE; /**< stop the process if the fault estimate shrinks by more than 20% */
 	double START_PERCENTAGE; /**< start the process if the fault estimate grows by more than 60% */

    // Magnitude regression parameters
    double MR_SWEIGHT; /**< for magnitude regression, relative misfit weight between P and S peak amps */
    size_t MR_MINSSTA; /**< for magnitude regression, minimum number of valid S stations to be used */
    double MR_MINMAG; /**< minimum magnitude for magnitude regression */
    double MR_MAXMAG; /**< maximum magnitude for magnitude regression (originally 7.0) */
    double MR_MAGSTEP; /**< magnitude step for magnitude regression */
    size_t MR_SONLY_THRESH; /**< for magnitude regression, above this number of S-waves, only S are considered */

    Finder_Config* finder_config; /**< finder_config to access params */
    std::vector<Finder_Parameters*> finder_parameters_list; /**< all finder_parameters in program */
    std::vector<Finder_Parameters*> proc_finder_parameters_list; /**< finder_parameters to use in this processing step */
    Finder_Parameters* finder_parameters; /**< GENERIC finder_parameters */
    Finder_Data* finder_data; /**< finder_data event parameters for this timestep */

    size_t version; /**< processing version number */
    size_t cmn_pgaind; /**< minimum pgaind to across ALL template sets from previous timestep */

    double minlog10PGA; /**< minimum log10(PGA) value for padding the observed data image */
    ImageParams imgparams; /**< extent parameters for GENERIC data image */
    std::vector<cv::Mat> Image; /**< vector of data images thresholded at each PGA */
    std::vector<double> image_sum; /**< pixel count for PGA-thresholded data images */

    PGA_Data_List sel_pga_data; /**< structure of PGA observations used in processing this timestep */
    size_t Nstat; /**< number of PGA observations used in processing this timestep */

  public:

/// ctor
    Finder_Event_Process(Finder_Config* fc, std::vector<Finder_Parameters*> fpl, Finder_Data* fd, size_t ver);

    void set_finder_config(Finder_Config* in_finder_config) { finder_config = in_finder_config; };
    void set_finder_parameters(Finder_Parameters* in_finder_parameters) {
        finder_parameters = in_finder_parameters; 
    };

    bool Init();

    double get_minlon() { return imgparams.minLon; };
    double get_maxlon() { return imgparams.maxLon; };
    double get_minlat() { return imgparams.minLat; };
    double get_maxlat() { return imgparams.maxLat; };
    double get_dLatDegree() { return imgparams.dLat; };
    double get_dLonDegree() { return imgparams.dLon; };
    int get_NLon() { return imgparams.NLon; };
    int get_NLat() { return imgparams.NLat; };
    size_t get_version() { return version; };
    size_t get_cmn_pgaind() { return cmn_pgaind; };
    size_t get_size_fdparam_list() { return proc_finder_parameters_list.size(); };
    void set_cmn_pgaind(size_t in) { cmn_pgaind = in; };

    // reject amplitude data that are deemed outlying (latent or anomalous PGA)
    void reject_data_by_percentile(PGA_Data_List& pga_data_list);
    // reject amplitude data that are deemed too late based on moveout
    void reject_data_by_time(PGA_Data_List& pga_data_list);

    void process_image(const double timestamp, const size_t version, PGA_Data_List& pga_data_list);

    bool centroid_check(const PGA_Data_List& pga_data_list, const Finder_Centroid& event_centroid);
    bool consistent_epi_fault(); /**< Check proxmity of epicenter and fault trace */

    double calculate_origin_time(const PGA_Data_List& pga_data_list);
    double calculate_origin_time();

    bool prepImage(PGA_Data_List& pga_data_list, std::vector<Mat> &img_list);
    bool gmtImage(std::vector<double> lat, std::vector<double> lon, std::vector<double> log10PGA, 
        std::vector<cv::Mat> &raw_img_list);
    double mag_regression(const PGA_Data_List& pga_data_list); 
    double mag_regression_Sonly(const PGA_Data_List& pga_data_list); 
    double computeGMPE(double mag, double dist, bool phase);

    void writeRuptureFile();

}; // end Finder_Event_Process class

class Template_Match {
  private:
    // Template matching per template set
    Finder_Event_Process* fep; /**< calling instance */
    Finder_Config* finder_config; /**< config parameters */
    Finder_Parameters* finder_parameters; /**< finder_parameters for single template set to be used */
    Finder_Data* finder_data; /**< data parameters to be filled */
    Template_Config* templ_config; /**< template set */
    Finder_Data_Template* finder_data_templ; /**< data parameters relating to template to be filled */

    // opencv parameters
    int MATCH_METHOD_GENERAL; /**< match method for misfit statistics */
	int MATCH_METHOD_GRID_SEARCH; /**< match method for searching over strike and length */

    ///What we want to output
    vector2d <double> strikesMisfit; /**< best misfit value for each strike and PGA */
    vector2d <double> strikesLat; /**< best loc lat for each strike and PGA */
    vector2d <double> strikesLon; /**< best loc lon for each strike and PGA */
    std::vector<double> strikesLikelihood; /**< best likelihood for each strike and PGA */

    vector2d <double> lengthsMisfit; /**< best misfit value for each templ and PGA */
    vector2d <double> lengthsLat; /**< best loc lat for each templ and PGA */
    vector2d <double> lengthsLon; /**< best loc lon for each templ and PGA */
    std::vector<double> log_lengthsLikelihood; /**< best likelihood for each templ and PGA */

    vector3d<double> minVal_all; /**< minimum misfit for each PGA, strike and template */
    vector3d<double> minLoc_lat; /**< best loc lat for each PGA, strike and template */
    vector3d<double> minLoc_lon; /**< best loc lon for each PGA, strike and template */
    vector3d<size_t> minCalc_all; /**< flag for computation completed at each PGA, strike and template */

    cv::Mat* in_data_img; /**< data image */
    std::vector<cv::Mat> Image; /**< vector of data images thresholded at each PGA */
    std::vector<double> image_sum; /**< pixel count for PGA-thresholded data images */

  public:

    Template_Match(Finder_Event_Process* fep, Finder_Config* finder_config, 
    Finder_Parameters* finder_parameters, Finder_Data* finder_data, cv::Mat* img, 
        std::vector<cv::Mat> Image, std::vector<double> image_sum);

    Finder_Data_Template* get_finder_data_templ() { return finder_data_templ; }

    void set_finder_config(Finder_Config* in_finder_config) { finder_config = in_finder_config; };
    void set_finder_parameters(Finder_Parameters* in_finder_parameters) {
        finder_parameters = in_finder_parameters; 
    };
 
    bool Init();

    static void* proc_template_match_image(Template_Match* tm); 
    bool template_match_image();

    bool getImage(cv::Mat& image_temp, cv::Mat& templ_temp, size_t best_x, size_t best_y, 
        cv::Mat& image_i);

    bool rotate2D(const cv::Mat& src, cv::Mat& dst, const double degrees);
    bool rotation_template_match(size_t pga_threshold_index);
    bool fast_template_match_generic(size_t pga_threshold_index);
    bool fast_template_match_specific(size_t pga_threshold_index);
    bool prepTemplate(size_t i, size_t k, cv::Mat& templ);
    bool wrapMatch(int MATCH_METHOD, size_t i, size_t j, size_t k);
    bool matching_method(int MATCH_METHOD, const double angle, const cv::Mat& img, const cv::Mat& templ, 
        cv::Mat& result, double& matchCorr, Point& matchLoc, Point& imgLoc);

    double pixel_guess(size_t pga_ind, size_t& len_ind);

    void strike_estimate();
    void strike_uncertainty(); 

    double mag_formula(const double length, const size_t MAG_OPTION);
    void magnitude_estimate(const size_t MAG_OPTION);
    void magnitude_uncertainty(const size_t MAG_OPTION, const double dlog_L);
    bool lat_lon_uncertainties(const Mat& resultLikelihood, const std::vector<double> result_axis_lat, 
        const std::vector<double> result_axis_lon, double& lat_uncer, double& lon_uncer);
    void lat_lon_uncer_estimate(const Mat& result, const std::vector<double>& result_axis_lat, 
        const std::vector<double>& result_axis_lon, double& lat_unc, double& lon_unc);
    void return_fault_ends(const double best_strike, const double best_length, 
        const std::vector<double>& best_centroid, const double dip,
        const double fwid, const double depth_top_value, const double depth_bottom_value,
        Finder_Rupture_List& fault_polygon);
    Finder_Rupture_List generate_finder_rupture_list(const std::vector<double>& fault_end1, 
        const std::vector<double>& fault_end2); 

    double gaussian_point(double lat, double lon, double mean_lat, double mean_lon, double sigma_lat, 
        double sigma_lon);
    void gaussian_matrix(size_t Nlat, size_t Nlon, const std::vector<double> result_axis_lat, 
        const std::vector<double> result_axis_lon, double mean_lat, double mean_lon, double sigma_lat, 
        double sigma_lon, Mat& gaussian_result);

    const std::string outfile_in_temp_folder(const std::string prefix, const double thresh, 
        const double timestamp);

    void writeDebugFiles(const size_t version);
    void writeThreshFiles(const size_t version);
}; // end Template_Match class

}; // end of FiniteFault namespace

#endif // __finder_event_process

// end of file: finder_event_process.h
