#!/bin/bash 
echo "Running interferogram generation script..."
echo $PWD
cd /home/ubuntu
echo $PWD

# Initialize software warning - defaults to root directory
#source ~/.bashrc
#source ~/.aliases
source /home/ubuntu/.aliases
start_isce

# Get the latest python scripts from github & add to path
git clone https://github.com/scottyhq/dinoSAR.git
export PATH=/home/ubuntu/dinoSAR/bin:$PATH
echo $PATH

# Download inventory file
get_inventory_asf.py -r 44.0 44.5 -122.0 -121.5

# Prepare interferogram directory
prep_topsApp.py -i query.geojson -m 20170927 -s 20170903 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5

# Run code
cd int_20170927_20170903
topsApp.py 2>&1 | tee topsApp.log

# Create S3 bucket and save results
aws s3 mb s3://int-20170927-20170903
cp *xml *log merged
aws s3 sync merged/ s3://int-20170927-20170903/ 

# Close instance
echo "Finished interferogram... shutting down"
#poweroff

