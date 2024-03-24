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

/////////////////////////////////////////////////////////////////////////
// Common Class Structures for the Finite Fault Data...Befores and Finder
/////////////////////////////////////////////////////////////////////////

#ifndef __finite_fault_h_
#define __finite_fault_h_


#include <time.h>       // time_t
#include <stdio.h>      // sprintf
#include <string>
#include <vector>
#include <algorithm>
#include <sstream>
#include <iostream>
#include <fstream> 
#include <stdlib.h>
#include <math.h>
#include <iomanip>
#include <map>
#include "finder_globals.h"

#define RCSID_finite_fault_h "$Id: finite_fault.h $"

using namespace std;

namespace FiniteFault {

class Finder_Parameters;

// define a generic collection class that knows how to stream it's contents
template <class T> 
class TemplateCollection : public std::vector<T> {
    typedef typename std::vector<T>::const_iterator Const_Iterator;
    public:

    friend std::ostream& operator<< (std::ostream& os, const std::vector<T>& in) {
        for (Const_Iterator iter = in.begin(); iter != in.end(); ++iter) {
            if (iter != in.begin() and in.size() > 0) os << " ";
            os << (*iter) << std::endl;
        }
        return os;
    }
    friend std::istream& operator>> (std::istream& is, std::vector<T>& out) {
        int count;
        is >> count;
        int read = 0;
        for (int idx = 0; idx < count; idx++) {
            T value;
            is >> value;
            out.push_back(value);
            read++;
        }
        return is;
    }
}; // class TemplateCollection


// three types of flags that are used to control the processing of a finder object
// if message == true, then a message is sent out
// if event_continue == true, then the earthquake is considered to be still active.  Will become false when the rupture decreases
// by a preset percentage
// if hold_object == true, we continue processing for the time window of the data in case a bigger event occurs.  Eventually,
// when hold_object == false the finder object associated with the earthquake is released
class Finder_Flags {
    protected:
        bool event_continue; /**< if true event is still active and processing/alerting continues*/
        bool hold_object; /**< if true continue to keep event alive */
        bool message; /**< if true event messages will be sent */
        bool first_template_match; /**< if true event has had a valid template match once */

    public:
        Finder_Flags(const bool event_continue = true, const bool hold_object = true, 
            const bool message = false, const bool first_template_match = true) : 
            event_continue(event_continue), hold_object(hold_object), message(message), 
            first_template_match(first_template_match) {}

        bool get_event_continue() const { return this->event_continue; }
        bool get_hold_object() const { return this->hold_object; }
        bool get_message() const { return this->message; }
        bool get_first_template_match() const { return this->first_template_match; }

        void set_event_continue(const bool event_continue) { this->event_continue = event_continue; }
        void set_hold_object(const bool hold_object) { this->hold_object = hold_object; }
        void set_message(const bool message) { this->message = message; }  
        void set_first_template_match(const bool first_template_match) { 
          this->first_template_match = first_template_match; 
        }
    
};  // class Finder_Flags


// these are the FinDer Config info that will want to pass to BEFORES on the fly if it gets updated.
class Finder_Config_Info {
	public:
		double dD; /**< strike resolution in degrees */
		double minD; /**< minimum strike in degrees */
		double maxD; /**< maximum strike in degrees */
		double sigma; /**< misfit/uncertainty */

		Finder_Config_Info(const double dD = NAN, const double minD = NAN, const double maxD = NAN, const double sigma = NAN) : dD(dD), minD(minD), maxD(maxD), sigma(sigma) {}
		
	friend std::ostream& operator<< (std::ostream& os, const Finder_Config_Info& in) {
    	os << " " << in.dD << " " << in.minD << " " << in.maxD << " " << in.sigma;
		return os;
	}
};  // class Finder_Config_Info


// this is the name of the template used in the FinDer solution.  Typically, it will be "generic" unless
// we use fault-specific templates.  BEFORES and FinDer will have copies of any fault-specific templates
// so only the template name needs to be passed as information
class Template_ID {
	public:
		std::string name; /**< template name */
		Template_ID(const string name = "generic") : name(name) {}

	friend std::ostream& operator<< (std::ostream& os, const Template_ID& in) {
    	os << " " << in.name;
		return os;
	}
};


class Template_ID_List : public TemplateCollection<Template_ID> {
}; // class Template_Table_List


class Coordinate {
    protected:  // protected means that subclasses can see it but the outside world cannot
        double lat; /**< latitude in decimal degrees */
        double lon; /**< longitude in decimal degrees */
    public:
       Coordinate(const double lat = NAN, const double lon = NAN) : lat(lat), lon(lon) {}
        double get_lat() const { return this->lat; }  
        double get_lon() const { return this->lon; }  
        std::vector<double> toVector() {
            std::vector<double> v;
            v.push_back(this->lon);
            v.push_back(this->lat);
            return v;
        }

        friend std::ostream& operator<< (std::ostream& os, const Coordinate& in) {
			ios_base::fmtflags old_flags = os.flags();
            os << setprecision(3) << fixed << in.lat << "/" << in.lon;
			os.flags(old_flags);
            return os;
        }
        friend std::istream& operator>> (std::istream& is, Coordinate& out) {
            is >> out.lat;
            is.ignore(1,'/'); is >> out.lon;
            return is;
        }
}; // class Coordinate



class Coordinate_List : public TemplateCollection<Coordinate>
{
}; // class Coordinate_List


class Coordinate3D {
	protected:
		double lat; /**< latitude in decimal degrees */
		double lon; /**< longitude in decimal degrees */
		double height; /**< height in metres */
	public:  
		Coordinate3D(const double lat = NAN, const double lon = NAN, const double height = NAN) 
			: lat(lat), lon(lon), height(height) {}
		double get_lat() const { return this->lat; }
		double get_lon() const { return this->lon; }
		double get_height() const { return this->height; }
		void set_values(const double lat, const double lon, const double height) {
        	this->lat = lat;
        	this->lon = lon;
        	this->height = height;
        }
	
		friend std::ostream& operator<< (std::ostream& os, const Coordinate3D& in) {
			ios_base::fmtflags old_flags = os.flags();
    		os << setprecision(3) << fixed << in.lat << "/" << in.lon << "/" << in.height;
			os.flags(old_flags);
            return os;
		}
 };  // class Coordinate3D


class Displacement {
	protected:
		double east; /**< east displacement in decimal degrees */
		double north; /**< north displacement in decimal degrees */
		double up; /**< up displacement in metres */
	public:  
		Displacement(const double east = NAN, const double north = NAN, const double up = NAN) 
			: east(east), north(north), up(up) {}
		double get_east() const { return this->east; }
		double get_north() const { return this->north; }
		double get_up() const { return this->up; }
		void set_values(const double east, const double north, const double up) {
        	this->east = east;
        	this->north = north;
        	this->up = up;
		}
	
