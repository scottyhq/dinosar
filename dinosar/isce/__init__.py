"""Functions for ISCE software.

This module has utilities for querying the NASA Alaska Satellite Facility
Distributed Active Archive Center (`ASF DAAC`_). Designed to easily search for
Sentinel-1 SAR scenes load associated JSON metadata into a Geopandas Dataframe.

Notes
-----
This file contains library functions. To run as a script use::

    $ get_inventory_asf.py --help

.. _ASF DAAC:
   https://www.asf.alaska.edu/get-data/api/

"""
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
