import unittest
import sqlite3
import json
import os
import requests
import matplotlib.pyplot as plt


    

####################################### INFO ##################################

def get_data(state_code): 
    state_code = state_code.lower()
    url = 'https://api.covidtracking.com/v2/states/'+ state_code+ '/daily.json'
    response = requests.get(url)
    data = response.text
    contents_d = json.loads(data)
    print(contents_d.keys())
    data = contents_d['data']
    print(data[0]['outcomes']['death']['total']['value'])
    return data
    
def setUpDatabase(db_name, state_code):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Covid')
    cur.execute('CREATE TABLE Covid (date_id INTEGER, state TEXT, total_cases INTEGER, confirmed INTEGER, hospitalized INTEGER, deaths INTEGER)')
    date = get_data(state_code)
    for day in date: 
        date_id = day['date']
        state = day['state']
        total_cases = day['cases']['total']['value']
        confirmed = day['cases']['confirmed']['value']
        hospitalized  = day['outcomes']['hospitalized']['currently']['value']
        deaths = day['outcomes']['death']['total']['value']
        cur.execute(
            """
            INSERT OR IGNORE INTO Covid (date_id, state, total_cases, confirmed, hospitalized, deaths)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (date_id, state, total_cases, confirmed, hospitalized, deaths))
        conn.commit() 

    # return cur, conn

def setUpDatabaseMonths(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Months')
    cur.execute('CREATE TABLE Months (num_id INTEGER, month TEXT)')
    month_dict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    for m in month_dict.keys():
        num_id = month_dict[m]
        month = m
        cur.execute(
            """
            INSERT OR IGNORE INTO Months (num_id, month)
            VALUES (?, ?)
            """,
            (num_id, month))
        conn.commit()  

setUpDatabaseMonths('months.db')







#cur.execute('CREATE TABLE Covid (date_id INTEGER, PRIMARY KEY, state TEXT, total_cases INTEGER, confirmed INTEGER, deaths INTEGER)')

# def setUpDatabase('COVID_TES.db', 'CT'):
#     cur.execute('CREATE TABLE Covid (date_id INTEGER, state TEXT, total_cases INTEGER, confirmed INTEGER, hospitalized INTEGER, deaths INTEGER)')



# def main():
#     # SETUP DATABASE AND TABLE
#     # cur, conn = setUpDatabase('HR.db')
#     cur, conn = setUpDatabase('Covid_data.db')
#     get_data('CT')
#     create_species_table(cur, conn)
#     add_date('CT', cur, conn)

# def create_date_table(cur, conn):

#     Date_data = get_data(state_code)
#     list_of_days = []
#     for i in Date_data:
#         list_of_days.append(i['date'])

#     cur.execute("DROP TABLE IF EXISTS Date")
#     cur.execute("CREATE TABLE Date(date_id INTEGER PRIMARY KEY, state TEXT, total_cases INTEGER, confirmed INTEGER, deaths INTEGER)")
#     for i in range(len(species)):
#         cur.execute("INSERT INTO Species (date_id, state, total_cases, confirmed, deaths) VALUES (?,?,?,?,?)",(i,list_of_days[i-1]))
#     conn.commit()

# def add_date(state_code, cur, conn):
#     date = get_data(state_code)
#     for day in data: 
#         date_id = day['employee_id']
#         state = day['state']
#         total_cases = day['cases']['confirmed']['value']
#         confirmed = day['hire_date']
#         hospitalized  = day['outcomes']['hospitalized']['currently']['value']
#         cur.execute(
#             '''
#             INSERT OR IGNORE INTO employeese(date_id, state, total_cases, confirmed, hospitalized)'
#             ''',
#             (date_id, state, total_cases, date, confirmed, hospitalized)
#         )
        