		friend std::ostream& operator<< (std::ostream& os, const Displacement& in) {
			ios_base::fmtflags old_flags = os.flags();
    		os << setprecision(3) << fixed << in.east << "/" << in.north << "/" << in.up;
			os.flags(old_flags);
            return os;
		}
 };  // class Displacement


// This is filled out by the wrapper for BEFORES, which populates a list of active sncls in a certain time frame.
typedef std::vector<std::string> Sncl_List;

class Sncl_Data {
	protected:
		string sncl; /**< SNCL string */
		Displacement value; /**< 3 component displacement */
	public:
		Sncl_Data(const string sncl = "nan", const Displacement value = Displacement(NAN, NAN, NAN)) 
			: sncl(sncl), value(value) {}
		string get_sncl() const { return this->sncl; }
		Displacement get_value() const { return this->value; }

	friend std::ostream& operator<< (std::ostream& os, const Sncl_Data& in) {
    	os << in.sncl << " " << in.value;
         return os;
	}
 };  // class Scnl_Data
	
class Sncl_Data_List : public TemplateCollection<Sncl_Data> {
}; // class Sncl_Data_List


// Data class that is filled out when reading a geodetic channel file for BEFORES.  One Channel_Data object
// per line of input from the channel file.
class Channel_Data {
	protected:
		std::string name; /**< station name */
		std::string network; /**< network code */
		std::string channel; /**< channel code */
		std::string location_code; /**< location code */
		std::string base_name; /**< base station name */
		Coordinate3D base_location; /**< base station location */
		std::string ref_name; /**< reference station name */
		Coordinate3D ref_location; /**< reference station location */
		std::string sol_type; /**< solution type */
		size_t sample_rate; /**< channel sampling rate */
		size_t gain; /**< channel gain */
		std::string units; /**< channel gain units */

	public:
		Channel_Data(const string name = "nan", const string network = "nan", const string channel = "nan", const string location_code = "nan", const string base_name = "nan", const Coordinate3D base_location = Coordinate3D(NAN,NAN,NAN), const string ref_name = "nan", const Coordinate3D ref_location = Coordinate3D(NAN,NAN,NAN), const string sol_type = "nan", const size_t sample_rate = 1, const size_t gain = 1000, const string units = "nan")
			: name(name), network(network), channel(channel), location_code(location_code), base_name(base_name), base_location(base_location), ref_name(ref_name), ref_location(ref_location), sol_type(sol_type), sample_rate(sample_rate), gain(gain), units(units) {}        
		std::string get_name() const { return this->name; }
        std::string get_network() const { return this->network; }
        std::string get_channel() const { return this->channel; }
        std::string get_location_code() const { return this->location_code; }
		std::string get_base_name() const { return this->base_name; }
        Coordinate3D get_base_location() const { return this->base_location; }
		std::string get_ref_name() const { return this->ref_name; }
        Coordinate3D get_ref_location() const { return this->ref_location; }
		std::string get_sol_type() const { return this->sol_type; }
		size_t get_sample_rate() const { return this->sample_rate; }
		size_t get_gain() const { return this->gain; }
		std::string get_units() const { return this->units; }

       friend std::ostream& operator<< (std::ostream& os, const Channel_Data & in) {
            os  << in.network << "." << in.name << "." << in.channel << "." << in.location_code << " "
               << "-- "
               << in.base_name << " " << in.base_location << " "
			   << in.ref_name << " " << in.ref_location << " "
			   << in.sol_type << " " 
			   << in.sample_rate << " " 
			   << in.gain << " "
			   << in.units;
        return os;
        }
}; //class Channel_Data

class Channel_Data_List : public TemplateCollection<Channel_Data> {
}; // class Channel_Data_List


// Data class for data used by FinDer 2...it breaks up the sncl into the four components
// has a lat/lon for location, value for the PGA, timestamp, include for good vs. noisy station, 
// and event_id_list for which events the station is included in for solutions.
class PGA_Data {
    protected:
        std::string name; /**< station name */
        std::string network; /**< network code */
        std::string channel; /**< channel code */
        std::string location_code; /**< location code */
        Coordinate location; /**< station location */
        double value; /**< PGA value in cm/s/s */
        double timestamp; /**< timestamp for PGA value */
        bool include; /**< "true" if it is a good station, "false" if it is a noisy station */
        bool trigger_flag; /**< "true" if station was counted as a valid trigger observation */
        TemplateCollection<long> event_id_list; /**< list of event ids with which this station /
             measurement is associated */
    public:
        PGA_Data(const string name = "nan", const string network = "nan", const string channel = "nan", 
            const string location_code = "nan", const Coordinate location = Coordinate(NAN,NAN), 
            const double value = NAN, const double timestamp = NAN, const bool include = true)
            : name(name), network(network), channel(channel), location_code(location_code), 
            location(location), value(value), timestamp(timestamp), include(include) { 
            trigger_flag = false;
        }
        std::string get_name() const { return this->name; }
        std::string get_network() const { return this->network; }
        std::string get_channel() const { return this->channel; }
        std::string get_location_code() const { return this->location_code; }
        Coordinate get_location() const { return this->location; }
        double get_value() const { return this->value; }
        double get_timestamp() const { return this->timestamp; }
        bool get_include() const { return this->include; }
        bool get_trigger_flag() const { return this->trigger_flag; }
        TemplateCollection<long> get_event_id_list() const { return this->event_id_list; }

        void update_value(const double value, const double timestamp)
        {
            this->value = value;
            this->timestamp = timestamp;
        }

        void set_include(const bool include) { this->include = include; }
        void set_trigger_flag(const bool bTrig) { this->trigger_flag = bTrig; }
        void set_event_id_list(const long event_id) { this->event_id_list.push_back(event_id); }
        void resize_event_id_list(const size_t Nid) { this->event_id_list.assign(Nid,0)
; }
        size_t size_event_id_list() const { return this->event_id_list.size(); }

