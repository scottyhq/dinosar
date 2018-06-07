
from dinosar.archive import asf
import requests


def test_url():
    ''' Just make sure the URL exists '''
    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    response = requests.get(baseurl)
    assert response.status_code == 200

def test_json():
    ''' Make sure response resturns valid geojson '''
    print('todo')

def test_sentinel1_query():
    ''' For a given timespan and roi, we know how many scenes are in the archive '''
    print('todo')
