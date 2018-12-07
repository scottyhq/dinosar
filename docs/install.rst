Installation
============


Quickstart
----------

``dinosar`` is easy to install with pip::

  pip install dinosar

It's recommended to install dinosar in an isolated python environment. See :ref:`full-install`.


Requirements
------------

- You'll need an institutional user agreement to run `ISCE software`_
- You'll need a `NASA Earthdata`_ login to download SAR data from `ASF Vertex`_.
- You'll need an AWS_ account to use AWS Batch functionality.
- dinosar only works with Python>3.6.
- for Python dependencies see requirements.txt


.. _configuration:

Configuration
-------------
This software reads ``~/.netrc`` and ``~/.aws/credentials`` configuration files.
The ``~/.netrc`` file is created manually with the following format:

.. code:: bash

    machine urs.earthdata.nasa.gov
        login [USER]
        password [PASSWORD]

The ``~/.aws/credentials`` file is created by installing the AWS CLI and running:

.. code:: bash

    aws configure


.. _full-install:

Full installation guide
-----------------------

This section assumes you are installing a dinosar for the first time. We are going to assume this is being installed on a Mac, but the procedure is almost identical on Linux, just make sure you get the correct `conda installer`_::

    wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
    bash Miniconda3-latest-MacOSX-x86_64.sh
    conda create -n dinosar python=3.6
    conda activate dinosar
    pip install dinosar


To get the full functionality of dinosar, you will need to install ISCE software as a Docker container. Fortunately Docker is easy to install on most systems - see `Docker Installation guide`_. Once Docker is installed create a local ISCE image::

    DINODIR=`pip show dinosar | grep Location | cut -d':' -f2`
    cd $DINODIR/docker
    ./build.sh


Now when you want to run ISCE, let Docker create a container from your image. By default this container will have access to all your system resources. **Unlike regular programs, docker containers are ephemeral and once closed all your data is deleted**, so be sure to map a local folder where you are working for data to persist. For example::

    docker run -it --rm -v $PWD:/home/ubuntu dinosar/isce:v2.2.0 /bin/bash

Docker containers also require additional command line arguments if you have graphical programs that you want to use (like `mdx.py`). It's convenient to wrap a bash function in your `~.bashrc` file so that launching ISCE is easy::

  start_isce () {
      echo 'Starting interactive ISCE session via docker'
      echo 'type "exit" to get back to your terminal'
      IP=$(ifconfig en0 | awk '/inet /{print $2 ":0"}')
      xhost +
      docker run -it --rm -e DISPLAY=$IP \
      -v $PWD:/home/ubuntu \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      dinosar/isce:v2.2.0 \
      /bin/bash
  }

Now in a folder prepared for processing an interferogram, run::

    start_isce
    topsApp.py --steps 2>&1 | tee topsApp.log


For a tutorial that demonstrates a full workflow, see the `examples section <./examples>`__.

.. _`conda installer`: https://conda.io/miniconda.html#miniconda
.. _`Docker Installation guide`: https://docs.docker.com/install/
.. _`ISCE software`: https://winsar.unavco.org/software/isce
.. _`NASA Earthdata`: https://urs.earthdata.nasa.gov
.. _`ASF Vertex`: https://vertex.daac.asf.alaska.edu
.. _AWS: https://aws.amazon.com
