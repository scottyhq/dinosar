"""Functions for querying ASF archive.

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

import requests
import json
import shapely.wkt
from shapely.geometry import box, mapping
import pandas as pd
import geopandas as gpd
import os
import subprocess
import shutil
import sys
from lxml import html


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


def inventory2s3(gf, s3bucket):
    """Mirror Sentinel1 inventory for specific path on S3.

    Assumes geodataframe has already been filtered for desired frames.
    """
    filenames = gf.downloadUrl.tolist()
    write_wget_download_file(filenames)

    nasauser = os.environ['NASAUSER']
    nasapass = os.environ['NASAPASS']
    os.mkdir('tmp')
    os.chdir('tmp')
    cmd = f'wget -q -nc --user={nasauser} --password={nasapass} --input-file=download-links.txt'
    # NOTE: don't print this command since it contains password info.
    run_bash_command(cmd)

    cmd = f'aws s3 sync . s3://{s3bucket}'
    run_bash_command(cmd)
    os.chdir('tmp')
    shutil.rmtree('tmp')


def load_asf_json(jsonfile: str):
    """Convert JSON metadata from ASF query to dataframe.

    JSON metadata returned from ASF DAAC API is loaded into a geopandas
    GeoDataFrame, with timestamps converted to datatime objects.

    Parameters
    ----------
    jsonfile : str
        Path to the json file from an ASF API query.

    Returns
    -------
    gf :  GeoDataFrame
        A geopandas GeoDataFrame

    """
    with open(jsonfile) as f:
        meta = json.load(f)[0]  # list of scene dictionaries

    df = pd.DataFrame(meta)
    polygons = df.stringFootprint.apply(shapely.wkt.loads)
    gf = gpd.GeoDataFrame(df,
                          crs={'init': 'epsg:4326'},
                          geometry=polygons)

    gf['timeStamp'] = pd.to_datetime(gf.sceneDate, format='%Y-%m-%d %H:%M:%S')
    gf['sceneDateString'] = gf.timeStamp.apply(
                                            lambda x: x.strftime('%Y-%m-%d'))
    gf['dateStamp'] = pd.to_datetime(gf.sceneDateString)
    gf['utc'] = gf.timeStamp.apply(lambda x: x.strftime('%H:%M:%S'))
    gf['orbitCode'] = gf.relativeOrbit.astype('category').cat.codes

    return gf


def summarize_orbits(gf):
    """Break inventory into separate dataframes by relative orbit.

    For each relative orbit in GeoDataFame, save simple summary of acquisition
    dates to acquisitions_[orbit].csv.

    Parameters
    ----------
    gf : GeoDataFrame
        a pandas geodataframe from load_asf_json

    """
    for orb in gf.relativeOrbit.unique():
        df = gf.query('relativeOrbit == @orb')
        gb = df.groupby('sceneDateString')
        nFrames = gb.granuleName.count()
        df = df.loc[:, ['sceneDateString', 'dateStamp', 'platform']]
        # Only keep one frame per date
        DF = df.drop_duplicates('sceneDateString').reset_index(drop=True)
        DF.sort_values('sceneDateString', inplace=True)
        DF.reset_index(inplace=True, drop=True)
        timeDeltas = DF.dateStamp.diff()
        DF['dt'] = timeDeltas.dt.days
        DF.loc[0, 'dt'] = 0
        DF['dt'] = DF.dt.astype('i2')
        DF['nFrames'] = nFrames.values
        DF.drop('dateStamp', axis=1, inplace=True)
        # DF.set_index('date') # convert to datetime difference
        outFile = 'acquisitions_{}.csv'.format(orb)
        print(f'Saving {outFile} ...')
        DF.to_csv(outFile)


def save_geojson_footprints(gf):
    """Save all frames from each date as separate geojson file.

    JSON footprints with metadata are easily visualized if pushed to GitHub.
    This saves a bunch of [date].geojson files in local directory.

    Parameters
    ----------
    gf : GeoDataFrame
        a pandas geodataframe from load_asf_json

    """
    attributes = ('granuleName', 'downloadUrl', 'geometry')
    gb = gf.groupby(['relativeOrbit', 'sceneDateString'])
    S = gf.groupby('relativeOrbit').sceneDateString.unique()
    for orbit, dateList in S.iteritems():
        os.makedirs(orbit)
        for date in dateList:
            dftmp = gf.loc[gb.groups[(orbit, date)], attributes].reset_index(drop=True)
            outname = os.path.join(orbit, date+'.geojson')
            dftmp.to_file(outname, driver='GeoJSON')


def summarize_inventory(gf):
    """Get basic statistics for each track.

    For each relativeOrbit in the dataframe, return the first date, last date,
    number of dates, number of total frames, flight direction (ascending, or
    descending), and UTC observation time. Also calculates approximate archive
    size by assuming 5Gb * total frames. Prints results to screen and also
    saves inventory_summary.csv.

    Parameters
    ----------
    gf : GeoDataFrame
        a pandas geodataframe from load_asf_json

    """
    dfS = pd.DataFrame(index=gf.relativeOrbit.unique())
    dfS['Start'] = gf.groupby('relativeOrbit').sceneDateString.min()
    dfS['Stop'] = gf.groupby('relativeOrbit').sceneDateString.max()
    dfS['Dates'] = gf.groupby('relativeOrbit').sceneDateString.nunique()
    dfS['Frames'] = gf.groupby('relativeOrbit').sceneDateString.count()
    dfS['Direction'] = gf.groupby('relativeOrbit').flightDirection.first()
    dfS['UTC'] = gf.groupby('relativeOrbit').utc.first()
    dfS.sort_index(inplace=True, ascending=False)
    dfS.index.name = 'Orbit'
    dfS.to_csv('inventory_summary.csv')
    print(dfS)
    size = dfS.Frames.sum()*5 / 1e3
    print('Approximate Archive size = {} Tb'.format(size))


def merge_inventories(s1Afile, s1Bfile):
    """Merge Sentinel 1A and Sentinel 1B into single dataframe.

    ASF API queries are done per satellite, so queries for S1A and S1B need to
    be merged into a single dataframe.

    Parameters
    ----------
    s1Afile : str
        Path to the json file from an ASF API query for Sentinel-1A data.
    s1Bfile : str
        Path to the json file from an ASF API query for Sentinel-1B data.

    Returns
    -------
    gf :  GeoDataFrame
        A geopandas GeoDataFrame

    """
    print('Merging S1A and S1B inventories')
    gfA = load_asf_json(s1Afile)
    gfB = load_asf_json(s1Bfile)
    gf = pd.concat([gfA, gfB])
    gf.reset_index(inplace=True)

    return gf


def save_inventory(gf, outname='query.geojson', format='GeoJSON'):
    """Save inventory GeoDataFrame as a GeoJSON file.

    Parameters
    ----------
    gf : GeoDataFrame
        a pandas geodataframe from load_asf_json.
    outname : str
        name of output file.
    format : str
        OGR-recognized output format.

    """
    # WARNING: overwrites existing file
    if os.path.isfile(outname):
        os.remove(outname)
    # NOTE: can't save pandas Timestamps!
    # ValueError: Invalid field type <class 'pandas._libs.tslib.Timestamp'>
    gf.drop(['timeStamp', 'dateStamp'], axis=1, inplace=True)
    gf.to_file(outname, driver=format)
    print('Saved inventory: ', outname)


def load_inventory(inventoryJSON):
    """Load inventory saved with asf.archive.save_inventory().

    Parameters
    ----------
    inventoryJSON : str
        dinsar inventory file (query.geojson)

    Returns
    -------
    gf :  GeoDataFrame
        A geopandas GeoDataFrame

    """
    gf = gpd.read_file(inventoryJSON)
    gf['timeStamp'] = gpd.pd.to_datetime(gf.sceneDate,
                                         format='%Y-%m-%d %H:%M:%S')
    gf['sceneDateString'] = gf.timeStamp.apply(
        lambda x: x.strftime('%Y-%m-%d'))
    gf['dateStamp'] = gpd.pd.to_datetime(gf.sceneDateString)
    gf['utc'] = gf.timeStamp.apply(lambda x: x.strftime('%H:%M:%S'))
    gf['relativeOrbit'] = gf.relativeOrbit.astype('int')
    gf.sort_values('relativeOrbit', inplace=True)
    gf['orbitCode'] = gf.relativeOrbit.astype('category').cat.codes

    return gf


def download_scene(downloadUrl):
    """Download a granule from ASF.

    Launches an external `wget` command to download a single granule from ASF.
    Note that if stored on S3, in us-east-1 region.

    Parameters
    ----------
    downloadUrl : str
        A valid download URL for an ASF granule.

    """
    print('Requires ~/.netrc file')
    cmd = 'wget -nc -c {downloadUrl}'
    run_bash_command(cmd)


def query_asf(snwe, sat='SA', format='json'):
    """Search ASF with [south, north, west, east] bounds.

    Saves result to local file: query_{sat}.{format}

    Parameters
    ----------
    snwe : list
        bounding coordinates [south, north, west, east].
    sat : str
        satellite id (either 'S1A' or 'S1B')
    format : str
        output format of ASF API (json, csv, kml, metalink)

    Notes
    ----------
    API keywords = [absoluteOrbit,asfframe,maxBaselinePerp,minBaselinePerp,
    beamMode,beamSwath,collectionName,maxDoppler,minDoppler,maxFaradayRotation,
    minFaradayRotation,flightDirection,flightLine,frame,granule_list,
    maxInsarStackSize,minInsarStackSize,intersectsWith,lookDirection,
    offNadirAngle,output,platform,polarization,polygon,processingLevel,
    relativeOrbit,maxResults,processingDate,start or end acquisition time,
    slaveStart/slaveEnd

    """
    print(f'Querying ASF Vertex for {sat}...')
    miny, maxy, minx, maxx = snwe
    roi = shapely.geometry.box(minx, miny, maxx, maxy)
    polygonWKT = roi.to_wkt()

    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    # relativeOrbit=$ORBIT
    data = dict(intersectsWith=polygonWKT,
                platform=sat,
                processingLevel='SLC',
                beamMode='IW',
                output=format)

    r = requests.get(baseurl, params=data, timeout=100)
    print(r.url)
    # Save Directly to dataframe
    # df = pd.DataFrame(r.json()[0])
    with open(f'query_{sat}.{format}', 'w') as j:
        j.write(r.text)


def get_orbit_url(granuleName, url='https://s1qc.asf.alaska.edu/aux_poeorb'):
    """Retrieve precise orbit file for a specific Sentinel-1 granule.

    Precise orbits available ~3 weeks after aquisition.

    Parameters
    ----------
    granuleName : str
        ASF granule name (e.g. S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA)
    url : str
        website with simple list of orbit file links

    Returns
    -------
    orbitUrl :  str
        url pointing to matched orbit file

    """
    sat = granuleName[:3]
    date = granuleName[17:25]
    print(f'downloading orbit for {sat}, {date}')
    r = requests.get(url)
    webpage = html.fromstring(r.content)
    orbits = webpage.xpath('//a/@href')
    df = gpd.pd.DataFrame(dict(orbit=orbits))
    dfSat = df[df.orbit.str.startswith(sat)].copy()
    dayBefore = gpd.pd.to_datetime(date) - gpd.pd.to_timedelta(1, unit='d')
    dayBeforeStr = dayBefore.strftime('%Y%m%d')
    dfSat.loc[:, 'startTime'] = dfSat.orbit.str[42:50]
    match = dfSat.loc[dfSat.startTime == dayBeforeStr, 'orbit'].values[0]
    orbitUrl = f'{url}/{match}'

    return orbitUrl


def get_slc_urls(gf, dateStr, relativeOrbit):
    """Get S1 frame downloadUrls for a given date and relative orbit.

    Parameters
    ----------
    gf : GeoDataFrame
        ASF inventory of S1 frames
    datStr : str
        date in string format (e.g. '2018/11/30')
    relativeOrbit : str
        relative orbit in string format (e.g. '136')

    Returns
    -------
    filenames :  list
        list of matching download url strings

    """
    try:
        GF = gf.query('relativeOrbit == @relativeOrbit')
        GF = GF.loc[GF.dateStamp == dateStr]
        filenames = GF.downloadUrl.tolist()
    except Exception as e:
        print('ERROR retrieving scenes, double check dates!')
        print(e)
        pass

    return filenames


def write_wget_download_file(fileList):
    """Write list of frame urls to a file.

    This is useful if you are running isce on a server and want to keep a
    record of download links. Writes download-links.txt to current folder.

    Parameters
    ----------
    fileList : list
        list of download url strings

    """
    with open('download-links.txt', 'w') as f:
        f.write("\n".join(fileList))


def ogr2snwe(vectorFile, buffer=None):
    """Convert ogr shape to South,North,West,East bounds.

    Parameters
    ----------
    vectorFile : str
        path to OGR-recognized vector file.
    buffer : float
        Amount of buffer distance to add to shape (in decimal degrees).

    Returns
    -------
    snwe :  list
        a list of coorinate bounds [S, N, W, E]

    """
    gf = gpd.read_file(vectorFile)
    gf.to_crs(epsg=4326, inplace=True)
    poly = gf.geometry.convex_hull
    if buffer:
        poly = poly.buffer(buffer)
    W, S, E, N = poly.bounds.values[0]
    snwe = [S, N, W, E]

    return snwe


def snwe2file(snwe):
    """Use Shapely to convert to GeoJSON & WKT.

    Save local text files in variety of formats to record bounds: snwe.json,
    snwe.wkt, snwe.txt.

    Parameters
    ----------
    snwe : list
        bounding coordinates [south, north, west, east].

    """
    S, N, W, E = snwe
    roi = box(W, S, E, N)
    with open('snwe.json', 'w') as j:
        json.dump(mapping(roi), j)
    with open('snwe.wkt', 'w') as w:
        w.write(roi.to_wkt())
    with open('snwe.txt', 'w') as t:
        snweList = '[{0:.3f}, {1:.3f}, {2:.3f}, {3:.3f}]'.format(S, N, W, E)
        t.write(snweList)
