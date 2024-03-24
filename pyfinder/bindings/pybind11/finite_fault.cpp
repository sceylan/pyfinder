#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "finder_headers/finite_fault.h"


namespace py = pybind11;

PYBIND11_MODULE(finite_fault, m) {
    m.doc() = "Python bindings for the FinDer library FiniteFault module";

    // Create a submodule for FiniteFault. ff represents the FiniteFault namespace 
    auto ff = m.def_submodule("FiniteFault", "Submodule for FiniteFault namespace");

    // Bind Coordinate class within FiniteFault
    py::class_<FiniteFault::Coordinate>(ff, "Coordinate")
        .def(py::init<double, double>(),
             py::arg("lat") = NAN, py::arg("lon") = NAN)
        .def("get_lat", &FiniteFault::Coordinate::get_lat)
        .def("get_lon", &FiniteFault::Coordinate::get_lon)
        .def("toVector", &Coordinate::toVector)
        .def("__repr__",
             [](const FiniteFault::Coordinate &c) {
                 return "<Coordinate lat=" + std::to_string(c.get_lat()) + ", lon=" + std::to_string(c.get_lon()) + ">";
             });

    // Bind TemplateCollection for Coordinate within FiniteFault
    py::bind_vector<FiniteFault::TemplateCollection<FiniteFault::Coordinate>>(ff, "CoordinateCollection")
        .def(py::init<>());

    // Use an alias for CoordinateList since it is a specialization of TemplateCollection
    ff.attr("CoordinateList") = ff.attr("CoordinateCollection");

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
        .def("size_event_id_list", &FiniteFault::PGA_Data::size_event_id_list)

    // Bind Finder_Centroid, inheriting from Coordinate
    py::class_<FiniteFault::Finder_Centroid, FiniteFault::Coordinate>(ff, "FinderCentroid")
        .def(py::init<double, double>(),
             py::arg("lat") = NAN, py::arg("lon") = NAN)
        // Inherits methods from Coordinate, no additional methods to bind
        .def("__repr__",
             [](const FiniteFault::Finder_Centroid &fc) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<FinderCentroid lat=" << fc.get_lat() << ", lon=" << fc.get_lon() << ">";
                 return os.str();
             });

    // Bind Finder_Rupture, inheriting from Coordinate
    py::class_<FiniteFault::Finder_Rupture, FiniteFault::Coordinate>(m, "FinderRupture")
        .def(py::init<double, double, double>(),
             py::arg("lat") = NAN, py::arg("lon") = NAN, py::arg("depth") = NAN)
        .def("get_depth", &FiniteFault::Finder_Rupture::get_depth)
        .def("__repr__",
             [](const FiniteFault::Finder_Rupture &fr) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<FinderRupture lat=" << fr.get_lat() << ", lon=" << fr.get_lon() << ", depth=" << fr.get_depth() << ">";
                 return os.str();
             });

    // Bind Finder_Rupture_List
    py::bind_vector<FiniteFault::Finder_Rupture_List>(ff, "FinderRuptureList")
        .def(py::init<>())
        // Finder_Rupture_List inherits TemplateCollection's methods, so 
        // most of the common functionalities are covered by py::bind_vector.
        ;

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
    py::bind_vector<FiniteFault::Misfit_List>(ff, "MisfitList")
        .def(py::init<>());

    // Bind Finder_Azimuth which inherits from Misfit
    py::class_<FiniteFault::Finder_Azimuth, FiniteFault::Misfit>(ff, "FinderAzimuth")
        .def(py::init<double, double>(),
             py::arg("azimuth") = NAN, py::arg("misf") = NAN)
        // Inherits get_value() and get_misf() from Misfit, so no need to redefine those
        .def("__repr__",
             [](const FiniteFault::Finder_Azimuth &azimuth) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<FinderAzimuth azimuth=" << azimuth.get_value() << ", misf=" << azimuth.get_misf() << ">";
                 return os.str();
             });

    // Bind Finder_Azimuth_List
    py::bind_vector<FiniteFault::Finder_Azimuth_List>(ff, "FinderAzimuthList")
        .def(py::init<>());

    
    // Bind Finder_Length, inheriting from Misfit
    py::class_<FiniteFault::Finder_Length, FiniteFault::Misfit>(ff, "FinderLength")
        .def(py::init<double, double>(),
             py::arg("length") = NAN, py::arg("misf") = NAN)
        // Inherits get_value() and get_misf() from Misfit, so no need to redefine those
        .def("__repr__",
             [](const FiniteFault::Finder_Length &fl) {
                 std::ostringstream os;
                 os << std::fixed << std::setprecision(3) << "<FinderLength length=" << fl.get_value() << ", misf=" << fl.get_misf() << ">";
                 return os.str();
             });

    // Bind Finder_Length_List
    py::bind_vector<FiniteFault::Finder_Length_List>(ff, "FinderLengthList")
        .def(py::init<>());


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


    // LogLikelihood_List as a vector of LogLikelihood pointers
    py::bind_vector<FiniteFault::LogLikelihood_List>(ff, "LogLikelihoodList")
        .def(py::init<>());

    // Bind Finder_Azimuth_LLK, inheriting from LogLikelihood
    py::class_<FiniteFault::Finder_Azimuth_LLK, FiniteFault::LogLikelihood>(ff, "FinderAzimuthLLK")
        .def(py::init<double, double>(),
            py::arg("azimuth") = NAN, py::arg("llk") = NAN)
        // Inherits methods from LogLikelihood
        .def("__repr__",
            [](const FiniteFault::Finder_Azimuth_LLK &fallk) {
                return "<FinderAzimuthLLK azimuth=" + std::to_string(fallk.get_value()) + ", llk=" + std::to_string(fallk.get_llk()) + ">";
            });

    // Bind Finder_Azimuth_LLK_List
    py::bind_vector<FiniteFault::Finder_Azimuth_LLK_List>(ff, "FinderAzimuthLLKList")
        .def(py::init<>());
}
