# Craig Stringham (craig@capellaspace.com)
# Date: March 2019

FROM continuumio/anaconda3 as build

RUN conda install -y cartopy
RUN conda install -y pip
WORKDIR /opt/
# TODO get changes pushed in to scottyhq's branch
RUN git clone https://github.com/stringhamc/dinosar.git
WORKDIR /opt/dinosar
RUN python setup.py .

# Don't run container as root user
RUN groupadd -r ubuntu && \
    useradd -u 1000 -r -l -s /bin/bash -g ubuntu ubuntu
USER ubuntu
WORKDIR /home/ubuntu

CMD /bin/bash
