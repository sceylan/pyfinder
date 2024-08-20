# -*- coding: utf-8 -*-
""" Configuration file for the pyfinder module. """
import os

def get_path_of_configuration():
    return os.path.dirname(os.path.abspath(__file__))

# Kahramanmaras, Turkey earthquake, 2023, Mw 7.8
KAHRAMANMARAS_TURKEY_EVENT_ID = "20230206_0000008"

# Norcia, Italy earthquake, 2016-10-30 06:40:18 UTC, Mw 6.5
NORCIA_ITALY_EVENT_ID = "20161030_0000029"

ESM_SHAKEMAP_SERVICE = "EMSC_ShakeMap"
RRSM_PEAK_MOTION_SERVICE = "RRSM_PeakMotion"
RRSM_SHAKEMAP_SERVICE = "RRSM_ShakeMap"
EMSC_FEELT_REPORT_SERVICE = "ESM_FeltReport"


pyfinderconfig = {
    "general": {
        # Web services ordered by priority
        "services": [ESM_SHAKEMAP_SERVICE, RRSM_PEAK_MOTION_SERVICE, EMSC_FEELT_REPORT_SERVICE],
        
        # The default test event id for the FinDer executable
        "test-event-id": NORCIA_ITALY_EVENT_ID,
    },

    # Logging configuration
    "logging": {
        # The default log level for the console logging
        "log-level": "INFO",

        # Overwrite the log file if it exists from previous runs. If False, 
        # the log file will be appended. If True, the previous logs will be lost.
        "overwrite-log-file": True,

        # Rotate the log file after reaching a certain size
        "rotate-log-file": True,
    },

    # Configuration for the FinDer executable
    "finder-executable": {
        # Path to the FinDer executable, including the executable name
        "path": "/usr/local/src/FinDer/finder_run",

        # The root path for outputs of all FinDer runs. A subfolder for
        # each run will be created under this path to store all the output.
        "output-root-folder": os.path.join(get_path_of_configuration(), "output"),

        # Path for logging the output of the FinDer executable
        "log-file-name": "pyfinder.log",

        # Path for all finder resources (templates, etc.)
        "path-for-finder-resources": "/usr/local/src/FinDer/config",

        # Path for GMT resources
        "path-for-gmt-resources": "/usr/local/src/FinDer/config/gmt_input",
    }
}


# Finder resources (templates, etc.) are stored in the following path
finder_resources = pyfinderconfig["finder-executable"]["path-for-finder-resources"]

# GMT resources are stored in the following path
gmt_resources = pyfinderconfig["finder-executable"]["path-for-gmt-resources"]

# If the GMT resources already includes gmt_input folder, remove it 
# and use the parent folder. It is added later in the configuration below.
if gmt_resources.endswith("gmt_input"):
    gmt_resources = os.path.dirname(gmt_resources)

