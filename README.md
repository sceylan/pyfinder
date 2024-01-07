# pyfinder
**pyfinder** is a Python wrapper for the FinDer. It is designed to query the ESM, EMSC and RRSM web services to retrieve the acceleration amplitudes and felt reports, and trigger the FinDer library with this new external information. This tool works within the SeisComp framework.

This tool:
- is able to query ESM and RRSM shakemap endpoint. With this endpoint, the tool also queries with the ```format=event``` option to retrieve the basic event information. See the [ESM Shakemap web service](https://esm-db.eu//esmws/shakemap/1/query-options.html) for more information. 
- RRSM also uses the same web services as the ESM. The tool only implements minor changes, such as the base service URL, for queries.
- The EMSC importer is currently under development.
