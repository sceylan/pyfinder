#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "finder_headers/finite_fault.h"
#include "finder_headers/finder.h"

namespace py = pybind11;

// Forward declarations
template <typename T> void bind_TemplateCollection(py::module &m, const std::string &typeName);
void init_finite_fault_bindings(py::module &ff);
void init_finder_bindings(py::module &ff);

// Main bindings entry function for the FiniteFault namespace
PYBIND11_MODULE(pylibfinder, m) {
    m.doc() = "Python bindings for the FinDer library";

    // Create a submodule for FiniteFault. ff represents the FiniteFault namespace 
    auto ff = m.def_submodule("FiniteFault", "Submodule for FiniteFault namespace");
    
    // Bind classes within FiniteFault namespace
    init_finite_fault_bindings(ff);

    // Bind Finder class within FiniteFault
    init_finder_bindings(ff);
}

// Bind TemplateCollection class explicity to avoid issues with py::bind_vector
template <typename T>
void bind_TemplateCollection(py::module &m, const std::string &typeName) {
    using Collection = FiniteFault::TemplateCollection<T>;

    py::class_<Collection>(m, typeName.c_str())
        .def(py::init<>())
        //.def("clear", &Collection::clear)
        .def("clear", [](Collection &c) { c.std::vector<T>::clear(); })
        .def("push_back", [](Collection &c, const T &value) { c.push_back(value); },
             "Appends the given element to the end of the container.")
        .def("pop_back", [](Collection &c) { c.pop_back(); },
             "Removes the last element of the container.")
        .def("size", &Collection::size)
        .def("begin", [](Collection &c) { return c.begin(); })
        .def("end", [](Collection &c) { return c.end(); })
        .def("__len__", [](const Collection &v) { return v.size(); })
        
        .def("__iter__", [](Collection &v) {
            return py::make_iterator(v.begin(), v.end());
        }, py::keep_alive<0, 1>()) /* Keep vector alive while iterator is used */

        .def("__getitem__", [](const Collection &v, size_t i) {
            if (i >= v.size()) throw py::index_error();
            return v[i];
        })
        .def("__setitem__", [](Collection &v, size_t i, const T &value) {
            if (i >= v.size()) throw py::index_error();
            v[i] = value;
        });
        
        // Add other std::vector methods and custom methods of TemplateCollection as needed
}


/**
 * Bindings for classes inside the finite_fault.h header file. All these classes 
 * are within the FiniteFault namespace.
 */
