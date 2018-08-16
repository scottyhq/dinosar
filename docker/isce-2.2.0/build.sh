# Script to retrive ISCE source code and create a docker container
wget https://imaging.unavco.org/software/ISCE/isce-2.2.0.tar.bz2
docker build --rm -t dinosar/isce:v2.2.0 . 
echo 'ISCE is now a docker image tagged "dinosar/isce:v2.2.0"'
