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


def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='prepare ISCE 2.1.0 topsApp')
    parser.add_argument('-i', type=str, dest='int_s3', required=True,
                        help='interferogram bucket name (s3://int-name)')
    parser.add_argument('-d', type=str, dest='dem_s3', required=True,
                        help='dem location (s3://dems-are-here)')

    return parser.parse_args()


def print_batch_params():
    """Print record of Docker container environment variables.

    print statements to stdout are recorded in AWS cloudwatch logs
    """
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


def get_proc_files(int_s3, dem_s3, aux_s3='s3://sentinel1-auxdata'):
    """Download ISCE configuration files and DEM from S3."""
    cmds = [f'aws s3 sync {int_s3} .',
            f'aws s3 sync {dem_s3} .',
            f'aws s3 sync {aux_s3} .']
    for cmd in cmds:
        run_bash_command(cmd)


def create_netrc():
    """Both aria2c and wget need this for authentication."""
    nasauser = os.environ['NASAUSER']
    nasapass = os.environ['NASAPASS']
    netrcFile = os.path.expanduser('~/.netrc')
    with open(netrcFile) as f:
        f.write(f"""machine urs.earthdata.nasa.gov
    login {nasauser}
    password {nasapass}
    """)
    os.chmod(netrcFile, 0o600)


def download_slcs():
    """Download SLC images from ASF server."""
    nasauser = os.environ['NASAUSER']
    nasapass = os.environ['NASAPASS']
    cmd = f'wget -q -nc --user={nasauser} --password={nasapass} \
            --input-file=download-links.txt'
    # NOTE: look into speedups with parall downloads or direct S3 access!
    # cmd = 'aria2c -x 8 -s 8 -i download-links.txt'
    # NOTE: don't print this command since it contains password info.
    run_bash_command(cmd)


def run_isce():
    """Call topsApp.py to generate single interferogram."""
    cmd = 'topsApp.py 2>&1 topsApp.log'
    print(cmd)
    run_bash_command(cmd)


def convert_outputs(int_s3):
    """Convert ISCE images to cloud-friendly format."""
    cmd = f'isce2aws.py {int_s3}'
    print(cmd)
    run_bash_command(cmd)


def main():
    """Process single interferogram."""
    inps = cmdLineParse()
    print_batch_params()
    intname = os.path.basename(inps.int_s3)
    os.mkdir(intname)  # NOTE: will fail if directory already exists
    os.chdir(intname)
    get_proc_files(inps.int_s3, inps.dem_s3)
    download_slcs()
    run_isce()

    os.chdir('../')
    convert_outputs(intname)

    # delete entire processing directory, (first save desired images to S3)
    # rmtree(intname)


if __name__ == '__main__':
    main()
