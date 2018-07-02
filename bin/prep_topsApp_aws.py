#!/usr/bin/env python3
"""Prepare directory for running topsApp.py on AWS Batch.

Generate topsApp.xml, put SLCs, Orbit files, and aux data in s3 bucket for
processing with topsApp.py (ISCE 2.1.0).

Example
-------

$ prep_topsApp_aws.py -i query.geojson -m 20141130 -s 20141106 -n 1 -r 46.45 46.55 -120.53 -120.43

Author: Scott Henderson (scottyh@uw.edu)
Updated: 02/2018

"""
import argparse
import os
from dinosar.archive import asf
import dinosar.isce as dice


def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='prepare ISCE 2.1 topsApp.py')
    parser.add_argument('-i', type=str, dest='inventory', required=True,
                        help='Inventory vector file (query.geojson)')
    parser.add_argument('-m', type=str, dest='master', required=True,
                        help='Master date')
    parser.add_argument('-s', type=str, dest='slave', required=True,
                        help='Slave date')
    parser.add_argument('-p', type=str, dest='path', required=True,
                        help='Path/Track/RelativeOrbit Number')
    parser.add_argument('-n', type=int, nargs='+', dest='swaths',
                        required=False, default=[1, 2, 3], choices=(1, 2, 3),
                        help='Subswath numbers to process')
    parser.add_argument('-o', dest='poeorb', action='store_true',
                        required=False, help='Use precise orbits (True/False)')
    parser.add_argument('-d', type=str, dest='dem', required=False,
                        help='Path to DEM file')
    parser.add_argument('-r', type=float, nargs=4, dest='roi', required=False,
                        metavar=('S', 'N', 'W', 'E'),
                        help='Region of interest bbox [S,N,W,E]')
    parser.add_argument('-g', type=float, nargs=4, dest='gbox', required=False,
                        metavar=('S', 'N', 'W', 'E'),
                        help='Geocode bbox [S,N,W,E]')

    return parser


def main():
    """Run as a script with args coming from argparse."""
    inps = parser.parse_args()
    gf = asf.load_inventory(inps.inventory)
    intdir = 'int-{0}-{1}'.format(inps.master, inps.slave)
    if not os.path.isdir(intdir):
        os.mkdir(intdir)
    os.chdir(intdir)

    master_urls = asf.get_slc_urls(gf, inps.master, inps.path)
    slave_urls = asf.get_slc_urls(gf, inps.slave, inps.path)
    downloadList = master_urls + slave_urls
    inps.master_scenes = [os.path.basename(x) for x in master_urls]
    inps.slave_scenes = [os.path.basename(x) for x in slave_urls]

    if inps.poeorb:
        try:
            frame = os.path.basename(inps.master_scenes[0])
            downloadList.append(asf.get_orbit_url(frame))
            frame = os.path.basename(inps.slave_scenes[0])
            downloadList.append(asf.get_orbit_url(frame))
        except Exception as e:
            print('Trouble downloading POEORB... maybe scene is too recent?')
            print('Falling back to using header orbits')
            print(e)
            inps.poeorb = False
            pass

    dice.write_topsApp_xml(inps)

    asf.write_wget_download_file(downloadList)

    # TODO: change these to use boto3 (or at least subprocess)
    os.chdir('../')
    cmd = f'aws s3 mb s3://{intdir}'
    print(cmd)
    os.system(cmd)
    cmd = f'aws s3 sync {intdir} s3://{intdir}'
    print(cmd)
    os.system(cmd)
    print(f'Moved files to s3://{intdir}')


if __name__ == '__main__':
    parser = cmdLineParse()
    main(parser)