void init_finite_fault_bindings(py::module &ff){
    // Bind Coordinate class 
    py::class_<FiniteFault::Coordinate>(ff, "Coordinate")
        .def(py::init<double, double>(),
             py::arg("lat") = NAN, py::arg("lon") = NAN)
        .def("get_lat", &FiniteFault::Coordinate::get_lat)
        .def("get_lon", &FiniteFault::Coordinate::get_lon)
        .def("toVector", &FiniteFault::Coordinate::toVector)
        .def("__repr__",
             [](const FiniteFault::Coordinate &c) {
                 return "<Coordinate lat=" + std::to_string(c.get_lat()) + 
                 ", lon=" + std::to_string(c.get_lon()) + ">";
             });

    // Bind CoordinateCollection as a vector of Coordinate pointers 
    // within FiniteFault namespace. Pybind11 bind_vector did not work.
    // bind_TemplateCollection<FiniteFault::Coordinate>(ff, "CoordinateCollection");

    // Use an alias for CoordinateList since it is a specialization of TemplateCollection
    // ff.attr("Coordinate_List") = ff.attr("CoordinateCollection");
    bind_TemplateCollection<FiniteFault::Coordinate>(ff, "Coordinate_List");

    // Bind PGA_Data class within FiniteFault
    py::class_<FiniteFault::PGA_Data>(ff, "PGA_Data")
        .def(py::init<const std::string&, const std::string&, const std::string&, const std::string&, const FiniteFault::Coordinate&, double, double, bool>(),
             py::arg("name") = "nan", py::arg("network") = "nan", py::arg("channel") = "nan",
             py::arg("location_code") = "nan", py::arg("location") = FiniteFault::Coordinate(NAN,NAN),
             py::arg("value") = NAN, py::arg("timestamp") = NAN, py::arg("include") = true)
        .def("get_name", &FiniteFault::PGA_Data::get_name)
        .def("get_network", &FiniteFault::PGA_Data::get_network)
        .def("get_channel", &FiniteFault::PGA_Data::get_channel)
        .def("get_location_code", &FiniteFault::PGA_Data::get_location_code)
        .def("get_location", &FiniteFault::PGA_Data::get_location)
        .def("get_value", &FiniteFault::PGA_Data::get_value)
        .def("get_timestamp", &FiniteFault::PGA_Data::get_timestamp)
        .def("get_include", &FiniteFault::PGA_Data::get_include)
        .def("get_trigger_flag", &FiniteFault::PGA_Data::get_trigger_flag)
        .def("get_event_id_list", &FiniteFault::PGA_Data::get_event_id_list)
        .def("update_value", &FiniteFault::PGA_Data::update_value)
        .def("set_include", &FiniteFault::PGA_Data::set_include)
        .def("set_trigger_flag", &FiniteFault::PGA_Data::set_trigger_flag)
        .def("set_event_id_list", &FiniteFault::PGA_Data::set_event_id_list)
        .def("resize_event_id_list", &FiniteFault::PGA_Data::resize_event_id_list)
        .def("size_event_id_list", &FiniteFault::PGA_Data::size_event_id_list);

    // Bind PGA_Data_List as a vector of PGA_Data pointers within FiniteFault namespace
    bind_TemplateCollection<FiniteFault::PGA_Data>(ff, "PGA_Data_List");
    
    // Bind Finder_Centroid, inheriting from Coordinate.
    // Finder_Centroid is the mid-point of the line source.
    py::class_<FiniteFault::Finder_Centroid, FiniteFault::Coordinate>(ff, "Finder_Centroid")
        .def(py::init<double, double>(),
             py::arg("lat") = NAN, py::arg("lon") = NAN)
        // Inherits methods from Coordinate, no additional methods to bind
        .def("__repr__",
             [](const FiniteFault::Finder_Centroid &fc) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<Finder_Centroid lat=" << fc.get_lat() << ", lon=" << fc.get_lon() << ">";
                 return os.str();
             });

    // Bind Finder_Rupture, inheriting from Coordinate
    py::class_<FiniteFault::Finder_Rupture, FiniteFault::Coordinate>(ff, "Finder_Rupture")
        .def(py::init<double, double, double>(),
             py::arg("lat") = NAN, py::arg("lon") = NAN, py::arg("depth") = NAN)
        .def("get_depth", &FiniteFault::Finder_Rupture::get_depth)
        .def("__repr__",
             [](const FiniteFault::Finder_Rupture &fr) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<Finder_Rupture lat=" << fr.get_lat() << ", lon=" << fr.get_lon() << ", depth=" << fr.get_depth() << ">";
                 return os.str();
             });

    // Bind Finder_Rupture_List
    bind_TemplateCollection<FiniteFault::Finder_Rupture>(ff, "Finder_Rupture_List");
    
    // Bind Misfit class within FiniteFault
    py::class_<FiniteFault::Misfit>(ff, "Misfit")
        .def(py::init<double, double>(),
             py::arg("value") = NAN, py::arg("misf") = NAN)
        .def("get_value", &FiniteFault::Misfit::get_value)
        .def("get_misf", &FiniteFault::Misfit::get_misf)
        .def("__repr__",
             [](const FiniteFault::Misfit &misfit) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<Misfit value=" << misfit.get_value() << ", misf=" << misfit.get_misf() << ">";
                 return os.str();
             });

    // Bind Misfit_List as a vector of Misfit pointers withtin FiniteFault namespace
    bind_TemplateCollection<FiniteFault::Misfit>(ff, "Misfit_List");

    // Bind Finder_Azimuth which inherits from Misfit
    py::class_<FiniteFault::Finder_Azimuth, FiniteFault::Misfit>(ff, "Finder_Azimuth")
        .def(py::init<double, double>(),
             py::arg("azimuth") = NAN, py::arg("misf") = NAN)
        // Inherits get_value() and get_misf() from Misfit, so no need to redefine those
        .def("__repr__",
             [](const FiniteFault::Finder_Azimuth &azimuth) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<Finder_Azimuth azimuth=" << azimuth.get_value() << ", misf=" << azimuth.get_misf() << ">";
                 return os.str();
             });

    // Bind Finder_Azimuth_List
    bind_TemplateCollection<FiniteFault::Finder_Azimuth>(ff, "Finder_Azimuth_List");
    
    // Bind Finder_Length, inheriting from Misfit
    py::class_<FiniteFault::Finder_Length, FiniteFault::Misfit>(ff, "Finder_Length")
        .def(py::init<double, double>(),
             py::arg("length") = NAN, py::arg("misf") = NAN)
        // Inherits get_value() and get_misf() from Misfit, so no need to redefine those
        .def("__repr__",
             [](const FiniteFault::Finder_Length &fl) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<Finder_Length length=" << fl.get_value() << ", misf=" << fl.get_misf() << ">";
                 return os.str();
             });

    // Bind Finder_Length_List
    bind_TemplateCollection<FiniteFault::Finder_Length>(ff, "Finder_Length_List");

    
    // Bind LogLikelihood class within FiniteFault
    py::class_<FiniteFault::LogLikelihood>(ff, "LogLikelihood")
        .def(py::init<double, double>(),
             py::arg("value") = NAN, py::arg("llk") = NAN)
        .def("get_value", &FiniteFault::LogLikelihood::get_value)
        .def("get_llk", &FiniteFault::LogLikelihood::get_llk)
        .def("__repr__",
             [](const FiniteFault::LogLikelihood &ll) {
                 return "<LogLikelihood value=" + std::to_string(ll.get_value()) + ", llk=" + std::to_string(ll.get_llk()) + ">";
             });

    // Bind LogLikelihood_List as a vector of LogLikelihood pointers
    bind_TemplateCollection<FiniteFault::LogLikelihood>(ff, "LogLikelihood_List");

    // // Bind Finder_Azimuth_LLK, inheriting from LogLikelihood
    // py::class_<FiniteFault::Finder_Azimuth_LLK, FiniteFault::LogLikelihood>(ff, "FinderAzimuthLLK")
    //     .def(py::init<double, double>(),
    //         py::arg("azimuth") = NAN, py::arg("llk") = NAN)
    //     // Inherits methods from LogLikelihood
    //     .def("__repr__",
    //         [](const FiniteFault::Finder_Azimuth_LLK &fallk) {
    //             return "<FinderAzimuthLLK azimuth=" + std::to_string(fallk.get_value()) + ", llk=" + std::to_string(fallk.get_llk()) + ">";
    //         });

    // // Bind Finder_Azimuth_LLK_List
    // py::bind_vector<FiniteFault::Finder_Azimuth_LLK_List>(ff, "FinderAzimuthLLKList")
    //     .def(py::init<>());
}


