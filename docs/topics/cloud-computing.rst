Cloud computing
===============

dinosar on the Cloud
--------------------
Docker containers can also be run as non-interactive tasks. So while the above directions are convenient for running ISCE interactively on any operating system with Docker installed, you might want to just launch some scripts and looks at the results when they are done.

You can launch many container copies that run a specific process. For example, launch *topsApp.py* 6 times to process different interferograms simultaneously with different allotments of CPU and RAM). This is similar to HPC job queues managed by PBS, and is commonly deployed on commercial Cloud computing clusters. Docker refers to this mode of operation as `Docker Swarm`_. Cloud providers provide convenient ways to deploy many containers like AWS ECS and AWS Batch. `Kubernetes`_ is another system for orchestrating containers that can be run on different Cloud computing providers (see AWS EKS). 


.. _`Kubernetes`: https://urs.earthdata.nasa.gov
.. _`Docker Swarm`: https://urs.earthdata.nasa.gov
