import requests
import json
import urllib.request
import urllib.parse
import ssl
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_popular_times(item, api_key):
    place_id = item['place_id']

    # use the place id to get the map url of the location
    url = "https://maps.googleapis.com/maps/api/place/details/json?place_id={}&key={}".format(place_id, api_key)

    response = requests.request("GET", url, headers={}, data={})
    obj = json.loads(response.text)
    thing = obj['result'].keys()

    url = obj['result']['url']

    # use selenium to open the url to scrape the popular times
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    html = driver.page_source
    bs4_obj = BeautifulSoup(html, "html.parser")
    divs = bs4_obj.find_all('div')

    current_popularity = ''
    popular_times = {}

    # these keys are DOM element attributes, the elements with these attribute values holds the popular time data
    date_dict = {
        '0': 'Sunday',
        '1': 'Monday',
        '2': 'Tuesday',
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday',
        '*6': 'Saturday'
    }
    date_keys = list(date_dict.keys())

    target_html = None
    current_popularity = None

    # go through all the divs to find the popular times section and the current popularity
    for div in divs:
        label = div.get('aria-label')
        if label and 'Popular times at' in label:
            target_html = div
        if label and 'Currently' in label:
            current_popularity = label

        if target_html and current_popularity:
            break

    if current_popularity:
        time_string = round(time.time())
        popular_times['current_time_and_popularity'] = {
            'time': time_string,
            'popularity': current_popularity
        }


    # if we have found the popular time section
    if target_html:
        inner_divs = target_html.find_all('div')

        for inner_div in inner_divs:
            # assume we're going to find data
            no_data = False
            jsinstance = inner_div.get('jsinstance')

            if jsinstance in date_keys:
                inner_divs2 = inner_div.find_all('div')
                time_list = []

                time_dict = {}
                for id2 in inner_divs2:
                    class_name = id2.get('class')
                    label = id2.get('aria-label')
                    if label and 'busy at' in label:
                        # this value means that theres no data from google about this day
                        if label != '% busy at .':
                            split = label.split(' busy at ')
                            pop_percent = split[0]
                            pop_time = split[1].replace('.', '')
                            time_dict[pop_time] = pop_percent
                        else:
                            no_data = True
                # if we have entries and the no_data flag is false, add the dict
                if time_dict and not no_data:
                    popular_times[date_dict[jsinstance]] = time_dict
                # if the no_data flag was flipped, add an empty entry
                elif no_data:
                    popular_times[date_dict[jsinstance]] = {}
    
    return popular_times

def map_search(api_key):
    # find locations within 5km of san ramon coordinates
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.765405%2C-121.951503&radius=10000&type=bar&key={}".format(api_key)

    # send request to google server for location details
    response = requests.request(
        "GET", 
        url, 
        headers={}, 
        data={}
    )

    obj = json.loads(response.text)

    return obj

def next_page_search(api_key, paging_token):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={}&key={}".format(paging_token, api_key)

    response = requests.request(
        "GET", 
        url, 
        headers={}, 
        data={}
    )

    obj = json.loads(response.text)

    if obj['status'] == 'INVALID_REQUEST':
        time.sleep(3)
        response = requests.request(
            "GET", 
            url, 
            headers={}, 
            data={}
        )

        obj = json.loads(response.text)

    return obj

def keep_searching(popular_times, api_key, paging_token=None):
    if paging_token:
        search = next_page_search(api_key, paging_token)
    else:
        search = map_search(api_key)
    
    results = search['results']
    next_page = search.get('next_page_token')

    for item in results:
        name = item['name']
        print(name)
        entry = get_popular_times(item, api_key)
        popular_times[name] = entry

    if next_page:
        keep_searching(popular_times, api_key, next_page)
    
    return popular_times

api_key = os.getenv('GOOGLE_API_KEY')
popular_times = {}

popular_times = keep_searching(popular_times, api_key)
print(popular_times)
