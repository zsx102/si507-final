'''
Name: Zihao Zhu
Uniqname:zihaozhu
'''

from bs4 import BeautifulSoup
import requests
import json
import secrets 
import time
import sqlite3
from decimal import Decimal


PARKS_URL = 'https://www.latlong.net/category/national-parks-236-42.html'
BASE_URL = 'https://api.yelp.com/v3/businesses/search'
CACHE_DICT = {}
CACHE_FILE_NAME = 'cache.json'
API_KEY = secrets.API_KEY


 
def build_parks_list(url):
    '''scraping the web page and get the information of each park

    Parameters
    ----------
    url: string
        the url we want to scrape
    
    Returns
    -------
    list
        the park information
    '''
    CACHE_DICT = open_cache()
    url_text = make_url_request_using_cache(url, CACHE_DICT)

    parks_list = []
    soup = BeautifulSoup(url_text, 'html.parser')
    parks = soup.find_all("tr")[1:]
    
    for park in parks:
        title = park.find('a')['title']
        park_name = title.split(',')[0].strip()
        latitude = park.find_all('td')[1].string
        longitude = park.find_all('td')[2].string
        parks_list.append((park_name, latitude, longitude))

    return parks_list


def insert_parks_database(parks_list):
    '''insert the data into a sqlite database.

    Parameters
    ----------
    parks_list: list
        the list with all parks info
    
    Returns
    -------
    None

    '''
    connection = sqlite3.connect("Final_Project.sqlite")
    cursor = connection.cursor()
    pk = 1
    for park in parks_list:
        query = f'''INSERT INTO Parks (Id, ParkName, Latitude, Longitude)
        VALUES ({pk}, "{park[0]}", "{park[1]}", "{park[2]}")
        '''
        cursor.execute(query)
        pk += 1
        connection.commit()
    connection.close()

def get_nearby_businesses(park_id):
    '''with specific park id get 20 nearby businesses from yelp api.

    Parameters
    ----------
    park_id: int
        the id of the specific park
    
    Returns
    -------
    dict:
        the dict type of returned data.
    '''
    
    connection = sqlite3.connect("Final_Project.sqlite")
    cursor = connection.cursor()
    latitude = Decimal(cursor.execute(f'SELECT * FROM Parks WHERE Id={park_id}').fetchall()[0][-2])
    longitude = Decimal(cursor.execute(f'SELECT * FROM Parks WHERE Id={park_id}').fetchall()[0][-1])
    connection.close()

    resource_url = BASE_URL
    headers = {'Authorization': 'Bearer %s' % API_KEY}
    params = {
        'latitude' : latitude,
        'longitude' : longitude,
    }
    response = requests.get(resource_url, headers=headers, params=params)
    return response.json()

def open_cache():
    '''opens the cache file if it exists and loads the JSON into
    the CACHE_DICT  dictionary.
    if the cache file doesn't exist, creates a nwe cache dictionary

    Parameters
    ----------
    None
    
    Returns
    -------
    The opend cache
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    '''saves the parks of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''check the cache for a saved result for url. If the
    result is found, return it. Otherwise send a new request,
    save it, then return it.

    Parameters
    ----------
    url: string
        The URL for the API endpoint

    cache_dict: dictionary
        The CACHE_DICT
    
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    if (url in cache.keys()): 
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]



def insert_businesses_database(id):
    '''insert businesses data into the sqlite database align with the park id

    Parameters
    ----------
    park_id: int
        the id of the park
    
    Returns
    -------
    None

    '''
    business_dict = get_nearby_businesses(id)
    connection = sqlite3.connect("Final_Project.sqlite")
    cursor = connection.cursor()
    pk = 1
    for business in business_dict['businesses']:
        name = business['name']
        park_id = id
        rating = business['rating'] if 'rating' in business else 'NULL'
        price = business['price'] if 'price' in business else 'NULL'
        distance = business['distance'] if 'distance' in business else 'NULL'
        link = business['url'] if 'url' in business else 'NULL'
        query = f'''INSERT INTO Businesses (Id, Name, ParkId, Rating, AvgPrice, Distance, Link)
        VALUES ({pk}, "{name}", {park_id}, "{rating}", "{price}", "{distance}", "{link}")
        '''
        cursor.execute(query)
        pk += 1
        connection.commit()
    connection.close()





if __name__ == "__main__":
    parks_list = build_parks_list(PARKS_URL)
    insert_parks_database(parks_list)
    for id in range(1, len(parks_list) + 1):
        insert_businesses_database(id)
    
