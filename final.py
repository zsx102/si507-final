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


COLLEGE_URL = 'https://www.latlong.net/category/colleges-236-35.html'
BASE_URL = 'https://api.yelp.com/v3/businesses/search'
CACHE_DICT = {}
CACHE_FILE_NAME = 'cache.json'
API_KEY = secrets.API_KEY

 
def build_college_list(url):
    '''scraping the web page and get the information of each college

    Parameters
    ----------
    url: string
        the url we want to scrape
    
    Returns
    -------
    list
        the information of the college
    '''
    CACHE_DICT = open_cache()
    url_text = make_url_request_using_cache(url, CACHE_DICT)
    college_list = []
    soup = BeautifulSoup(url_text, 'html.parser')
    colleges = soup.find_all("tr")[1:]
    for index in range(0, len(colleges)):
        title = colleges[index].find('a')['title']
        if index == 6:
            name = title.split(',')[0].strip() + ', ' + title.split(',')[1].strip()
            city = title.split(',')[2].strip()
        elif index == 11 or index == 14 or index == 15:
            name = title.split(',')[0].strip()
            city = '####'
        else:
            name = title.split(',')[0].strip()
            city = title.split(',')[1].strip()
        state = title.split(',')[-2].strip()
        latitude = colleges[index].find_all('td')[-2].string
        longitude = colleges[index].find_all('td')[-1].string
        college_list.append((name, city, state, latitude, longitude))
    return college_list


def insert_colleges_database(college_list):
    '''insert the data into a sqlite database.

    Parameters
    ----------
    college_list: list
        the list with all colleges info
    
    Returns
    -------
    None

    '''
    connection = sqlite3.connect("Final_Project.sqlite")
    cursor = connection.cursor()
    pk = 1
    for college in college_list:
        query = f'''INSERT INTO Colleges (Id, Name, City, State, Latitude, Longitude)
        VALUES ({pk}, "{college[0]}", "{college[1]}", "{college[2]}",  "{college[3]}", "{college[4]}")
        '''
        cursor.execute(query)
        pk += 1
        connection.commit()
    connection.close()

def get_nearby_businesses(college_id):
    '''Get nearby businesses from yelp api with specific college id

    Parameters
    ----------
    college_id: int
        the id of the specific college
    
    Returns
    -------
    dict:
        the dict type of returned data.
    '''
    
    connection = sqlite3.connect("Final_Project.sqlite")
    cursor = connection.cursor()
    latitude = Decimal(cursor.execute(f'SELECT * FROM Colleges WHERE Id={college_id}').fetchall()[0][-2])
    longitude = Decimal(cursor.execute(f'SELECT * FROM Colleges WHERE Id={college_id}').fetchall()[0][-1])
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
    '''saves the colleges of the cache to disk
    
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
    '''insert businesses data into the sqlite database attached with the college id

    Parameters
    ----------
    college_id: int
        the id of the college
    
    Returns
    -------
    None

    '''
    business_dict = get_nearby_businesses(id)
    connection = sqlite3.connect("Final_Project.sqlite")
    cursor = connection.cursor()
    i = 1
    for business in business_dict['businesses']:
        name = business['name']
        college_id = id
        rating = business['rating'] if 'rating' in business else '####'
        price = business['price'] if 'price' in business else '####'
        distance = business['distance'] if 'distance' in business else '####'
        category = business['categories'][0]['title']
        query = f'''INSERT INTO Businesses (Id, Name, CollegeId, Rating, AvgPrice, Distance, Category)
        VALUES ({i}, "{name}", {college_id}, "{rating}", "{price}", "{distance}", "{category}")
        '''
        cursor.execute(query)
        i += 1
        connection.commit()
    connection.close()


if __name__ == "__main__":
    college_list = build_college_list(COLLEGE_URL)
    insert_colleges_database(college_list)
    for id in range(1, len(college_list) + 1):
        insert_businesses_database(id)
    
