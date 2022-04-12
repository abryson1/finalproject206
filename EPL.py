import requests 
import json
import sys
import os
import matplotlib
import sqlite3
import unittest
import csv
import matplotlib.pyplot as plt
import tweepy


#### EPL CODE USE THIS 

apikey = "309b5f90-ba8a-11ec-a85d-61050b9d6978"

import requests
def get_england_code(country_name): 
    apikey = "309b5f90-ba8a-11ec-a85d-61050b9d6978"
    continent = 'Europe'
    url = 'https://app.sportdataapi.com/api/v1/soccer/countries?'+ 'apikey='+ apikey + '&continent='+ continent 
    response = requests.get(url)
    data = response.text
    contents_d = json.loads(data)
    info = contents_d['data']
    info_keys = info.keys()
    england_code = []
    country_name = country_name.upper()
    for i in info_keys:
        if info[i]['name'].upper() == country_name:
            england_code.append(i)
    print(england_code[0])
    return england_code[0]

## england is 41 
print(get_england_code('england'))
# country_id = 41

def get_league_info(country_id):
     url = 'https://app.sportdataapi.com/api/v1/soccer/leagues?'+ 'apikey='+ apikey + '&country_id=' + country_id
     response = requests.get(url)
     data = response.text
     contents_d = json.loads(data)
     print(contents_d)

get_league_info('41')  
# analysis tone of text => sad, bull, 
# engagement => number of likes and comments 
# negative / postive / neutral 

