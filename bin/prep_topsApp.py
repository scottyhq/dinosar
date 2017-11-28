#!/usr/bin/env python3
'''
Generate topsApp.xml and download scenes for a given date
with topsApp.py (ISCE 2.1.0)

Examples:
# process just subswaths 1 and 2
prep_topsApp.py -i query.geojson -m 20160910 -s 20160724

Author Scott Henderson
Updated: 10/2017
'''
import argparse
import os
import glob
import geopandas as gpd
from lxml import html
import requests

import isce
from isceobj.XmlUtil import FastXML as xml


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
    parser.add_argument('-p', type=int, dest='path', required=True,
            help='Path/Track/RelativeOrbit Number')
    parser.add_argument('-n', type=int, nargs='+', dest='swaths', required=False,
	        default=[1,2,3], choices=(1,2,3),
            help='Subswath numbers to process')
    parser.add_argument('-o', type=str, dest='orbitdir', required=False,
            default=os.environ['POEORB'],
            help='Orbit directory')
    parser.add_argument('-a', type=str, dest='auxdir', required=False,
            default=os.environ['AUXCAL'],
            help='Auxilary file directory')
    parser.add_argument('-d', type=str, dest='dem', required=False,
            help='Path to DEM file')
    parser.add_argument('-r', type=float, nargs=4, dest='roi', required=False,
            metavar=('S','N','W','E'),
	        help='Region of interest bbox [S,N,W,E]')
    parser.add_argument('-g', type=float, nargs=4, dest='gbox', required=False,
            metavar=('S','N','W','E'),
	        help='Geocode bbox [S,N,W,E]')

    return parser.parse_args()



def download_scene(downloadUrl):
    '''
    aria2c --http-auth-challenge=true --http-user=CHANGE_ME --http-passwd='CHANGE_ME' "https://api.daac.asf.alaska.edu/services/search/param?granule_list=S1A_EW_GRDM_1SDH_20151003T040339_20151003T040351_007983_00B2A6_7377&output=metalink"
    '''
    print('Downloading frame from ASF...')
    print('Requires ~/.netrc file:  ')
    print('See: https://winsar.unavco.org/software/release_note_isce-2.1.0.txt')
    cmd = 'wget -q -nc -c {}'.format(downloadUrl) #nc won't overwrite. -c continuous if unfinished -q is for 'quiet mode' since many incremental download % updates go to /var/log/cloud-init-output.log
    print(cmd)
    os.system(cmd)


def load_inventory(vectorFile):
    '''
    load merged inventory. easy!
    '''
    gf = gpd.read_file(vectorFile)
    gf['timeStamp'] = gpd.pd.to_datetime(gf.sceneDate, format='%Y-%m-%d %H:%M:%S')
    gf['sceneDateString'] = gf.timeStamp.apply(lambda x: x.strftime('%Y-%m-%d'))
    gf['dateStamp'] = gpd.pd.to_datetime(gf.sceneDateString)
    gf['utc'] = gf.timeStamp.apply(lambda x: x.strftime('%H:%M:%S'))
    gf['orbitCode'] = gf.relativeOrbit.astype('category').cat.codes
    return gf


def download_orbit(granuleName):
    '''
    Grab orbit files from ASF
    '''
    cwd = os.getcwd()
    os.chdir(os.environ['POEORB'])
    sat = granuleName[:3]
    date = granuleName[17:25]
    print('downloading orbit for {}, {}'.format(sat,date))

    url = 'https://s1qc.asf.alaska.edu/aux_poeorb'
    r = requests.get(url)
    webpage = html.fromstring(r.content)
    orbits = webpage.xpath('//a/@href')
    # get s1A or s1B
    df = gpd.pd.DataFrame(dict(orbit=orbits))
    dfSat = df[df.orbit.str.startswith(sat)]
    dayBefore = gpd.pd.to_datetime(date) - gpd.pd.to_timedelta(1, unit='d')
    dayBeforeStr = dayBefore.strftime('%Y%m%d')
    # get matching orbit file
    dfSat['startTime'] = dfSat.orbit.str[42:50]
    match = dfSat.loc[dfSat.startTime == dayBeforeStr, 'orbit'].values[0]
    cmd = 'wget -q -nc {}/{}'.format(url,match) #-nc means no clobber
    print(cmd)
    os.system(cmd)
    os.chdir(cwd)


def download_auxcal():
    '''
    Auxilary data files <20Mb, just download all of them!
    NOTE: probably can be simplified! see download_orbit
    '''
    cwd = os.getcwd()
    os.chdir(os.environ['AUXCAL'])
    print('Downloading S1 AUXILARY DATA...')
    url = 'https://s1qc.asf.alaska.edu/aux_cal'
    cmd = 'wget -q -r -l2 -nc -nd -np -nH -A SAFE {}'.format(url)
    print(cmd)
    os.system(cmd)
    os.chdir(cwd)


def find_scenes(gf, dateStr, relativeOrbit, download=True):
    '''
    Get downloadUrls for a given date
    '''
    GF = gf.query('relativeOrbit == @relativeOrbit')
    GF = gf.loc[ gf.dateStamp == dateStr ]

    if download:
        for i,row in GF.iterrows():
            download_scene(row.downloadUrl)
        download_orbit(GF.granuleName.iloc[0])

    filenames = GF.fileName.tolist()
    print('SCENES: ', filenames)
    # create symlinks #probably need to do this for multiple
    #for f in filenames:
    #    os.symlink(f, os.path.basename(f))
    return filenames


def write_topsApp_xml(inps):
    ''' use built in isce utility to write XML programatically (based on unoffical isce guide Sep2014'''
    insar = xml.Component('topsinsar')
    common = {}
    common['orbit directory'] = inps.orbitdir
    common['auxiliary data directory'] = inps.auxdir
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
    #####Catalog example
    #insar['dem'] = xml.Catalog('dem.xml') #Components include a writeXML method
    insar.writeXML('topsApp.xml', root='topsApp')



if __name__ == '__main__':
    #Try to set orbit paths with envrionment variables
    print('Looking for environment variables POEORB, AUXCAL, DEMDB...')
    if not 'POEORB' in os.environ:
        os.environ['POEORB'] = './'
    if not 'AUXCAL' in os.environ:
        os.environ['AUXCAL'] = './'

    inps = cmdLineParse()
    gf = load_inventory(inps.inventory)
    intdir = 'int-{0}-{1}'.format(inps.master, inps.slave)
    if not os.path.isdir(intdir):
        os.mkdir(intdir)
    os.chdir(intdir)
    download_auxcal()
    inps.master_scenes = find_scenes(gf, inps.master, inps.path, download=True)
    inps.slave_scenes = find_scenes(gf, inps.slave, inps.path, download=True)
    write_topsApp_xml(inps)
    print('Ready to run topsApp.py in {}'.format(intdir))
