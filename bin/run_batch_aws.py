#!/usr/bin/env python3
"""Script to launch topsApp.py on AWS Batch."""

import argparse
import subprocess
import sys
import os


def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='prepare ISCE 2.2 topsApp')
    parser.add_argument('-b', type=str, dest='batchmap_s3', required=True,
                        help='processing list (s3://my-batch-job/pairs.txt)')
    parser.add_argument('-d', type=str, dest='dem_s3', required=True,
                        help='dem location (s3://isce-dems)')
    return parser.parse_args()


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


def get_batch_mapping(list_s3):
    """Get map between AWS batch array job number and interferogram."""
    cmd = f'aws s3 cp {list_s3} .'
    localFile = os.path.basename(list_s3)
    run_bash_command(cmd)
    with open(localFile) as f:
        pairs = [line.rstrip() for line in f]
        mapping = dict(enumerate(pairs))

    return mapping


def main():
    """Launch processing of single interferogram."""
    inps = cmdLineParse()

    mapping = get_batch_mapping(inps.batchmap_s3)
    index = int(os.environ['AWS_BATCH_JOB_ARRAY_INDEX'])
    pair = mapping[index]
    print(f'Batch index: {index}, Processing pair: {pair}')
    # Temporary Cludge! need to add these scripts/dinosar to docker image
    int_s3 = f's3://{pair}'
    cmd = f'/home/ubuntu/bin/run_interferogram_aws.py -i {int_s3} -d {inps.dem_s3}'
    print(cmd)
    run_bash_command(cmd)


if __name__ == '__main__':
    main()
