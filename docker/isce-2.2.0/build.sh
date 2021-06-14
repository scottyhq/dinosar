# Script to retrieve ISCE source code and create a docker container
echo '\n***** Downloading isce (requires .netrc)... *****\n'
wget https://imaging.unavco.org/software/ISCE/isce-2.2.0.tar.bz2
echo '\n***** Starting Docker multistage build *****\n'
docker build --rm -t dinosar/isce:v2.2.0 .
echo '\n***** Removing intermediate docker image *****\n'
docker rmi $(docker images -q -f dangling=true)
echo '\n***** ISCE is now a Docker image tagged "dinosar/isce:v2.2.0" *****\n'
