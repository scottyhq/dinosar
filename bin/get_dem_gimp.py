#!/usr/bin/env python3
"""
Convert GIMP DEM to use w/ ISCE
https://nsidc.org/data/nsidc-0715/versions/1

NOTE: requires gdal>=2.4 and .netrc with URS credentials

# NOTE this has holes:
TILE=https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0715_MEASURES_gimp_dem/reg/tile_0_1_reg_30m_day.tif

Should use the 'fit' smoothed version for processing:
/fit/
tile_0_1_fit_30m_dem.tif
tile_0_1_fit_30m_err.tif
tile_0_1_fit_30m_hillshade.tif

TILE=https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0715_MEASURES_gimp_dem/fit/tile_0_1_fit_30m_day.tif
GDAL_HTTP_COOKIEJAR=.urs_cookies GDAL_HTTP_COOKIEFILE=.urs_cookies gdalinfo /vsicurl/$TILE
"""
import argparse
import subprocess
import numpy as np
import sys
import os
import glob

# GDAL ENVIRONMENT SETTINGS
os.environ["GDAL_HTTP_COOKIEJAR"] = ".urs_cookies"
os.environ["GDAL_HTTP_COOKIEFILE"] = ".urs_cookies"


def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description="get_inventory_asf.py")
    parser.add_argument(
        "-r",
        type=float,
        nargs=4,
        dest="roi",
        required=False,
        metavar=("S", "N", "W", "E"),
        help="Region of interest bbox [S,N,W,E]",
    )
    parser.add_argument(
        "-l",
        type=str,
        dest="url",
        required=False,
        default="https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0715_MEASURES_gimp_dem/fit/",
        help="Download URL from DLR",
    )
    parser.add_argument(
        "-d",
        action="store_true",
        default=False,
        dest="download",
        required=False,
        help="Download all the files",
    )
    parser.add_argument(
        "-m",
        action="store_true",
        default=False,
        dest="mosaic",
        required=False,
        help="Create a mosaic",
    )
    parser.add_argument(
        "-i",
        action="store_true",
        default=False,
        dest="isce",
        required=False,
        help="Output ISCE format in addition to VRT",
    )
    return parser


def run_bash_command(cmd):
    """Call a system command through the subprocess python module."""
    print(cmd)
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)


def download(url, rows=range(6), cols=range(6)):
    """Build VRT from list of zip files """
    for i in rows:
        for j in cols:
            file = f"tile_{i}_{j}_fit_30m_dem.tif"
            name, ext = os.path.splitext(file)
            urlpath = os.path.join(url, file)
            cmd = f'gdal_calc.py -A /vsicurl/{urlpath} \
            --outfile={name}_calc.tif --calc="0*(A==-9999)+A*(A!=-9999)" --NoDataValue=0'
            run_bash_command(cmd)


def change_nodata():
    tifs = glob.glob("tile*tif")
    for tif in tifs:
        name, ext = os.path.splitext(tif)
        cmd = f'gdal_calc.py -A {tif} --outfile={name}_calc.tif \
        --calc="0*(A==-9999)+A*(A!=-9999)" --NoDataValue=0'
        run_bash_command(cmd)


def mosaic(roi, outname="mosaic.vrt", res=0.000833333333333, tiff=False, isce=False):
    """Build VRT from list of zip files """
    # gdalbuildvrt mosaic.vrt tile*calc.tif
    # gdalwarp -t_srs EPSG:4326 -r cubic -tr 0.000833333333333 0.000833333333333 -te -49 73 -16 81 mosaic.vrt mosaic.tif
    S, N, W, E = np.round(roi).astype("int")
    cmd = f"gdalbuildvrt mosaic.vrt tile*calc.tif"
    run_bash_command(cmd)

    if tiff:
        cmd = f"gdalwarp -t_srs EPSG:4326 -r cubic -te {W} {S} {E} {N} \
         -tr {res} {res} mosaic.vrt mosaic.tif"
        run_bash_command(cmd)
    if isce:
        cmd = (
            f"gdal_translate -of ISCE -ot Float32 mosaic.tif mosaic-gimp-isce.dem.wgs84"
        )
        run_bash_command(cmd)
        cmd = f"gdal_translate -of VRT mosaic-gimp-isce.dem.wgs84 mosaic-gimp-isce.dem.wgs84.vrt"
        print("NOTE: add manually to mosaic-isce.dem.wgs84.xml")
        print(
            """
    <property name="family">
        <value>demimage</value>
        <doc>Instance family name</doc>
    </property>
    <property name="name">
        <value>demimage_name</value>
        <doc>Instance name</doc>
    </property>
    <property name="image_type">
        <value>dem</value>
        <doc>Image type used for displaying.</doc>
    </property>
    <property name="reference">
        <value>WGS84</value>
        <doc>Geodetic datum</doc>
    </property>
    <property name="extra_file_name">
        <value>mosaic-gimp-isce.dem.wgs84.vrt</value>
        <doc>For example name of vrt metadata.</doc>
    </property>"""
        )


def main(parser):
    """Run as a script with args coming from argparse."""
    args = parser.parse_args()
    if args.download:
        download(args.url)
    else:
        change_nodata()
    if args.mosaic:
        mosaic(args.roi, tiff=args.tiff, isce=args.isce)

    # To create XML metadata for tiff file use in ISCE:
    # gdal2isce.py -i mosaic.tif -d


if __name__ == "__main__":
    parser = cmdLineParse()
    main(parser)
