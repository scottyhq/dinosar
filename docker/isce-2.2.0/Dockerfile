# Scott Henderson (scottyh@uw.edu)
# Date: July 2018
FROM ubuntu:18.04 as build

WORKDIR /tmp

COPY isce-2.2.0.tar.bz2 SConfigISCE /tmp/

# Update Base Ubuntu installation
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && \
    apt install -y gfortran libmotif-dev libhdf5-dev libfftw3-dev libgdal-dev scons python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install ISCE and remove files from /tmp folder
RUN bunzip2 isce-2.2.0.tar.bz2 && \
    tar -xf isce-2.2.0.tar && \
    cd isce-2.2.0 && \
    export PYTHONPATH=/tmp/isce-2.2.0/configuration && \
    export SCONS_CONFIG_DIR=/tmp && \
    scons install --skipcheck && \
    rm -rf /tmp/*

# Multistage build reduces size (no need for all development libraries)
FROM ubuntu:18.04 as run

# Install run-time libraries
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && \
    apt install -y zip curl libmotif-common libfftw3-3 python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip aria2 && \
    rm -rf /var/lib/apt/lists/*

# Install additional python packages
RUN pip3 --no-cache-dir install awscli

# Setup ISCE environment
ENV ISCE_ROOT /opt/isce-2.2.0
ENV ISCE_HOME $ISCE_ROOT/isce
ENV PATH $ISCE_HOME/bin:$ISCE_HOME/applications:$PATH
ENV PYTHONPATH $ISCE_ROOT:$ISCE_HOME/applications:$ISCE_HOME/component

# Don't run container as root user
# easiest compatibility w/ AWS Batch running ECS-optimized AMI is to set uid and gid to match
RUN groupadd -r --gid 500 ubuntu && \
    useradd -r -l -s /bin/bash -g ubuntu --uid 500 ubuntu
USER ubuntu
WORKDIR /home/ubuntu

# Copy ISCE installation files
COPY --from=build /opt /opt

CMD /bin/bash