       friend std::ostream& operator<< (std::ostream& os, const PGA_Data & in) {
			ios_base::fmtflags old_flags = os.flags();
            os  << in.network << "." << in.name << "." << in.channel << "." << in.location_code << " "
               << in.location << " "
               << "-- "
               << in.value << " "
               << setprecision(3) << fixed << in.timestamp
               << " include = " 
               << in.include
               << ", station id = " 
               << in.event_id_list;
			os.flags(old_flags);
        return os;
        }

};  // class PGA_Data


class PGA_Data_List : public TemplateCollection<PGA_Data> {
}; // class PGA_Data_List


// The centroid of the rupture could very well be different from the epicenter if
// you have a unilateral rupture for example.
class Finder_Centroid : public Coordinate {
    public:
        Finder_Centroid(const double lat = NAN, const double lon = NAN)
            : Coordinate(lat, lon) {}
}; // class Finder_Centroid


/** Extending to 3D **/
class Finder_Rupture : public Coordinate {
    protected:  
        double depth; /**< depth in km */
    public:
        Finder_Rupture(const double lat = NAN, const double lon = NAN, const double depth = NAN) : Coordinate(lat, lon), depth(depth) {}
        double get_depth() const { return this->depth; }

        friend std::ostream& operator<< (std::ostream& os, const Finder_Rupture& in) {
			ios_base::fmtflags old_flags = os.flags();
            os << setprecision(3) << fixed << in.lat << "/" << in.lon << "/" << in.depth;
			os.flags(old_flags);
            return os;
        }
        friend std::istream& operator>> (std::istream& is, Finder_Rupture& out) {
            is >> out.lat;
            is.ignore(1,'/'); is >> out.lon;
            is.ignore(1,'/'); is >> out.depth;
            return is;
        }
};  // class Finder_Rupture


class Finder_Rupture_List : public TemplateCollection<Finder_Rupture> {
};  // class Finder_Rupture_List


// This is for the correlation values which range from 0 to 1.0.  Higher corr values indicate better fits to data
class Correlation {
    protected:  
        double value; /**< value for which correlation is calculated */
        double corr; /**< correlation value */
    public:
        Correlation(const double value = NAN, const double corr = NAN) 
            : value(value), corr(corr) {}
        double get_value() const { return this->value; }  
        double get_corr() const { return this->corr; }  

        friend std::ostream& operator<< (std::ostream& os, const Correlation& in) {
			ios_base::fmtflags old_flags = os.flags();
            os << " " << setprecision(3) << fixed << in.value << "," << in.corr;
			os.flags(old_flags);
            return os;
        }
}; // class Correlation


class Correlation_List : public TemplateCollection<Correlation> {
}; // class Correlation_List


// This is for misfit values...typically, we will use normalized value from 0.0 to 1.0.  
// Lower values of misf indicate better fit to data.
class Misfit {
    protected:  
        double value; /**< value for which misfit is calculated */
        double misf; /**< misfit value */
    public:
        Misfit(const double value = NAN, const double misf = NAN) 
            : value(value), misf(misf) {}
        double get_value() const { return this->value; }  
        double get_misf() const { return this->misf; }  

        friend std::ostream& operator<< (std::ostream& os, const Misfit& in) {
			ios_base::fmtflags old_flags = os.flags();
            os << setprecision(3) << fixed << in.value << "," << in.misf;
			os.flags(old_flags);
            return os;
        }
        friend std::istream& operator>> (std::istream& is, Misfit& out) {
            is >> out.value;
            is.ignore(1,'/'); is >> out.misf;
            return is;
        }
}; // class Misfit


class Misfit_List : public TemplateCollection<Misfit> {
}; // class Misfit_List


class Misfit2D {
    protected:
        Coordinate location; /**< misfit location */
        double misf; /**< misfit value */
    public:
        Misfit2D(const double lat = NAN, const double lon = NAN, const double misf = NAN)
            : location(lat, lon), misf(misf) {}
        Coordinate get_location() const { return this->location; }
        double get_misf() const { return this->misf; }

        friend std::ostream& operator<< (std::ostream& os, const Misfit2D& in) {
                        ios_base::fmtflags old_flags = os.flags();
            os << setprecision(3) << fixed << in.location << "," << scientific << in.misf;
                        os.flags(old_flags);
            return os;
        }
        friend std::istream& operator>> (std::istream& is, Misfit2D& out) {
	    is >> out.location;
            is.ignore(1,'/'); is >> out.misf;
            return is;
        }
}; // class Misfit2D


class Misfit2D_List : public TemplateCollection<Misfit2D> {
}; // class Misfit2D_List


// these are for loglikelihood values where higher values of llk indicate a better fit to data
class LogLikelihood {
	protected:
		double value; /**< value for which log likelihood is calculated */
		double llk; /**< log likelihood value */
	public:
		LogLikelihood(const double value = NAN, const double llk = NAN)
			: value(value), llk(llk) {}
		double get_value() const { return this->value; }
		double get_llk() const { return this->llk; }

        friend std::ostream& operator<< (std::ostream& os, const LogLikelihood& in) {
			ios_base::fmtflags old_flags = os.flags();
            os << setprecision(3) << fixed << in.value << "," << in.llk;
			os.flags(old_flags);
            return os;
        }
}; // class LogLikelihood


class LogLikelihood_List : public TemplateCollection<LogLikelihood> {
}; // class LogLikelihood_List

class LogLikelihood2D {
    protected:
        Coordinate location; /**< location as lat,lon coordinate pair */
	    double llk; /**< log likelihood value for location */
    public:
        LogLikelihood2D(const double lat = NAN, const double lon = NAN, const double llk = NAN)
            : location(lat, lon), llk(llk) {}
        Coordinate get_location() const { return this->location; }
        double get_llk() const { return this->llk; }

