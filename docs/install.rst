dinosar Installation
====================

``dinosar`` is easy to install with pip::

  pip install dinosar

Requirements
-------------

- Note that dinosar only works with Python>3.6.
- To run `ISCE software`_ you need to have an institutional user agreement.
- You'll need a `NASA Earthdata`_ login to download SAR data.
- You'll need an AWS_ account to use AWS Batch functionality.

Configuration
-------------
This software reads ``~/.netrc`` and ``~/.aws/credentials`` configuration files.
The ``~/.netrc`` file is created manually with the following format::

  machine urs.earthdata.nasa.gov
    login [USER]
    password [PASSWORD]

The ``~/.aws/credentials`` file is created by installing the AWS CLI and running::

  aws configure


.. _`ISCE software`: https://winsar.unavco.org/software/isce
.. _`NASA Earthdata`: https://urs.earthdata.nasa.gov
.. _AWS: https://aws.amazon.com
