FROM ubuntu:18.04 as build
# Build ISCE as root with development libraries
# --------------------------------
LABEL maintainer="scottyh@uw.edu"

ENV ISCE_VERSION=2.3.3

WORKDIR /tmp

COPY SConfigISCE /tmp/

# Update Base Ubuntu installation
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && apt-get install -y wget gfortran libmotif-dev libhdf5-dev libfftw3-dev libgdal-dev scons python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ISCE and remove files from /tmp folder
RUN wget https://github.com/isce-framework/isce2/archive/v${ISCE_VERSION}.tar.gz \
    && tar -zxf v${ISCE_VERSION}.tar.gz \
    && cd isce2-${ISCE_VERSION} \
    && export PYTHONPATH=/tmp/isce2-${ISCE_VERSION}/configuration \
    && export SCONS_CONFIG_DIR=/tmp \
    && scons install --skipcheck \
    && rm -rf /tmp/*


# Multistage build reduces size (no need for compilers and development libraries)
# ----------------------------------
FROM ubuntu:18.04 as run

ENV USER ubuntu
ENV UID 1000

# Install run-time libraries
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && apt-get install -y zip curl libfftw3-3 python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip aria2 \
    && apt-get clean \
    &&  rm -rf /var/lib/apt/lists/*

# Don't run container as root user
RUN groupadd --gid ${UID} ${USER}  \
    && useradd --create-home --gid ${UID} --no-log-init  --shell /bin/bash --uid ${UID} ${USER} \
    && chown -R ${USER}:${USER} /opt

USER ubuntu
WORKDIR /home/ubuntu

# Copy ISCE installation files and entrypoint script
COPY --chown=ubuntu:ubuntu --from=build /opt /opt
COPY --chown=ubuntu:ubuntu entrypoint.sh /opt/entrypoint.sh

# Install aws cli, ensure entrypoint is executable
RUN pip3 install awscli==1.18.25 --no-cache-dir \
    && chmod +x /opt/entrypoint.sh

# Setup ISCE environment
ENV ISCE_ROOT /opt/isce2-${ISCE_VERSION}
ENV ISCE_HOME $ISCE_ROOT/isce
ENV PATH $ISCE_HOME/bin:$ISCE_HOME/applications:$PATH
ENV PYTHONPATH $ISCE_ROOT:$ISCE_HOME/applications:$ISCE_HOME/component

# Placeholders for NASA URS AUTH
ENV NASAUSER runtimeenv
ENV NASAPASS runtimeenv

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["/bin/bash"]