        friend std::ostream& operator<< (std::ostream& os, const LogLikelihood2D& in) {
                        ios_base::fmtflags old_flags = os.flags();
            os << setprecision(3) << fixed << in.location << "," << scientific << in.llk;
                        os.flags(old_flags);
            return os;
        }
        friend std::istream& operator>> (std::istream& is, LogLikelihood2D& out) {
	    is >> out.location;
            is.ignore(1,'/'); is >> out.llk;
            return is;
        }
}; // class LogLikelihood2D


class LogLikelihood2D_List : public TemplateCollection<LogLikelihood2D> {
}; // class LogLikelihood2D_List


class Finder_Azimuth : public Misfit {
    public:
        Finder_Azimuth(const double azimuth = NAN, const double misf = NAN)
            : Misfit(azimuth, misf) {}
};  // class Finder_Azimuth


// list of misfit values associated with each azimuth that is tested for a FinDer solution
class Finder_Azimuth_List : public TemplateCollection<Finder_Azimuth> {
};  // class Finder_Azimuth_List


class Finder_Azimuth_LLK : public LogLikelihood {
    public:
        Finder_Azimuth_LLK(const double azimuth = NAN, const double llk = NAN)
            : LogLikelihood(azimuth, llk) {}
};  // class Finder_Azimuth_LLK

class Finder_Azimuth_LLK_List : public TemplateCollection<Finder_Azimuth_LLK> {
};  // class Finder_Azimuth_LLK_List


class Finder_Length : public Misfit {
    public:
        Finder_Length(const double length = NAN, const double misf = NAN)
            : Misfit(length, misf) {}
};  // class Finder_Length


// list of misfit values associated with each length that is tested for a FinDer solution
class Finder_Length_List : public TemplateCollection<Finder_Length> {
};  // class Finder_Length_List


class Finder_Length_LLK : public LogLikelihood {
    public:
	Finder_Length_LLK(const double length = NAN, const double llk = NAN)
            : LogLikelihood(length, llk) {}
};  // class Finder_Length_LLK

class Finder_Length_LLK_List : public TemplateCollection<Finder_Length_LLK> {
};  // class Finder_Length_LLK_List


// define a Core_Info class for Befores...contains all the needed values from the DM Core_Info message
class Core_Info {
    public:
        long id; /**< event id */
        double mag; /**< event magnitude */
        double lat; /**< event epicenter latitude */
        double lon; /**< event epicenter longitude */
        double origin_time; /**< event origin time */

    Core_Info() : id(0), mag(NAN), lat(NAN), lon(NAN), origin_time(NAN) {}

    Core_Info(const long id, const double mag, const double lat, const double lon, const double origin_time) 
		: id(id), mag(mag), lat(lat), lon(lon), origin_time(origin_time) {}

    Core_Info(const Core_Info& info) {
        *this = info;
    } // CoreInfo copy ctor

    long   get_id() const  { return this->id; }
    double get_mag() const { return this->mag; }
    double get_lat() const { return this->lat; }
    double get_lon() const { return this->lon; }
    double get_origin_time() const { return this->origin_time; }

    friend std::ostream& operator<< (std::ostream& os, const Core_Info& in) {
		ios_base::fmtflags old_flags = os.flags();
        os << "id=" << in.id << setprecision(3) << fixed << ",mag=" << in.mag << ",lat=" << in.lat << ",lon=" << in.lon
            << ",origin_time="<<  in.origin_time;
        os.flags(old_flags);
        return os;
    }

    friend std::istream& operator>> (std::istream& is, Core_Info& out) {
        is.ignore(20,'='); is >> out.id;
        is.ignore(20,'='); is >> out.mag;
        is.ignore(20,'='); is >> out.lat;
        is.ignore(20,'='); is >> out.lon;
        is.ignore(20,'='); is >> out.origin_time;
        return is;
    }
private:

}; // class Core_Info


// Putting all the FinDer needed messages together into a single class for BEFORES
class Finder_Info : public Core_Info {

	std::string template_id; /**< finder object template ID */
    Finder_Centroid finder_centroid; /**< finder rupture centroid */
	Finder_Rupture_List finder_rupture_list; /**< finder rupture vertices */
	Finder_Length_List finder_length_list; /**< finder length list */
	Finder_Azimuth_List finder_azimuth_list; /**< finder strike list */

    public:

        Finder_Info() : Core_Info() {}

        Finder_Info(const long id, const double mag, const double lat, const double lon, const double origin_time) :
				Core_Info(id, mag, lat, lon, origin_time) {}
 
       	Finder_Info(const Finder_Info& finder_info) : Core_Info() {
			*this = finder_info;
	   	}

		void set_template_id(const string template_id) { this->template_id = template_id; }
		void set_finder_centroid(const Finder_Centroid finder_centroid) { this->finder_centroid = finder_centroid; }
		void set_finder_rupture_list(const Finder_Rupture_List finder_rupture_list) { 
            this->finder_rupture_list.resize(0);
            this->finder_rupture_list = finder_rupture_list; 
        }
		void set_finder_length_list(const Finder_Length_List finder_length_list) { 
            this->finder_length_list.resize(0);
            this->finder_length_list = finder_length_list; 
        }
		void set_finder_azimuth_list(const Finder_Azimuth_List finder_azimuth_list) { 
            this->finder_azimuth_list.resize(0);
            this->finder_azimuth_list = finder_azimuth_list; 
        }

		std::string get_template_id() const { return this->template_id; }
		Finder_Centroid get_finder_centroid() const { return this->finder_centroid; }
		Finder_Rupture_List get_finder_rupture_list() const { return this->finder_rupture_list; }
		Finder_Length_List get_finder_length_list() const { return this->finder_length_list; }
		Finder_Azimuth_List get_finder_azimuth_list() const { return this->finder_azimuth_list; }

       friend std::ostream& operator<< (std::ostream& os, const Finder_Info& in) {
            os << (Core_Info&)in << std::endl;
            os << "template_id=" << in.template_id << std::endl;
            os << "finder_centroid=" << in.finder_centroid << std::endl;
            os << "finder_rupture_list=" << in.finder_rupture_list.size() << std::endl << 
                in.finder_rupture_list << std::endl;
            os << "finder_length_list=" << in.finder_length_list.size() << std::endl << 
                in.finder_length_list << std::endl;
            os << "finder_azimuth_list=" << in.finder_azimuth_list.size() << std::endl << 
                in.finder_azimuth_list;
        return os;
        }

       friend std::istream& operator>> (std::istream& is, Finder_Info& out) {
           is >> (Core_Info&)out;
           is.ignore(50,'='); is >> out.template_id;
           is.ignore(50,'='); is >> out.finder_centroid;
           is.ignore(50,'='); is >> out.finder_rupture_list;
           is.ignore(50,'='); is >> out.finder_length_list;
           is.ignore(50,'='); is >> out.finder_azimuth_list;
           return is;
       }
}; // class Finder_Info


class Befores_Rupture {
    protected:
        Coordinate coordinate_start; /**< rupture start coordinates */
        Coordinate coordinate_end; /**< rupture end coordinates */
        double slip; /**< rupture slip */
    public:
        Befores_Rupture(const double lat_start = NAN, const double lon_start = NAN, const double lat_end = NAN, const double lon_end = NAN, const double slip = NAN)
            : coordinate_start(lat_start, lon_start), coordinate_end(lat_end, lon_end), slip(slip) {}
        Coordinate get_coordinate_start() const { return this->coordinate_start; }
        Coordinate get_coordinate_end() const { return this->coordinate_end; }
        double get_slip() const { return this->slip; }
 
