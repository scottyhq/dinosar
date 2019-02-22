#!/usr/bin/env python3
'''
Download a TDM (WorldDEM) data 90m and mosaic
https://download.geoservice.dlr.de/TDM90/
NOTES:
    * original resolution 30m
    * tile extents vary by latitude:
        * (0-60: 1x1 deg, 60-80: 1x2 degree, 80-90, 1x4 degree)
https://download.geoservice.dlr.de/TDM90/files/N80/W018/TDM1_DEM__30_N80W018.zip
'''

import argparse
import subprocess
import numpy as np
import sys
import os
import glob

def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='get_inventory_asf.py')
    parser.add_argument('-r', type=float, nargs=4, dest='roi', required=False,
                        metavar=('S', 'N', 'W', 'E'),
                        help='Region of interest bbox [S,N,W,E]')
    parser.add_argument('-u', type=str, dest='user', required=True,
                        default='scottyh@uw.edu',
                        help='Account email with DLR')
    parser.add_argument('-p', type=str, dest='password', required=True,
                        help='Account password')
    parser.add_argument('-l', type=str, dest='url', required=False,
                        default='https://download.geoservice.dlr.de/TDM90/files',
                        help='Download URL from DLR')
    parser.add_argument('-d', action='store_true', default=False,
                        dest='download', required=False,
                        help='Download all the files')
    parser.add_argument('-t', action='store_true', default=False,
                        dest='tiff', required=False,
                        help='Output GeoTiff in addition to VRT')
    parser.add_argument('-i', action='store_true', default=False,
                        dest='isce', required=False,
                        help='Output ISCE format in addition to VRT')
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


def download_all(urlFile, user, password):
    """Download all sequentially"""
    cmd = f'wget --auth-no-challenge --user={user} --password={password} \
     -nv -nc -c -i {urlFile}'
    run_bash_command(cmd)


def construct_urls(lats, lons, url):
    """construct urls for downloading """
    URLs = []
    for lat in lats:
        for lon in lons:
            lon = abs(lon)
            baselon = lon // 10 * 10  # works only for integers
            folder = f'N{lat:02d}/W{baselon:03d}'
            scene = f'TDM1_DEM__30_N{lat:02d}W{lon:03d}.zip'
            URLs.append(os.path.join(url, folder, scene))

    return URLs


def get_file_list(roi, url):
    """Construct file list e.g. Greenland: (SNWE) [73, 81, -49, -16] """
    # get_dem_tdx.py -r 73 81 -49 -16 -d -u scottyh@uw.edu -t -p CHANGE
    print('WARNING: hardcoded for N & W Hemisphere...')
    S, N, W, E = np.round(roi).astype('int')
    print(f'S={S}, N={N}, W={W}, E={E}')
    lats = np.arange(S, N+1)
    lons = np.arange(W, E+1)
    URLs = []
    # Break up loops based on variable latitude tiling
    lats1 = lats[(lats > 0) & (lats <= 60)]
    if len(lats1) > 0:
        URLs += construct_urls(lats1, lons, url)
    lats2 = lats[(lats > 60) & (lats <= 80)]
    lons2 = lons[lons % 2 == 0]
    if len(lats2) > 0:
        URLs += construct_urls(lats2, lons2, url)
    lats3 = lats[(lats > 80) & (lats <= 90)]
    lons3 = lons[lons % 4 == 0]
    if len(lats3) > 0:
        URLs += construct_urls(lats3, lons3, url)

    with open('download-list.txt', 'w') as f:
        f.write('\n'.join(URLs))

    return URLs


def extract():
    """ """
    cmd = "unzip '*zip'"
    run_bash_command(cmd)


def mosaic(roi, outname='mosaic.vrt', res=0.000833333333333, tiff=False, isce=False):
    """Build VRT from list of zip files """
    zips = glob.glob('*zip')
    for z in zips:
        name, ext = os.path.splitext(z)
        # register nodata value
        # cmd = 'gdal_edit.py -a_nodata -32767 {z}'
        # the hammer: replace all nodata with zero (CAREFUL! for coastlines & death valley, etc...)
        # definitely not a good idea.
        # cmd = 'gdal_calc.py -A {z} --outfile={name}.vrt --calc="A*(A>0)+0*(A<=0)" --NoDataValue=0'
        # replace no-data with zero
        cmd = f'gdal_calc.py -A /vsizip/{z}/{name}_V01_C/DEM/{name}_DEM.tif \
        --outfile={name}.tif --calc="0*(A==-32767)+A*(A!=-32767)" --NoDataValue=0'
        run_bash_command(cmd)

    # -vrtnodata 0 -tap? -te xmin ymin xmax ymax
    S, N, W, E = np.round(roi).astype('int')
    # NOTE: -te to nearest integer accomplishes requisit 1/2 pixel shift for ISCE
    # don't need -vrtnodata since it is set in the preceding gdal_calc cmd
    # NOTE: consider using dave shean's tandemx_mask.py
    cmd = f'gdalbuildvrt -r cubic -tr {res} {res} -te {W} {S} {E} {N} \
    {outname} TDM1_DEM*.tif'
    #{outname} TDM1_DEM__30*/DEM/*_DEM.tif'
    run_bash_command(cmd)

    # creates shapefile (perimeter) of masaiic
    # cmd = f'gdaltindex mosaic.shp mosaic.vrt'
    # run_bash_command(cmd)

    # -of ISCE doesn't create all the items for DEMs (e.g. 'reference')
    # NOTE: should output Cloud-optimized geotiff here!
    if tiff:
        cmd = f'gdal_translate mosaic.vrt mosaic.tif'
        run_bash_command(cmd)
    if isce:
        cmd = f'gdal_translate -of ISCE -ot Float32 mosaic.tif mosaic-isce.dem.wgs84'
        run_bash_command(cmd)
        cmd = f'gdal_translate -of VRT mosaic-isce.dem.wgs84 mosaic-isce.dem.wgs84.vrt'
        print('NOTE: add manually to mosaic-isce.dem.wgs84.xml')
        print('''
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
        <value>mosaic-isce.dem.wgs84.vrt</value>
        <doc>For example name of vrt metadata.</doc>
    </property>''')


def main(parser):
    """Run as a script with args coming from argparse."""
    args = parser.parse_args()
    if args.download:
        get_file_list(args.roi, args.url)
        download_all('download-list.txt', args.user, args.password)
        extract()
    mosaic(args.roi, tiff=args.tiff, isce=args.isce)


if __name__ == '__main__':
    parser = cmdLineParse()
    main(parser)
