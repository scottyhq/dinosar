from dinosar.archive import asf

import requests
import os.path


def test_get_list():
    """Check specific file in inventory.

    Comma-separated list of specific granules. Large lists will need to utilize
    a POST request. Note: specifying a granule list will cause most other
    keywords to be ignored including format and output. Granule_list output
    is metalink only.

    """
    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    granules = [
        'S1B_IW_SLC__1SDV_20171117T015310_20171117T015337_008315_00EB6C_40CA',
        'S1A_IW_SLC__1SSV_20150526T015345_20150526T015412_006086_007E23_34D6',
        ]
    paramDict = dict(granule_list=granules,
                     output='METALINK')
    r = requests.get(baseurl, params=paramDict, verify=False, timeout=(5, 10))

    assert r.status_code == 200


def test_get_inventory():
    """Default region of interst query should work.
    """
    asf.query_asf([0.611, 1.048, -78.196, -77.522], 'S1A')
    assert os.path.isfile('query_S1A.json')
    asf.query_asf([0.611, 1.048, -78.196, -77.522], 'S1B')
    assert os.path.isfile('query_S1B.json')


def test_query_keywords():
    """Check keywords valid in ASF REST API.

    https://www.asf.alaska.edu/get-data/learn-by-doing/
    keywords = [absoluteOrbit,asfframe,maxBaselinePerp,minBaselinePerp,
    beamMode,beamSwath,collectionName,maxDoppler,minDoppler,maxFaradayRotation,
    minFaradayRotation,flightDirection,flightLine,frame,granule_list,
    maxInsarStackSize,minInsarStackSize,intersectsWith,lookDirection,
    offNadirAngle,output,platform,polarization,polygon,processingLevel,
    relativeOrbit,maxResults,processingDate,start or end acquisition time,
    slaveStart/slaveEnd
    """
    # TODO: implement a test
    pass