/**
 * Bindings for the Finder class from the finder.h header file. 
 */
void init_finder_bindings(py::module &ff) {
    // Binding the Finder class. All other classes should be already bound.
    py::class_<FiniteFault::Finder>(ff, "Finder")
        .def(py::init<const FiniteFault::Coordinate&, const FiniteFault::PGA_Data_List&, long, long>())
        .def_static("Set_Debug_Level", &FiniteFault::Finder::Set_Debug_Level)
        .def_static("Get_Debug_Level", &FiniteFault::Finder::Get_Debug_Level)
        .def_static("Init", &FiniteFault::Finder::Init,
            py::arg("config_file"), py::arg("station_coord_list"),
            "Initializes the Finder with a configuration file and a list of station coordinates.")

        // Accessor methods to retrieve calculated values
        .def("get_event_id", &FiniteFault::Finder::get_event_id)
        .def("get_mag", &FiniteFault::Finder::get_mag)
        .def("get_mag_FD", &FiniteFault::Finder::get_mag_FD)
        .def("get_mag_reg", &FiniteFault::Finder::get_mag_reg)
        .def("get_mag_uncer", &FiniteFault::Finder::get_mag_uncer)
        .def("get_epicenter", &FiniteFault::Finder::get_epicenter)
        .def("get_epicenter_uncer", &FiniteFault::Finder::get_epicenter_uncer)
        .def("get_origin_time", &FiniteFault::Finder::get_origin_time)
        .def("get_origin_time_uncer", &FiniteFault::Finder::get_origin_time_uncer)
        .def("get_depth", &FiniteFault::Finder::get_depth)
        .def("get_depth_uncer", &FiniteFault::Finder::get_depth_uncer)
        .def("get_likelihood_estimate", &FiniteFault::Finder::get_likelihood_estimate)
        .def("get_rupture_length", &FiniteFault::Finder::get_rupture_length)
        .def("get_rupture_azimuth", &FiniteFault::Finder::get_rupture_azimuth)
        .def("get_azimuth_uncer", &FiniteFault::Finder::get_azimuth_uncer)
        
        // Setter functions for controlling the behavior of Finder 
        .def("set_last_message_time", &FiniteFault::Finder::set_last_message_time)
        .def("set_start_time", &FiniteFault::Finder::set_start_time)
        .def("set_finder_flags", &FiniteFault::Finder::set_finder_flags)
        .def("set_hold_time", &FiniteFault::Finder::set_hold_time)
        .def("set_rejected_stations", &FiniteFault::Finder::set_rejected_stations)
        .def("set_pga_data_list", &FiniteFault::Finder::set_pga_data_list)
        .def("set_pga_above_min_thresh", &FiniteFault::Finder::set_pga_above_min_thresh)
        ;
}