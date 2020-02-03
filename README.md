![Action Status](https://github.com/scottyhq/dinosar/workflows/Package/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/dinosar/badge/?version=latest)](https://dinosar.readthedocs.io/en/latest/?badge=latest)

[![DOI](https://zenodo.org/badge/110758901.svg)](https://zenodo.org/badge/latestdoi/110758901)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/zenodo/10.5281/zenodo.3626175)

# dinoSAR (BETA!) 

dinoSAR processes InSAR data on the Cloud.

dinoSAR is software that enables on-demand processing of single interferograms and sets of interferograms for a given area of interest on the Cloud. Processing is done with [ISCE Software](https://winsar.unavco.org/isce.html) that is [Dockerized](https://docs.docker.com) and run on [AWS Batch](https://aws.amazon.com/batch). So for now we have *dinoSARaws*.

Currently, dinoSAR works with [Sentinel-1](http://www.esa.int/Our_Activities/Observing_the_Earth/Copernicus/Sentinel-1) data, which is provided by the European Space Agency (ESA). dinoSAR utilities for searching for data [via the Alaska Satellite Facility (ASF)](https://www.asf.alaska.edu/) and setting up processing to either run locally or on the Cloud. Why run on the Cloud? SAR imagery takes up a lot of disk space and because data is being stored on AWS, running on the Cloud circumvents the need to download data. Furthermore, we can take advantage of scalable parallel processing!  

dinoSAR enables Cloud-native processing of output imagery by creating [Cloud-Optimized Geotiffs](http://www.cogeo.org) with accompanying [STAC metadata](https://github.com/radiantearth/stac-spec). You can find examples of postprocessing workflows on the [Pangeo website](http://pangeo.io). 


## acknowledgments

This project got started with funding from the University of Washington [eScience Institute](http://escience.washington.edu) and the [Washington Research Foundation](http://www.wrfseattle.org). Additionally, financial support has come from Amazon 'Earth on AWS' [Grants program](https://aws.amazon.com/earth/research-credits/) and the [NASA ACCESS program](https://earthdata.nasa.gov/community/community-data-system-programs/access-projects/community-tools-for-analysis-of-nasa-earth-observation-system-data-in-the-cloud).
