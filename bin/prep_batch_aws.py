#!/usr/bin/env python3
"""Prepare directory for running topsApp.py on AWS Batch.

Setup up batch processing w/ pre-downloaded interferograms, dem, orbits, and
aux files on EFS drive

Author: Scott Henderson (scottyh@uw.edu)
Updated: 12/2018

"""
import argparse
import os
from dinosar.archive import asf
import dinosar.isce as dice


def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description="prepare ISCE 2.1 topsApp.py")
    parser.add_argument(
        "-i",
        type=str,
        dest="inventory",
        required=True,
        help="Inventory file (query.geojson)",
    )
    parser.add_argument(
        "-p",
        type=str,
        dest="path",
        required=True,
        help="Path/Track/RelativeOrbit Number",
    )
    parser.add_argument(
        "-t",
        type=str,
        dest="template",
        required=True,
        help="Path to YAML input template file",
    )
    parser.add_argument(
        "-m", type=str, dest="master", required=True, help="Master date"
    )
    parser.add_argument("-s", type=str, dest="slave", required=True, help="Slave date")
    parser.add_argument(
        "-o", type=str, dest="orbitdir", required=False, help="orbit directory on EFS"
    )
    parser.add_argument(
        "-d", type=str, dest="dem", required=False, help="DEM file path on EFS"
    )
    parser.add_argument(
        "-r", type=str, dest="rawdir", required=False, help="raw data path on EFS"
    )
    # parser.add_argument('-a', type=str, dest='auxdir', required=False,
    #                    help='aux data path on EFS')

    return parser


def main(parser):
    """Run as a script with args coming from argparse."""
    inps = parser.parse_args()
    gf = asf.load_inventory(inps.inventory)

    # print(f'Reading from template file: {inps.template}...')
    inputDict = dice.read_yaml_template(inps.template)

    intdir = "int-{0}-{1}".format(inps.master, inps.slave)
    if not os.path.isdir(intdir):
        os.mkdir(intdir)
    os.chdir(intdir)

    master_scenes = asf.get_slc_names(gf, inps.master, inps.path)
    slave_scenes = asf.get_slc_names(gf, inps.slave, inps.path)
    # Append processing Path
    if inps.rawdir:
        master_scenes = [os.path.join(inps.rawdir, x) for x in master_scenes]
        slave_scenes = [os.path.join(inps.rawdir, x) for x in slave_scenes]

    # Update input dictionary with argparse inputs
    inputDict["topsinsar"]["master"]["safe"] = master_scenes
    inputDict["topsinsar"]["slave"]["safe"] = slave_scenes

    xml = dice.dict2xml(inputDict)
    dice.write_xml(xml)

    os.chdir("../")


if __name__ == "__main__":
    parser = cmdLineParse()
    main(parser)