       friend std::ostream& operator<< (std::ostream& os, const Befores_Rupture & in) {
            os << " lat/lon start = " << in.coordinate_start << ", lat/lon end = " << in.coordinate_end << ", slip = " << in.slip; 
        return os;
        }

};  // class Befores_Rupture


// A description of rupture coordinates output by BEFORES in a format similar to a GPSlip message to the DM
class Befores_Rupture_List : public TemplateCollection<Befores_Rupture> {
}; // class Befores_Rupture_List


class Station_Data {
	protected:
		std::string network; /**< station network code */
		Coordinate3D location; /**< station location (only updated maybe once a week) */
		bool include; /**< flag on whether station should be included */
		std::string units; /**< station measurement units */
	public:
		Station_Data(const string network = "nan", 
			const Coordinate3D location = Coordinate3D(NAN,NAN,NAN), 
 			const bool include = true, const string units = "m") 
 			: network(network), location(location), include(include), units(units) {}
 		std::string get_network() const { return this->network; }
 		Coordinate3D get_location() const { return this->location; }
 		bool get_include() const { return this->include; }
 		std::string get_units() const { return this->units; }
 		
 		friend std::ostream& operator<< (std::ostream& os, const Station_Data& in) {
    		os << in.network << ", " << in.location << ", " << in.include << "," 
    		<< in.units;
            return os;
        }
};  // end of Station_Data class

// Create a map where the keyword string is the station name and it is associated with a Station_Data object
// to fill in extra information like network, location, include, and the units uses.  Include indicates whether
// or not it is a predetermined noisy stations
typedef map<std::string, Station_Data> Station_Map;


class Vector3D {
    protected:  // protected means that subclasses can see it but the outside world cannot
        double E; /**< east component of vector (positive east) */
        double N; /**< north component of vector (positive north) */
        double Up; /**< vertical component of vector (positive up) */
    public:
       Vector3D(const double E = NAN, const double N = NAN, const double Up = NAN) 
       	: E(E), N(N), Up(Up) {}
        double get_E() const { return this->E; }  
        double get_N() const { return this->N; }
        double get_Up() const { return this->Up; }
        void set_values(const double E, const double N, const double Up) {
        	this->E = E;
        	this->N = N;
        	this->Up = Up;
        }

        friend std::ostream& operator<< (std::ostream& os, const Vector3D& in) {
            os << in.E << "/" << in.N << "/" << in.Up;
            return os;
        }
}; // class Vector2D


class Geodetic_Data {
 	protected:
		Coordinate3D location; /**< location of data point */
		Vector3D displacement; /**< displacement vector of data point */
 		double timestamp; /**< timestamp of data point */
 	public:
 		Geodetic_Data(const Coordinate3D location = Coordinate3D(NAN,NAN,NAN),
 			const Vector3D displacement = Vector3D(NAN,NAN,NAN), const double timestamp = NAN)
 			: location(location), displacement(displacement), timestamp(timestamp) {}
 		Coordinate3D get_location() const { return this->location; }
 		Vector3D get_displacement() const { return this->displacement; }
 		double get_timestamp() const { return this->timestamp; }
 		
 		void set_values(const Coordinate3D location, const Vector3D, const double timestamp) {
 			this->location = location;
 			this->displacement = displacement;
 			this->timestamp = timestamp;
 		}
 		
 		friend std::ostream& operator<< (std::ostream& os, const Geodetic_Data& in) {
			ios_base::fmtflags old_flags = os.flags();
    		os << in.location << ", " << in.displacement << ", " 
    			<< setprecision(3) << fixed << in.timestamp;
			os.flags(old_flags);
            return os;
        }
 }; // Geodetic_Data class
// Once BEFORES receives a trigger, we begin getting data out of the ring buffer...we may have
// to go backwards to pick up the zero time position.  Then calculate the displacements relative 
// to the zero time position.  The results of the calculations will then be the message 
// sent to the BEFORES algorithm.

 typedef map<std::string, Geodetic_Data> Geodetic_Data_Map;

 		
// class Geodetic_Data_List : public TemplateCollection<circular_buffer<Geodetic_Data> >
// {
// }; // class PGA_Data_List 		


class Seismic_Data {
    protected:
    	Coordinate location; /**< location of seismic data point */
        double value; /**< value of seismic data point */
        double timestamp; /**< timestamp of seismic data point */
    public:
        Seismic_Data(const Coordinate location = Coordinate(NAN,NAN), const double value = NAN, const double timestamp = NAN)
            : location(location), value(value), timestamp(timestamp) {}
        Coordinate get_location() const { return this->location; }
        double get_value() const { return this->value; }
        double get_timestamp() const { return this->timestamp; }

        void set_values(const Coordinate location, const double value, const double timestamp)
        {
        	this->location = location;
            this->value = value;
            this->timestamp = timestamp;
        }

       friend std::ostream& operator<< (std::ostream& os, const Seismic_Data & in) {
			ios_base::fmtflags old_flags = os.flags();
            os  << in.location << "," << in.value << ", " << setprecision(3)<< fixed << in.timestamp;
			os.flags(old_flags);
        	return os;
        }

};  // class Seismic_Data

    typedef map<std::string, Seismic_Data> Seismic_Data_Map;

// class Seismic_Data_List : public TemplateCollection<circular_buffer<Seismic_Data> >
// {
// }; // class Seismic_Data_List


class Station_Param {
  public:
    
