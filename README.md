[![Build Status](https://travis-ci.org/scottyhq/dinosar.svg?branch=master)](https://travis-ci.org/scottyhq/dinosar)
[![Documentation Status](https://readthedocs.org/projects/dinosar/badge/?version=latest)](https://dinosar.readthedocs.io/en/latest/?badge=latest)


# dinoSAR (BETA!) 

dinoSAR processes InSAR data on the Cloud.

dinoSAR is software that enables on-demand processing of single interferograms and sets of interferograms for a given area of interest in the Cloud. Processing is done with [ISCE Software](https://winsar.unavco.org/isce.html) that is [Dockerized](https://docs.docker.com) and run on [AWS Batch](https://aws.amazon.com/batch). So for now we have *dinoSARaws*, but it is straightforward to running components locally or on other Clouds.

Currently, dinoSAR works with [Sentinel-1](http://www.esa.int/Our_Activities/Observing_the_Earth/Copernicus/Sentinel-1) data, which is provided by the European Space Agency (ESA). dinoSAR also contains some Jupyter Notebooks for analyzing ISCE outputs. The main idea is to do as much as possible on the Cloud and tax your local computer as little as possible.


## acknowledgments

This project got started with funding from the University of Washington [eScience Institute](http://escience.washington.edu) and the [Washington Research Foundation](http://www.wrfseattle.org). Additionally, financial support has come from Amazon 'Earth on AWS' [Grants program](https://aws.amazon.com/earth/research-credits/) and the [NASA ACCESS program](https://aws.amazon.com/earth/research-credits/).
