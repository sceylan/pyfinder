#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include "finder_headers/finder.h"  // Ensure this includes all necessary definitions

namespace py = pybind11;

// PYBIND11_MODULE(finite_fault, m) {
//     auto ff = m.def_submodule("FiniteFault", "Submodule for FiniteFault namespace");

    // Binding Finder_List as a vector of Finder pointers
    py::bind_vector<FiniteFault::TemplateCollection<FiniteFault::Finder*>>(ff, "FinderList");

    // Binding the Finder class. All other classes should be already bound.
    py::class_<FiniteFault::Finder>(ff, "Finder")
        .def(py::init<const FiniteFault::Coordinate&, const FiniteFault::PGA_Data_List&, long, long>())
        .def_static("Set_Debug_Level", &FiniteFault::Finder::Set_Debug_Level)
        .def_static("Get_Debug_Level", &FiniteFault::Finder::Get_Debug_Level)
        .def_static("Init", &FiniteFault::Finder::Init)
        
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
