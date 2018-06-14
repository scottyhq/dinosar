#!/usr/bin/env python3
'''
Generate topsApp.xml, put SLCs, Orbit files, and aux data in s3 bucket for
processing with topsApp.py (ISCE 2.1.0)

# NOTE: requires inventory file from get_inventory_asf.py
prep_topsApp_aws.py -i query.geojson -m 20141130 -s 20141106 -n 1 -r 46.45 46.55 -120.53 -120.43

Author: Scott Henderson (scottyh@uw.edu)
Updated: 02/2018
'''
import argparse
import os
import glob
import geopandas as gpd
from lxml import html
import requests
# Borrowed from Piyush Agram:
import FastXML as xml


def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser( description='prepare ISCE 2.1 topsApp.py')
    parser.add_argument('-i', type=str, dest='inventory', required=True,
            help='Inventory vector file (query.geojson)')
    parser.add_argument('-m', type=str, dest='master', required=True,
            help='Master date')
    parser.add_argument('-s', type=str, dest='slave', required=True,
            help='Slave date')
    parser.add_argument('-p', type=str, dest='path', required=True,
            help='Path/Track/RelativeOrbit Number')
    parser.add_argument('-n', type=int, nargs='+', dest='swaths', required=False,
	        default=[1,2,3], choices=(1,2,3),
            help='Subswath numbers to process')
    parser.add_argument('-o', dest='poeorb', action='store_true', required=False,
            help='Use precise orbits (True/False)')
    parser.add_argument('-d', type=str, dest='dem', required=False,
            help='Path to DEM file')
    parser.add_argument('-r', type=float, nargs=4, dest='roi', required=False,
            metavar=('S','N','W','E'),
	        help='Region of interest bbox [S,N,W,E]')
    parser.add_argument('-g', type=float, nargs=4, dest='gbox', required=False,
            metavar=('S','N','W','E'),
	        help='Geocode bbox [S,N,W,E]')

    return parser.parse_args()


def load_inventory(vectorFile):
    '''
    load merged (S1A and S1B) inventory
    '''
    gf = gpd.read_file(vectorFile)
    gf['timeStamp'] = gpd.pd.to_datetime(gf.sceneDate, format='%Y-%m-%d %H:%M:%S')
    gf['sceneDateString'] = gf.timeStamp.apply(lambda x: x.strftime('%Y-%m-%d'))
    gf['dateStamp'] = gpd.pd.to_datetime(gf.sceneDateString)
    gf['utc'] = gf.timeStamp.apply(lambda x: x.strftime('%H:%M:%S'))
    gf['orbitCode'] = gf.relativeOrbit.astype('category').cat.codes
    return gf


def get_orbit_url(granuleName):
    '''
    Grab orbit files from ASF
    '''
    sat = granuleName[:3]
    date = granuleName[17:25]
    #print('downloading orbit for {}, {}'.format(sat,date))
    # incomplete inventory 'https://s1qc.asf.alaska.edu/aux_poeorb/files.txt'
    url = 'https://s1qc.asf.alaska.edu/aux_poeorb'
    r = requests.get(url)
    webpage = html.fromstring(r.content)
    orbits = webpage.xpath('//a/@href')
    # get s1A or s1B
    df = gpd.pd.DataFrame(dict(orbit=orbits))
    dfSat = df[df.orbit.str.startswith(sat)].copy()
    dayBefore = gpd.pd.to_datetime(date) - gpd.pd.to_timedelta(1, unit='d')
    dayBeforeStr = dayBefore.strftime('%Y%m%d')
    # get matching orbit file
    dfSat.loc[:, 'startTime'] = dfSat.orbit.str[42:50]
    match = dfSat.loc[dfSat.startTime == dayBeforeStr, 'orbit'].values[0]
    orbitUrl = f'{url}/{match}'

    return orbitUrl


def get_slc_urls(gf, dateStr, relativeOrbit):
    '''
    Get downloadUrls for a given date
    '''
    try:
        GF = gf.query('relativeOrbit == @relativeOrbit')
        GF = GF.loc[GF.dateStamp == dateStr]
        filenames = GF.downloadUrl.tolist()
    except Exception as e:
        print(f'ERROR retrieving {val} scenes, double check dates:')
        print(e)
        pass

    return filenames

def write_wget_download_file(fileList):
    '''
    instead of downloading locally, write a download file for orbits and SLCs
    '''
    with open('download-links.txt', 'w') as f:
        f.write("\n".join(fileList))



def write_topsApp_xml(inps):
    ''' use built in isce utility to write XML programatically (based on unoffical isce guide Sep2014'''
    insar = xml.Component('topsinsar')
    common = {}
    if inps.poeorb:
        common['orbit directory'] = './'
    common['auxiliary data directory'] = './'
    #common['swath number'] = inps.subswath
    if inps.roi:
        common['region of interest'] = inps.roi
    master = {}
    master['safe'] = inps.master_scenes
    master['output directory'] = 'masterdir'
    master.update(common)
    slave = {}
    slave['safe'] = inps.slave_scenes
    slave['output directory'] = 'slavedir'
    slave.update(common)
    #####Set sub-component
    insar['master'] = master
    insar['slave'] = slave
    ####Set properties
    insar['sensor name'] = 'SENTINEL1'
    insar['do unwrap'] = True
    insar['unwrapper name'] = 'snaphu_mcf'
    insar['swaths'] = inps.swaths
    if inps.gbox:
        insar['geocode bounding box'] = inps.gbox
    #insar['geocode list'] = []
    if inps.dem:
        insar['demfilename'] = inps.dem

    insar.writeXML('topsApp.xml', root='topsApp')



if __name__ == '__main__':
    inps = cmdLineParse()
    gf = load_inventory(inps.inventory)
    intdir = 'int-{0}-{1}'.format(inps.master, inps.slave)
    if not os.path.isdir(intdir):
        os.mkdir(intdir)
    os.chdir(intdir)

    master_urls  = get_slc_urls(gf, inps.master, inps.path)
    slave_urls  = get_slc_urls(gf, inps.slave, inps.path)
    downloadList = master_urls + slave_urls
    inps.master_scenes = [os.path.basename(x) for x in master_urls]
    inps.slave_scenes = [os.path.basename(x) for x in slave_urls]

    if inps.poeorb:
        try:
            frame = os.path.basename(inps.master_scenes[0])
            downloadList.append(get_orbit_url(frame))
            frame = os.path.basename(inps.slave_scenes[0])
            downloadList.append(get_orbit_url(frame))
        except Exception as e:
            print('Trouble downloading POEORB... maybe scene is too recent?')
            print('Falling back to using header orbits')
            print(e)
            inps.poeorb = False
            pass

    write_topsApp_xml(inps)

    write_wget_download_file(downloadList)

    os.chdir('../')
    cmd = f'aws s3 mb s3://{intdir}'
    print(cmd)
    os.system(cmd)
    cmd = f'aws s3 sync {intdir} s3://{intdir}'
    print(cmd)
    os.system(cmd)
    print(f'Moved files to S3://{intdir}')
