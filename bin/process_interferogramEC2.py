#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Will launch an EC2 instance, process an interferogram with specified parameters
and store the 'merged' folder on S3. Look into doing this with 'boto'

Approach: create a bash script and pass it to EC2 instanch on launch

Note: intended for single interferogram processing. For batch processing
figure out how to store common data and DEM on an EFS drive

# EXAMPLE:
process_interferogramEC2.py -p 115 -m 20170927 -s 20170915 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5


# Archived Files:
*xml *log
#filt_topophase.unw* filt_topophase.flat* dem.crop* los.rdr.geo* phsig.cor.geo* 
# For now just stash entire meged directory

Created on Sun Nov 19 16:26:27 2017

@author: scott
"""

import argparse
import os

def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser( description='prepare ISCE 2.1 topsApp.py')
    parser.add_argument('-m', type=str, dest='master', required=True,
            help='Master date')
    parser.add_argument('-s', type=str, dest='slave', required=True,
            help='Slave date')
    parser.add_argument('-p', type=int, dest='path', required=True,
            help='Path/Track/RelativeOrbit Number')
    parser.add_argument('-n', type=int, nargs='+', dest='swaths', required=False,
	        default=[1,2,3], choices=(1,2,3),
            help='Subswath numbers to process')
    parser.add_argument('-r', type=float, nargs=4, dest='roi', required=False,
            metavar=('S','N','W','E'),
	        help='Region of interest bbox [S,N,W,E]')
    parser.add_argument('-g', type=float, nargs=4, dest='gbox', required=False,
            metavar=('S','N','W','E'),
	        help='Geocode bbox [S,N,W,E]')

    return parser.parse_args()



def create_bash_script(inps):
    '''
    Write bash file to process and interferogram based on user input
    '''
    with open('run_interferogram.sh', 'w') as bash:
        bash.write('''#!/bin/bash 
echo "Running interferogram generation script..."

# Initialize software
source ~/.bashrc
start_isce

# Get the latest python scripts from github & add to path
git clone https://github.com/scottyhq/dinoSAR.git
echo PATH=/home/ubuntu/dinoSAR/bin:$PATH

# Download inventory file
get_inventory_asf.py -r {roi}

# Prepare interferogram directory
prep_topsApp.py -i query.geojson -m {master} -s {slave} -n {swaths} -r {roi} -g {gbox}

# Run code
cd int_{master}_{slave}
topsApp.py 2>&1 | tee topsApp.log

# Create S3 bucket and save results
aws s3 mb s3://int-{master}-{slave}
cp *xml *log merged
aws s3 sync merged/ s3://int-{master}-{slave}/ 

# Close instance
echo "Finished interferogram... shutting down"
#poweroff

'''.format(**vars(inps)))


def launch_ec2(ami='ami-d015daa8', instance='t2.micro', key='isce-key',
               security_group='sg-eee2ef93'):
    '''
    launch an ec2 with interferogram script
    Reasonable instances: 'c4.4xlarge' 
    '''
    cmd = ('aws ec2 run-instances --image-id {0} --count 1 --instance-type {1}' 
    ' --key-name {2} --security-group-ids {3}'
    ' --user-data file://run_interferogram.sh').format(ami,instance,key,security_group)
    print(cmd)
    #os.system(cmd)


if __name__ == '__main__':
    inps = cmdLineParse()
    create_bash_script(inps)
    print('Running Interferogram on EC2')
    launch_ec2()
    print('EC2 should close automatically when finished...')
    
    