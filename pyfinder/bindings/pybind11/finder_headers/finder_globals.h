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

#ifndef __finder_globals_h__
#define __finder_globals_h__

#include <iostream>

#ifdef ENABLE_PLOG // PLOG enabled so include the header
    #include "plog/Log.h"
    #define ELL ""
#endif
#ifdef ENABLE_SCLOG 
    #include "plog2sclog_wrapper.h"
    #define ELL "ELL"
#endif
#ifndef LOGV
    #define LOGV std::cout
    #define LOGD std::cout 
    #define LOGI std::cout 
    #define LOGW std::cout
    #define LOGE std::cout
    #define LOGF std::cout
    #define LOGN std::cout
    #define ELL std::endl
#endif 


namespace FiniteFault {
    const std::string LIB_VERSION = std::string("3.2.4_2023-10-31"); /**< Finder library version string */
    const std::string FD_VERSION_STRING = std::string("finder") + std::string("-") + FiniteFault::LIB_VERSION; /**< algorithm version string */

    const int BLEN = 1000; /**< bufferlength */
    const std::string TEMP_DIR = std::string("temp"); /**< name of temporary data directory */
    const std::string TEMP_DATA_DIR = std::string("temp_data");  /**< location of log files for all new events */

    const std::string PADDED_DATA_FILE = TEMP_DIR + std::string("/data_for_gmt.txt"); /**< name of padded data file */
    const std::string GRIDDED_DATA_FILE = TEMP_DIR + std::string("/mean.xyz"); /**< name of gridded data file */
    const std::string RAW_GRIDDED_DATA_NC = TEMP_DIR + std::string("/raw_data.nc"); /**< name of raw gridded data file */
    const std::string GRIDDED_DATA_NC = TEMP_DIR + std::string("/data.nc"); /**< name of gridded nc data file */
    const std::string MASK_TRIM_NC = TEMP_DIR + std::string("/mask_trim.nc"); /**< name of trimmed mask nc data file */
    const std::string GMT_IMAGE_FILE = TEMP_DIR + std::string("/gm.xyz"); /**< name of gmt image file */
    const std::string HEADER_INFO_FILE = TEMP_DIR + std::string("/header_info.txt"); /**< name of header info data file */
    const std::string RUPTURE_DATA = TEMP_DIR + std::string("/rupture.dat"); /**< name of rupture data file */

    const std::string CALCULATED_MASK = TEMP_DIR + std::string("/calculated_mask.nc"); /**< name of mask nc file */
    const std::string STATION_LIST = TEMP_DIR + std::string("/stations.xy"); /**< name of stations data file */
    const std::string DIST_NC = TEMP_DIR + std::string("/dist.nc"); /**< name of distance nc file */

    //default Station_Param parameters
    const double DEFAULT_MIN_PERCENT = 50.0; /**< percentage of stations that must exceed the 
        minimum expected distance-dependent PGA ratio during noisy station identification */
    const size_t DEFAULT_NUM_NEIGHBORS = 5; /**< number of closest neighbors used to check 
        PGA ratio for noisy station identification */
    const double DEFAULT_MIN_RATIO = 2.0; /**< coefficient to calculate distance-dependent 
        PGA ratio */ 
    const double DEFAULT_MIN_RATIO_A = 25.0; /**< coefficient to calculate distance-dependent 
        PGA ratio */
    const double DEFAULT_MIN_RATIO_DIST = 10.0; /**< maximum distance for neighbours considered
        in distance-dependent PGA ratio check */
    const double DEFAULT_MIN_THRESH = 10.0;  /**< PGA threshold in cm/s/s used for remove noisy 
        stations and origin time calculation */

    const double EXCLUSION_FACTOR = 4.0; /**< factor for excluding stations from a trigger based
        on association with another Finder object, where station is within distance range based
        on template size and exclusion factor (sometimes we want this to be 2xINCLUSION_FACTOR) */
    const double INCLUSION_FACTOR = 2.0; /**< factor for including stations with a Finder object, 
        where station is within distance range based on template size and inclusion factor:
        1.0 means 1/2 template width used in process_image */

    const int DAYS = 7; /**< number of days passed before calculating a new mask */

	const double ASSOCIATION_TIME = 60.0; /**< max time that can pass and have stations still 
        associated with an event, if time is used as a factor */

	// config options that have been moved to finder_util.h
	const double TENSION = 0.6; /**< values 0.0-1.0, tension factor for gmt surface interpolation */
	const double RESIZE_FRACTION = 1.0; /**< values > 0.0, ideally 1.0, how to resize the image 
        and templates */
	const double MIN_LOG10PGA = -4.0; /**< log10(PGA) value border values in GMT grid are set to */
	const double MAX_MISFIT = 0.30; /**< double 0.0<value<1.0, maximum misfit to choose a 
        higher PGA threshold */
	const std::string INCLUDE_CONTINUOUS = "no"; /**< string "yes" or "no" for including a continous 
        template/image */
	const std::string DISPLAY_WINDOWS = "no"; /**< string "yes" or "no" for displaying the windows */

    const double SWAVE_VEL = 3.55; /**< S-wave velocity in km/s, used in determine_trigger and
        origin time calculation */

    const double POINT_SOURCE_LENGTH = 5.0; /**< max length for calculating same misfit as a 
                                            function of strike, units of km */
    const double MAX_LENGTH_TO_UPDATE_OTIME = 20.0; /**< maximum fault length to calculate origin 
                                                    time, units of km */

    // default parameters for computing origin time
    const double SWAVE_VELOCITY = SWAVE_VEL; /**< S-wave velocity in km/s (originally 3.55 km/s),
            using the value from finder_util.h to avoid multiple definitions */
    const double PWAVE_VELOCITY = 6.10; /**< P-wave velocity in km/s */
	const double ORIGIN_TIME_MIN_DIST = 50.0; /**< km beyond min distance between epicenter and a 
            station to use for origin time calculation */
//    const double GM_THRESHOLD = 1.0; 

    const double MAX_MAG_MISFIT = 0.7; /**< should have a value between 0.0 and 1.0 */
    const double MAX_LOC_MISFIT = 0.7; /**< should have a value between 0.0 and 1.0 */

    const double MAG_DEFAULT = 0.0; /**< default magnitude */
    const double MAG_UNCER_DEFAULT = 0.5; /**< default magnitude uncertainty */
    const double LAT_UNCER_DEFAULT = 0.25; /**< default latitude uncertainty */
    const double LON_UNCER_DEFAULT = 0.25; /**< default longitude uncertainty */
	const double ORIGIN_TIME_UNCER_DEFAULT = 2.515; /**< default origin time uncertainty */

	const double EXCEED_THRESH = 0.5; /**< threshold to exceed for a listing of stations 
                                    to be displayed in a report...must be above 0.0 */
    
	//for Chile
	const double NOISE_MEAN_PERCENT = 0.8; /**< */
	const double NOISE_HALF_RANGE_PERCENT = 0.05; /**< */
	const double PEAK_THRESH = 5.0; /**< */

}; // end of FiniteFault namespace

#endif // __finder_globals

// end of file: finder_globals.h