# The template configuration for the FinDer executable (finder_file)
finder_file_comfig_template = {
    # <size_t> number of thresholds, list of their <double> PGA values
    "THRESHOLDS": "9 2.0 4.6 10.5 23.2 48.6 90.7 148.8 221.3 304.5",
    
    # <string> [local directory] for generic templates 
    "TEMPLATE_DIRECTORY": os.path.join(finder_resources, "Templates_PGA_20161020_CH2009_resolution_5"),
    
    # <string> [filename] list of generic + fault-specific templates IDs uploaded into FinDer
    "TEMPLATE_ID_FILE": os.path.join(finder_resources, "template.config"),
    
    # <double> delta degrees in strike search
    "D_DEG": "5.0",
    
    # <double> minimum strike angle to search over
    "MIN_DEG": "0.0",
    
    # <double> maximum strike angle to search over
    "MAX_DEG": "175.0",
    
    # <double> minimum rupture length to search over
    "MIN_LENGTH": "0.0",
    
    # <double> maximum rupture length to search over
    "MAX_LENGTH": "300.0",
    
    # <double> default depth for the earthquake source...this has no effect on FinDer calculation
    "DEFAULT_DEPTH": "10.0",
    
    # <double> default depth uncertainty for the earthquake source...no effect on calculation
    "DEFAULT_DEPTH_UNCER": "5.0",
    
    # <int> 1 for Wells and Coppersmith (e.g. CA) and 2 for Blaser (e.g. JP)
    "MAG_OPTION": "1",
    
    # <string> "complete" or "fast"
    "RUN_SPEED": "fast",
    
    # <string> [filename], "calculate" to generate a mask, "no_mask" if no mask
    "REGIONAL_MASK": os.path.join(gmt_resources, "gmt_input", "Switzerland_mask_20161012.nc"),
    
    # <double> [m] When calculating the mask, what is the max distance between stations
    "MASK_STATION_DISTANCE": "75.0",
    
    # <size_t> minimum number of stations needed to trigger FinDer, minimum of 1
    "MIN_TRIGGER_STATIONS": "2",
    
    # <double> the maximum radius between trigger stations
    "TRIGGER_RADIUS": "50.0",
    
    # <string> switch for using station specific triggering radius
    "USE_FIXED_TRIGRAD": "yes",
    
    # <double> max value (km) for station specific triggering radius
    "MAX_STATION_TRIGRAD": "150.0",
    
    # <size_t> number of networks, list of their <string> network codes
    "SECONDARY_NETWORKS": "2 CE CSN",
    
    # <double> minimum 1.0, minimum degrees border around image
    "BORDER_DEGREES": "1.0",
    
    # <size_t> values > 0, number of pixels that have to pass the threshold to use the threshold
    "IMAGE_PIXELS": "10",
    
    # <size_t> values > 0, number of pixels that have to pass to move up a threshold
    "MAX_IMAGE_PIXELS": "50",
    
    # <double> value > 0.0, the minimum likelihood value for an estimate
    "MIN_LIKELIHOOD_ESTIMATE_FOR_MESSAGE": "0.65",
    
    # <double> value > 0.0, related to the misfit calculations
    "SIGMA_LENGTH": "1.0",
    
    # <double> value > 0.0, related to the misfit calculations
    "SIGMA_AZIMUTH": "1.0",
    
    # <double> value > 0.0, related to the misfit calculations
    "SIGMA_LATLON": "1.0",
    
    # <size_t> the max # of ruptures FinDer outputs for generic templates, min of 1
    "MAX_RUPTURES": "30",
    
    # <string> "yes" or "no" for using the GMT 5.2.0 API
    "GMT_API_OPTION": "yes",
    
    # <string> "gmt" for GMT 5.0, "---" for blank in front of gmt commands
    "GMT_PREFIX": "---",
    
    # <string> "yes" or "no" for creating gmt_plots for offline testing
    "GMT_PLOT": "no",
    
    # <string> [filename]
    "COLOR_SCALE": os.path.join(gmt_resources, "gmt_input", "log_pga_wald.cpt"),
    
    # <string> [filename]
    "FAULT_DEFINITIONS": os.path.join(gmt_resources, "gmt_input", "jennings.xy"),
    
    # <string> [filename] station specific thresholds
    "STATION_CONFIG": "---",
    
    # <string> [foldername]
    "GMT_FOLDER": os.path.join(gmt_resources, "gmt_input"),
    
    # <string> [foldername] place to put temp and temp_dir folders
    "DATA_FOLDER": "<PATH>",
    
    # <double> distance in km between epicenter and fault, 
    # if exceeded new event id is created
    "EPI_FAULT_DIST_THRESH": "100.",  
    
    # <double> value below which regression may be carried out, above the threshold 
    # the original rupture-based FinDer magnitude will always be used. Set to a small 
    # value (e.g. -1.) to disable regression, or a high value (e.g. 10) to always use 
    # regression. Setting this value to ~5.5-6.0 should be appropriate, preferring an 
    # amplitude-based magnitude for smaller events and a rupture length based magnitude 
    # for finite fault events.
    "MAG_REGRESSION_THRESH": 5.5,

    "STOP_LENGTH_DECREASE_PC": "0.2",
    
    "RESTART_LENGTH_INCREASE_PC": "0.0001",
    
    "UNCERTAINTY_METHOD": "0",
    
    
}
