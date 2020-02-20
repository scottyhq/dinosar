Cloud computing
===============

If you are new to Cloud computing, there are lots of resources out there, but many of the examples tend to be geared towards web applications rather than research. This guide, put together by the university of Washington eScience Institute is a good starting point.

``dinosar`` was built with Cloud computing in mind. In particular, it packages ISCE as a Docker container in order to run computations on any computer hardware. For example, we can launch 6 dinosar containers that each run *topsApp.py* to process different interferograms simultaneously. This workflow is similar to HPC job queues managed by PBS, and is a common use-case for commercial Cloud computing clusters. Docker refers to this mode of operation as `Docker Swarm`_. Cloud providers provide convenient ways to deploy many containers like AWS ECS and AWS Batch. `Kubernetes`_ is another system for orchestrating containers that can be run on different Cloud computing providers (see `AWS EKS`_).

dinosar on AWS
--------------

Although you can run a docker container on different Cloud services, it makes sense to run your software wherever the data is stored. This is because transfer speeds between machines are very fast, and no charges are incurred so long as data is not transferred out over the internet.

Most of the Sentinel-1 SLC data distributed by ASF is actually stored in the AWS in the ``us-east-1`` region, so we will want to launch our computing resources in that region!


interactive work
----------------

Perhaps you just want to launch a single powerful desktop with ISCE installed and work interactively in the us-east-1 region. You can do that by launching an `Amazon Machine Image (AMI_) pre-loaded with Docker`.  Then follow the dinosar installation instructions and examples as if you are working on your local machine. You can then save the modified AMI for future use, to not have to re-run all these steps next time. You'll want a machine with at least 16 Gb of RAM, so ``c5.2xlarge`` is a good choice for instance type. Also, add an additional amount of storage space for processing (either an EBS or EFS drive). With AWS you can add features and change options via the web interface. It's often convenient to set up scripts to do all the configuration (especially if you want to repeat what you are doing in the future!) - you can use AWS CloudFormation to do this.


.. _AMI: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html
.. _`Kubernetes`: https://urs.earthdata.nasa.gov
.. _`Docker Swarm`: https://urs.earthdata.nasa.gov
.. _`AWS EKS`: https://aws.amazon.com/eks