    double min_percent; /**< percentage of stations that must exceed the minimum expected 
        distance-dependent PGA ratio during noisy station identifcation*/
    size_t num_neighbors; /**< number of closest neigbors used to check PGA ratio for noisy
        station identification */
    double min_ratio; /**< coefficient to calculate distance-dependent PGA ratio */
    double min_ratio_a; /**< coefficient to calculate distance-dependent PGA ratio */
    double min_ratio_dist; /**< maximum distance for neighbours considered in 
        distance-dependent PGA ratio check */
}; //Station_Param


/** \class Finder_Internal
 * \brief Contains most of the parameters describing an earthquake source that must
 * be saved from one timestep of FinDer processing
 * */
class Finder_Internal {
  private:
    std::string template_id; /**< identifier for template */
    size_t Nstat_used; /**< number of stations above PGA threshold used in finder */
    // core_info
    double mag; /**< earthquake magnitude */
    double mag_FD; /**< magnitude determined by Finder rupture fitting process */
    double mag_reg; /**< magnitude determined by regression of amplitudes */
    double mag_uncer; /**< magnitude uncertainty */
    std::vector<double> mag_uncer_vector; /**< magnitude uncertainty for both dimensions */
    Coordinate event_epicenter; /**< event epicenter */
    Coordinate epicenter_uncer; /**< event epicenter uncertainty */
    double origin_time; /**< origin time in UNIX seconds */
    double likelihood_estimate; /**< rupture likelihood estimate */
    std::vector<double> misfit; /**< rupture misfit to select between template sets */
    // rupture
    double rupture_length; /**< Event rupture length */
    double rupture_azimuth; /**< Event rupture azimuth */
    double azimuth_uncer; /**< azimuth uncertainty */
    Finder_Centroid finder_centroid; /**< finder centroid */
    Finder_Centroid finder_centroid_uncer; /**< finder centroid uncertainty */
    Finder_Rupture_List finder_rupture_list; /**< rupture vertices list */
    Finder_Azimuth_List finder_azimuth_list; /**< rupture azimuth list */
    Finder_Length_List finder_length_list; /**< rupture length list */
    Finder_Azimuth_LLK_List finder_azimuth_llk_list; /**< azimuth likelihood list */
    Finder_Length_LLK_List finder_length_llk_list; /**< length likelihood list */
    LogLikelihood2D_List centroid_lat_pdf; /**< PDF of centroid latitude */
    LogLikelihood2D_List centroid_lon_pdf; /**< PDF of centroid longitude */

  public:
    std::string get_template_id() const { return this->template_id; }
    size_t get_Nstat_used() const { return this->Nstat_used; }
    double get_mag() const { return this->mag; }
    double get_mag_FD() const { return this->mag_FD; }
    double get_mag_reg() const { return this->mag_reg; }
    double get_mag_uncer() const { return this->mag_uncer; }
    std::vector<double> get_mag_uncer_vector() const { return this->mag_uncer_vector; }
    Coordinate get_epicenter() const { return this->event_epicenter; }
    Coordinate get_epicenter_uncer() const { return this->epicenter_uncer; }
    double get_origin_time() const { return this->origin_time; }
    double get_likelihood_estimate() const { return this->likelihood_estimate; }
    double get_misfit(size_t i) const { return this->misfit[i]; }
    double get_rupture_length() const { return this->rupture_length; }
    double get_rupture_azimuth() const { return this->rupture_azimuth; }
    double get_azimuth_uncer() const { return this->azimuth_uncer; }
    Finder_Centroid get_finder_centroid() const { return this->finder_centroid; }
    Finder_Centroid get_finder_centroid_uncer() const { return this->finder_centroid_uncer; }
    Finder_Rupture_List get_finder_rupture_list() const { return this->finder_rupture_list; }
    Finder_Azimuth_List get_finder_azimuth_list() const { return this->finder_azimuth_list; }
    Finder_Length_List get_finder_length_list() const { return this->finder_length_list; }
    Finder_Azimuth_LLK_List get_finder_azimuth_llk_list() const
        { return this->finder_azimuth_llk_list; }
    Finder_Length_LLK_List get_finder_length_llk_list() const
        { return this->finder_length_llk_list; }
    LogLikelihood2D_List get_centroid_lat_pdf() const { return this->centroid_lat_pdf; }
    LogLikelihood2D_List get_centroid_lon_pdf() const { return this->centroid_lon_pdf; }

    void set_template_id(const std::string template_id) { this->template_id = template_id; }
    void set_Nstat_used(const size_t Nstat_used) { this->Nstat_used = Nstat_used; }
    void set_mag(const double mag_new) { this->mag = mag_new; }
    void set_mag_FD(const double mag_FD_new) { this->mag_FD = mag_FD_new; }
    void set_mag_reg(const double mag_reg) { this->mag_reg = mag_reg; }
    void set_mag_uncer(const double mag_uncer_new) { this->mag_uncer = mag_uncer_new; }
    void set_mag_uncer_vector(const std::vector<double> mag_uncer_vec_new) 
        { this->mag_uncer_vector = mag_uncer_vec_new; }
    void set_mag_uncer_vector_at(const size_t ind, double val)
        { mag_uncer_vector[ind] = val; }
    void set_epicenter(const double event_lat_new, const double event_lon_new) 
        { this->event_epicenter = Coordinate(event_lat_new, event_lon_new); }
    void set_epicenter_uncer(const double lat_uncer, const double lon_uncer) 
        { this->epicenter_uncer = Coordinate(lat_uncer, lon_uncer); }
    void set_origin_time(const double origin_time_new) { this->origin_time = origin_time_new; }
    void set_likelihood_estimate(const double likelihood_estimate_new)
        { this->likelihood_estimate = likelihood_estimate_new; }
    void set_misfit(const size_t i, const double misfit_new)
        { this->misfit[i] = misfit_new; }
    void set_rupture_length(const double best_length) { this->rupture_length = best_length; }
    void set_rupture_azimuth(const double best_azimuth) { this->rupture_azimuth = best_azimuth; }
    void set_azimuth_uncer(const double azimuth_uncer) { this->azimuth_uncer = azimuth_uncer; }
    void set_finder_centroid(const double lat, const double lon)
        { this->finder_centroid = Finder_Centroid(lat, lon); }
    void set_finder_centroid_uncer(const double lat, const double lon)
        { this->finder_centroid_uncer = Finder_Centroid(lat, lon); }
    void set_finder_rupture_list(const Finder_Rupture_List finder_rupture_list_new) {
        this->finder_rupture_list.resize(0);
        this->finder_rupture_list = finder_rupture_list_new; 
    }
    void set_finder_azimuth_list(const Finder_Azimuth_List finder_azimuth_list_new) { 
        this->finder_azimuth_list.resize(0);
        this->finder_azimuth_list = finder_azimuth_list_new; 
    }
    void set_finder_length_list(const Finder_Length_List finder_length_list_new) {
        this->finder_length_list.resize(0);
        this->finder_length_list = finder_length_list_new; 
    }
    void set_finder_azimuth_llk_list(const Finder_Azimuth_LLK_List finder_azimuth_llk_list_new) {
        this->finder_azimuth_llk_list.resize(0);
        this->finder_azimuth_llk_list = finder_azimuth_llk_list_new; 
    }
    void set_finder_length_llk_list(const Finder_Length_LLK_List finder_length_llk_list_new) {
        this->finder_length_llk_list.resize(0);
        this->finder_length_llk_list = finder_length_llk_list_new; 
    }
    void set_centroid_lat_pdf(const LogLikelihood2D_List centroid_lat_pdf) { 
        this->centroid_lat_pdf.resize(0);
        this->centroid_lat_pdf = centroid_lat_pdf; 
    }
    void set_centroid_lon_pdf(const LogLikelihood2D_List centroid_lon_pdf) { 
        this->centroid_lon_pdf.resize(0);
        this->centroid_lon_pdf = centroid_lon_pdf; 
    }

