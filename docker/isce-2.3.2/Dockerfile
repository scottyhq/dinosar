FROM ubuntu:18.04 as build
# Build ISCE as root with development libraries
# --------------------------------
LABEL maintainer="scottyh@uw.edu"

WORKDIR /tmp

COPY SConfigISCE /tmp/
COPY entrypoint.sh /opt/entrypoint.sh

# Update Base Ubuntu installation
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && apt-get install -y wget gfortran libmotif-dev libhdf5-dev libfftw3-dev libgdal-dev scons python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ISCE and remove files from /tmp folder
RUN wget https://github.com/isce-framework/isce2/archive/v2.3.2.tar.gz \
    && tar -zxf v2.3.2.tar.gz \
    && cd isce2-2.3.2 \
    && export PYTHONPATH=/tmp/isce2-2.3.2/configuration \
    && export SCONS_CONFIG_DIR=/tmp \
    && scons install --skipcheck \
    && rm -rf /tmp/*


# Multistage build reduces size (no need for compilers and development libraries)
# ----------------------------------
FROM ubuntu:18.04 as run

ENV USER ubuntu
ENV UID 1000

# Copy ISCE installation files
COPY --from=build /opt /opt

# Install run-time libraries
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && apt-get install -y zip curl libmotif-common libfftw3-3 python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip aria2 \
    && apt-get clean \
    &&  rm -rf /var/lib/apt/lists/*

# Don't run container as root user
RUN groupadd \
        --gid ${UID} \
        ${USER}  \
    && useradd \
        --comment "Default user" \
        --create-home \
        --gid ${UID} \
        --no-log-init \
        --shell /bin/bash \
        --uid ${UID} \
        ${USER} \
    && chown -R ${USER}:${USER} /opt \
    && chown -R ${USER}:${USER} /home/${USER}

# Setup ISCE environment
ENV ISCE_ROOT /opt/isce2-2.3.2
ENV ISCE_HOME $ISCE_ROOT/isce
ENV PATH $ISCE_HOME/bin:$ISCE_HOME/applications:$PATH
ENV PYTHONPATH $ISCE_ROOT:$ISCE_HOME/applications:$ISCE_HOME/component

# Placeholders for NASA URS AUTH
ENV NASAUSER runtimeenv
ENV NASAPASS runtimeenv

USER ubuntu
WORKDIR /home/ubuntu

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["/bin/bash"]
