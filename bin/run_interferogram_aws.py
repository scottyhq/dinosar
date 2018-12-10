#!/usr/bin/env python3
"""Generate interferogram on AWS_BATCH.

This script executes the following steps:
    1) Sync interferogram processing directory on S3 to EFS drive
    2) Download DEM, Orbit fies, and auxillary files from ASF
    3) Download SLCs for Processing
    4) Run topsApp.py
    5) Convert output to COG with STAC-compliant metadata
"""

import os
import argparse
import sys
import subprocess
import shutil

def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='prepare ISCE 2.2.0 topsApp')
    parser.add_argument('-i', type=str, dest='int_s3', required=True,
                        help='interferogram bucket name (s3://int-name)')
    parser.add_argument('-d', type=str, dest='dem_s3', required=True,
                        help='dem location (s3://dems-are-here)')
    parser.add_argument('-c', dest='create_cogs', action='store_true',
                        default=False, help='create cloud-optimized geotiff')
    parser.add_argument('-2', dest='create_stac', action='store_true',
                        default=False, help='generate STAC metadata')
    parser.add_argument('-r', dest='removedir', action='store_true',
                        default=False, help='remove processing folder')


    return parser.parse_args()


def print_batch_params():
    """Print record of Docker container environment variables.

    print statements to stdout are recorded in AWS cloudwatch logs
    """
    # NOTE: also print instance type currently running
    print('CWD: ', os.getcwd())
    [print(x, os.environ[x]) for x in os.environ if x.startswith('AWS_BATCH')]


def run_bash_command(cmd):
    """Call a system command through the subprocess python module."""
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)


def get_proc_files(int_s3, dem_s3):
    """Download ISCE configuration files and DEM from S3."""
    cmds = [f'aws s3 sync {int_s3} .',
            f'aws s3 sync {dem_s3} .']
    for cmd in cmds:
        run_bash_command(cmd)


def create_netrc():
    """Both aria2c and wget need this for authentication."""
    # NOTE: hopefully will change to direct S3 access soon!
    nasauser = os.environ['NASAUSER']
    nasapass = os.environ['NASAPASS']
    netrcFile = os.path.expanduser('~/.netrc')
    with open(netrcFile, 'w') as f:
        f.write(f"""machine urs.earthdata.nasa.gov
        login {nasauser}
        password {nasapass}
    """)
    os.chmod(netrcFile, 0o600)


def download_slcs():
    """Download SLC images from ASF server."""
    # cmd = f'wget -q -nc --user={nasauser} --password={nasapass} \
    #        --input-file=download-links.txt'
    cmd = 'aria2c -c -x 8 -s 8 -i download-links.txt'
    run_bash_command(cmd)

def cleanup():
    """Remove specified files from processing directory."""
    cmd = 'rm -r S1*zip dem* coarse_coreg coarse_interferogram coarse_offsets \
    ESD fine_coreg fine_interferogram fine_offsets \
    geom_master masterdir PICKLE slavedir'
    #cmd = 'rm -r S1*zip dem*'
    run_bash_command(cmd)
    #

def run_isce():
    """Call topsApp.py to generate single interferogram."""
    cmd = 'topsApp.py --steps 2>&1 | tee topsApp.log'
    print(cmd)
    run_bash_command(cmd)


def convert_outputs(int_s3):
    """Convert ISCE images to cloud-friendly format."""
    cmd = f'/home/ubuntu/bin/topsApp2aws.py -i {int_s3}'
    print(cmd)
    run_bash_command(cmd)

def create_stac(intname):
    """Convert ISCE images to cloud-friendly format."""
    cmd = f'/home/ubuntu/bin/topsApp2stac.py -i {intname}'
    print(cmd)
    run_bash_command(cmd)


def main():
    """Process single interferogram."""
    inps = cmdLineParse()
    print_batch_params()
    intname = inps.int_s3.lstrip('s3://')
    if not os.path.isdir(intname): os.makedirs(intname)
    os.chdir(intname)
    if not os.path.isdir('./merged'):
        # NOTE: for large batch workflows, consider pre-downloading all onto EFS!
        # then link to directory in template file
        get_proc_files(inps.int_s3, inps.dem_s3)
        # create_netrc() #for now manually put in rootdir of EFS drive
        download_slcs()
        run_isce()


        #Note can run these afterwards!
        if inps.create_cogs:
            convert_outputs(inps.int_s3)

        if inps.create_stac:
            create_stac(intname)

    cleanup()
    # Warning, this will remove entire processing(first save desired images to S3)
    # Alternatively can remove everything but /merged directory
    if inps.removedir:
        os.chdir('../')
        shutil.rmtree(intname)


if __name__ == '__main__':
    main()
