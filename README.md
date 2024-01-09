# pyfinder
**pyfinder** is a Python wrapper for the [FinDer](https://docs.gempa.de/sed-eew/current/base/intro-finder.html#finder) (Finite Fault Rupture Detector) library. It is designed to query the ESM, EMSC and RRSM web services to retrieve the acceleration amplitudes and felt reports, and trigger the FinDer with this new external parametric information. This tool works within the SeisComp framework.

This tool is able to query:
- The ESM ```shakemap``` endpoint, using both ```format=event_dat``` for amplitudes and ```format=event``` option to retrieve the basic event information. See the [ESM Shakemap web service](https://esm-db.eu//esmws/shakemap/1/query-options.html) for more information. 

- RRSM ```shakemap``` web service, which also uses the same web service as the ESM. The tool only implements minor changes such as the base service URL and order of options for queries. RRSM queries are slightly different than ESM, and do not support ```format``` option. The tool is designed to handle these nuances.  

- The EMSC felt reports, for the basic event information (```includeTestimonies=false```) and intensities (```includeTestimonies=true```).

More information on these web services are avaliable on:
- RMSS: https://www.orfeus-eu.org/rrsm/about/
- ESM: https://esm-db.eu/#/data_and_services/web_services and https://esm-db.eu//esmws/shakemap/1/
- EMSC: https://www.emsc.eu/Earthquake_data/Data_queries.php

For further information on FinDer, see the references below and [Swiss Seismological Service at ETH Zurich](http://www.seismo.ethz.ch/en/research-and-teaching/products-software/EEW/finite-fault-rupture-detector-finder/) web page.

_**References**:_

    Böse, M., Heaton, T. H., & Hauksson, E., 2012. Real‐time Finite Fault Rupture Detector (FinDer) for large earthquakes. Geophysical Journal International, 191(2), 803–812, doi:10.1111/j.1365-246X.2012.05657.x

    Böse, M., Felizardo, C., & Heaton, T. H., 2015. Finite-Fault Rupture Detector (FinDer): Going Real-Time in Californian ShakeAlertWarning System. Seismological Research Letters, 86(6), 1692–1704, doi:10.1785/0220150154

    Böse, M., Smith, D., Felizardo, C., Meier, M.-A., Heaton, T. H., & Clinton, J. F., 2018. FinDer v.2: Improved Real-time Ground-Motion Predictions for M2-M9 with Seismic Finite-Source Characterization. Geophysical Journal International, 212(1), 725-742, doi:10.1093/gji/ggx430

    Cauzzi, C., Behr, Y. D., Clinton, J., Kastli, P., Elia, L., & Zollo, A., 2016. An Open-Source Earthquake Early Warning Display. Seismological Research Letters, 87(3), 737–742, doi:10.1785/0220150284