    void resize_rupture_list(int size) { finder_rupture_list.resize(size); }
    void resize_azimuth_list(int size) { finder_azimuth_list.resize(size); }
    void resize_length_list(int size) { finder_length_list.resize(size); }
    void resize_azimuth_llk_list(int size) { finder_azimuth_llk_list.resize(size); }
    void resize_length_llk_list(int size) { finder_length_llk_list.resize(size); }
    void resize_centroid_lat_pdf(int size) { centroid_lat_pdf.resize(size); }
    void resize_centroid_lon_pdf(int size) { centroid_lon_pdf.resize(size); }
    void resize_misfit(size_t size, double val) { this->misfit.resize(size, val); }

    void azimuth_list_push_back(Finder_Azimuth value) {
        this->finder_azimuth_list.push_back(value);
    }
    void length_list_push_back(Finder_Length value) {
        this->finder_length_list.push_back(value);
    }
    void azimuth_llk_list_push_back(Finder_Azimuth_LLK value) {
        this->finder_azimuth_llk_list.push_back(value);
    }
    void length_llk_list_push_back(Finder_Length_LLK value) {
        this->finder_length_llk_list.push_back(value);
    }
    void centroid_lat_pdf_push_back(LogLikelihood2D value) {
        this->centroid_lat_pdf.push_back(value);
    }
    void centroid_lon_pdf_push_back(LogLikelihood2D value) {
        this->centroid_lon_pdf.push_back(value);
    }

    friend ostream& operator<< (ostream& os, Finder_Internal& f) {
        os << f.finder_centroid.get_lat() << "," << f.finder_centroid.get_lon() << "," << f.rupture_length;
        return os;
    }

    bool copyFrom(Finder_Internal* f) {
        mag = f->get_mag();
        mag_FD = f->get_mag_FD();
        mag_reg = f->get_mag_reg();
        mag_uncer = f->get_mag_uncer();
        set_epicenter(f->get_epicenter().get_lat(), f->get_epicenter().get_lon());
        set_epicenter_uncer(f->get_epicenter_uncer().get_lat(), f->get_epicenter_uncer().get_lon());
        set_origin_time(f->get_origin_time());
        set_likelihood_estimate(f->get_likelihood_estimate());
        set_rupture_length(f->get_rupture_length());
        set_rupture_azimuth(f->get_rupture_azimuth());
		set_azimuth_uncer(f->get_azimuth_uncer());
		set_Nstat_used(f->get_Nstat_used());

		set_template_id(f->get_template_id());
        set_finder_centroid(f->get_finder_centroid().get_lat(), f->get_finder_centroid().get_lon());
        set_finder_centroid_uncer(f->get_finder_centroid_uncer().get_lat(), f->get_finder_centroid_uncer().get_lon());
        set_finder_rupture_list(f->get_finder_rupture_list());
        set_finder_azimuth_list(f->get_finder_azimuth_list());
        set_finder_length_list(f->get_finder_length_list());
        set_finder_azimuth_llk_list(f->get_finder_azimuth_llk_list());
        set_finder_length_llk_list(f->get_finder_length_llk_list());
        set_centroid_lat_pdf(f->get_centroid_lat_pdf());
        set_centroid_lon_pdf(f->get_centroid_lon_pdf());

        return true;
    }

    void init() {
        set_likelihood_estimate(0.0);
        set_rupture_length(0.0);
        set_rupture_azimuth(0.0);
	    set_azimuth_uncer(0.0);
        resize_rupture_list(0);
        resize_rupture_list(0);
        resize_azimuth_list(0);
        resize_length_list(0);  
        resize_azimuth_llk_list(0);
        resize_length_llk_list(0);
        resize_centroid_lat_pdf(0);
        resize_centroid_lon_pdf(0);
    };

    void set_defaults() {
        set_epicenter_uncer(LAT_UNCER_DEFAULT, LON_UNCER_DEFAULT);
        set_mag(MAG_DEFAULT);
        set_mag_FD(MAG_DEFAULT);
        set_mag_reg(MAG_DEFAULT);
        set_mag_uncer(MAG_UNCER_DEFAULT);
        std::vector<double> tmp;
        tmp.push_back(MAG_UNCER_DEFAULT);
        tmp.push_back(MAG_UNCER_DEFAULT);
        set_mag_uncer_vector(tmp);
        set_finder_centroid_uncer(LAT_UNCER_DEFAULT, LON_UNCER_DEFAULT);
    };

    void init_epicenter(Coordinate epicenter) {
        set_epicenter(epicenter.get_lat(), epicenter.get_lon());
        set_finder_centroid(epicenter.get_lat(), epicenter.get_lon());
    };

    void reset_mags() {
        set_mag(0.);
        std::vector<double>::iterator it;
        for (it=mag_uncer_vector.begin(); it!=mag_uncer_vector.end(); it++) {
            *it = 0.;
        }
    }

}; // Finder_Internal

/** \class Finder_Data_Template Class to hold information about the template matching for one 
 * instance of Finder_Parameters (template set) for one event
 */
class Finder_Data_Template : public Finder_Internal {
  public:
    Finder_Parameters* finder_parameters;
    bool usedLastIter;
    bool run_status;

