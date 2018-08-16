[![Build Status](https://travis-ci.org/scottyhq/dinosar.svg?branch=master)](https://travis-ci.org/scottyhq/dinosar)
[![Documentation Status](https://readthedocs.org/projects/dinosar/badge/?version=latest)](https://dinosar.readthedocs.io/en/latest/?badge=latest)


# dinoSAR

dinoSAR processes InSAR data on the Cloud.

dinoSAR is software that enables on-demand processing of single interferograms and sets of interferograms for a given area of interest in the Cloud. Processing is done with [ISCE Software](https://winsar.unavco.org/isce.html) that is [Dockerized](https://docs.docker.com) and run on [AWS Batch](https://aws.amazon.com/batch). So for now we have *dinoSARaws*, but it is straightforward to running components locally or on other Clouds.

Currently, dinoSAR works with [Sentinel-1](http://www.esa.int/Our_Activities/Observing_the_Earth/Copernicus/Sentinel-1) data, which is provided by the European Space Agency (ESA). dinoSAR also contains some Jupyter Notebooks for analyzing ISCE outputs. The main idea is to do as much as possible on the Cloud and tax your local computer as little as possible.

## example

[this notebook](link) queries the ASF archive, selects a set of interferograms, and processes them with non-default parameters.

[this notebook](link) provides examples of postprocessing dinosar outputs, which are stored on AWS S3.


## installation

dinosar requires a Python environment with python>3.6. We recommend setting that up with [conda](https://conda.io/docs/). Then simply run:

```
pip install dinosar
```

This will allow you to query the ASF Sentinel-1 archive, but if you want to process interferograms with ISCE you have to have a license agreement to retrieve the software and install it:

```
cd dinosar
./install-isce-latest.sh 2&>1 | tee install.log
```

Finally, if you want to process interferograms on AWS, you need to have an AWS Account setup,
```
./setup-aws.sh
```


## acknowledgments

This project got started with funding from the University of Washington [eScience Institute](http://escience.washington.edu) and the [Washington Research Foundation](http://www.wrfseattle.org). Additionally, financial support has come from Amazon 'Earth on AWS' [Grants program](https://aws.amazon.com/earth/research-credits/) and the [NASA ACCESS program](https://aws.amazon.com/earth/research-credits/).
