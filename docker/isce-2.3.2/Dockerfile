# Scott Henderson (scottyh@uw.edu)
# Date: July 2018
FROM ubuntu:18.04 as build

WORKDIR /tmp

COPY v2.3.2.tar.gz SConfigISCE /tmp/

# Update Base Ubuntu installation
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && \
    apt install -y gfortran libmotif-dev libhdf5-dev libfftw3-dev libgdal-dev scons python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install ISCE and remove files from /tmp folder
RUN tar -zxf v2.3.2.tar.gz && \
    cd isce2-2.3.2 && \
    export PYTHONPATH=/tmp/isce2-2.3.2/configuration && \
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

# Setup ISCE environment
ENV ISCE_ROOT /opt/isce2-2.3.2
ENV ISCE_HOME $ISCE_ROOT/isce
ENV PATH $ISCE_HOME/bin:$ISCE_HOME/applications:$PATH
ENV PYTHONPATH $ISCE_ROOT:$ISCE_HOME/applications:$ISCE_HOME/component

# Don't run container as root user
RUN groupadd -r ubuntu && \
    useradd -r -l -s /bin/bash -g ubuntu ubuntu
USER ubuntu
WORKDIR /home/ubuntu

# Copy ISCE installation files
COPY --from=build /opt /opt

CMD /bin/bash