    size_t min_ind_pgathresh; /**< index of PGA threshold with minimum misfit & reaching minimum pixel limit (mini)*/
    size_t min_ind_pgathresh_old; /**< keep one layer of history of minimum misfit PGA */
    std::vector<double> minVal_min; /**< vector of minimum misfits at each PGA */
    std::vector<size_t> min_ind_strikes; /**< vector of indices of strikes with minimum misfits for all PGA thresholds (minj) */
    std::vector<size_t> min_ind_strikes_old; /**< keep one layer of history of strike minimum misfit indices */
    std::vector<size_t> min_ind_lengths; /**< vector of indices of lengths with minimum misfits for all PGA thresholds (mink) */
    std::vector<size_t> min_ind_lengths_old; /**< keep one layer of history of length minimum misfit indices */
    int min_ind_length; /**< Index of best length giving minimum misfit (mink) */

    Finder_Data_Template(Finder_Parameters* fp) : finder_parameters(fp) {
        min_ind_pgathresh = 0;
        min_ind_pgathresh_old = 0;
        min_ind_length = 0;
    }

    void init(size_t N_thresh) {
        resize_min_ind_strikes(N_thresh, 0);
        resize_min_ind_lengths(N_thresh, 0);
        resize_min_ind_strikes_old(N_thresh, 0);
        resize_min_ind_lengths_old(N_thresh, 0);
        resize_minVal_min(N_thresh, 1.0);
        run_status = false;
        usedLastIter = false;
    }

    int get_min_ind_length() const { return this->min_ind_length; }
    size_t get_min_ind_pgathresh() const { return this->min_ind_pgathresh; }
    size_t get_min_ind_pgathresh_old() const { return this->min_ind_pgathresh_old; }
    std::vector<double> get_minVal_min() const { return this->minVal_min; }
    std::vector<size_t> get_min_ind_strikes() const { return this->min_ind_strikes; }
    size_t get_min_ind_strike_at(const int ind) { return this->min_ind_strikes[ind]; }
    std::vector<size_t> get_min_ind_lengths() const { return this->min_ind_lengths; }
    size_t get_min_ind_length_at(const int ind) { return this->min_ind_lengths[ind]; }

    void set_min_ind_length(const int mink) { this->min_ind_length = mink; }
    void set_min_ind_length() { this->min_ind_length = this->min_ind_lengths[this->min_ind_pgathresh]; }
    void set_min_ind_length_at(const int ind, size_t val) { this->min_ind_lengths[ind] = val; }
    void set_min_ind_strike_at(const int ind, size_t val) { this->min_ind_strikes[ind] = val; }
    void set_min_ind_pgathresh(const int mini) { this->min_ind_pgathresh = mini; }
    void set_min_ind_pgathresh_old(const int mini) { this->min_ind_pgathresh_old = mini; }
    void set_minVal_min_at(const int ind, size_t val) { this->minVal_min[ind] = val; }

    void resize_min_ind_lengths(int size, double value) {
        min_ind_lengths.assign(size, value);
    }
    void resize_min_ind_strikes(int size, double value) {
        min_ind_strikes.assign(size, value);
    }
    void resize_min_ind_lengths_old(int size, double value) {
        min_ind_lengths_old.assign(size, value);
    }
    void resize_min_ind_strikes_old(int size, double value) {
        min_ind_strikes_old.assign(size, value);
    }
    void resize_minVal_min(int size, double value) {
        minVal_min.assign(size, value);
    }
    void updateMinIndexOldVectors(int thresh_end) {
        if (this->min_ind_pgathresh > this->min_ind_pgathresh_old) {
            this->min_ind_pgathresh_old = this->min_ind_pgathresh;
        }
        for (int i = this->min_ind_pgathresh; i < thresh_end; i++) {
            min_ind_strikes_old[i] = min_ind_strikes[i];
            min_ind_lengths_old[i] = min_ind_lengths[i];
            //LOGD << "For threshold i = " << i << " minj = " << this->f_data->minj[i] 
            //  << " and mink = " << this->f_data->mink[i] << ELL;
        }
    }
    void checkMinAndUpdate(double value, size_t i, size_t j, size_t k) {
        if (value <= minVal_min[i]) {
            min_ind_strikes[i] = j;
            min_ind_lengths[i] = k;
            minVal_min[i] = value;
        }
    }

}; // Finder_Data_Template

/** \class Finder_Data
 * \brief Contains most of the parameters describing an earthquake source for FinDer, inherits 
 * from Finder_Internal which has most parameters that change with each timestep and adds other
 * parameters that remain the same or do not need to be stored
 * */
class Finder_Data : public Finder_Internal {
  private:
    long event_id; /**< event id */
    bool multiple_objects; /**< true if more than one active finder object */
    bool event_continue; /**< flag for whether to continue event processing */

    // core event information that mostly does not change
    Coordinate object_center; /**< set to epicenter or finder centroid*/
    double origin_time_uncer; /**< Event origin time uncertainty */
    double depth; /**< Event depth */
    double depth_uncer; /**< Event depth uncertainty */

    // rupture
    double maxL_overtime; /**< maximum rupture length estimate over all processing */

  public:
    Finder_Parameters* finder_parameters; /**< pointer to instance of finder_parameters last used for this event */
    Finder_Data_Template* sel_fdata_templ;
    std::vector<Finder_Data_Template> templ_history_list; 

    void set_all_defaults() {
        set_defaults();
        set_origin_time_uncer(ORIGIN_TIME_UNCER_DEFAULT);
    };

    // accessor methods to retrieve values 
    Coordinate get_object_center() const { return this->object_center; }  
    double get_origin_time_uncer() const { return this->origin_time_uncer; }
    double get_depth() const { return this->depth; }
    double get_depth_uncer() const { return this->depth_uncer; }
    long get_event_id() const { return this->event_id; }
    bool get_multiple_objects() const { return this->multiple_objects; }
    double get_maxL_overtime() const { return this->maxL_overtime; }
    bool get_event_continue() const { return this->event_continue; }

    void set_object_center(const double center_lat, const double center_lon)
        { this->object_center = Coordinate(center_lat, center_lon); }
    void set_origin_time_uncer(const double origin_time_uncer_new)
        { this->origin_time_uncer = origin_time_uncer_new; }
    void set_depth(const double depth_new) { this->depth = depth_new; }
    void set_depth_uncer(const double depth_uncer_new) { this->depth_uncer = depth_uncer_new; }
    void set_event_id(const long event_id) { this->event_id = event_id; }
    void set_multiple_objects(const bool new_multiple_objects)
        { this->multiple_objects = new_multiple_objects; }
    void set_maxL_overtime(double value) { this->maxL_overtime = value; }
    void set_event_continue(bool value) { this->event_continue = value; }

}; // Finder_Data

}; // namespace FiniteFault

#endif // __finite_fault_h_

// end of file: finite_fault.h
