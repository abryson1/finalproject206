from tkinter.tix import INTEGER
import unittest
import sqlite3
import json
import time
import csv
import os
import requests
import matplotlib.pyplot as plt
import numpy as np


####################################### set up db ##################################
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn 

###################### create tables #########################
def create_table1(cur, conn):
    cur, conn = setUpDatabase('joint_data_bases.db')
    cur.execute('CREATE TABLE IF NOT EXISTS Covidtest3(id_num INTEGER, date_id INTEGER, year TEXT, month INTEGER, state TEXT, total_cases INTEGER, confirmed INTEGER, hospitalized INTEGER, deaths INTEGER, dailychg_cases INTEGER)')
    conn.commit()

def create_table2(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS CovidM2(id_num INTEGER, year INTEGER, month TEXT, new_cases INTEGER)')
    conn.commit()

###################### clean data + calculations #########################
def get_data(state_code): 
    state_code = state_code.lower()
    url = 'https://api.covidtracking.com/v2/states/'+ state_code+ '/daily.json'
    response = requests.get(url)
    data = response.text
    contents_d = json.loads(data)
    date = contents_d['data']
    data = []
    for i in range(0, 365):
        id_num = i + 1 
        date_id = date[i]['date']
        year = date_id[0:4]
        month = date_id[5:7]
        state = date[i]['state']
        total_cases = date[i]['cases']['total']['value']
        confirmed = date[i]['cases']['confirmed']['value']
        hospitalized = date[i]['outcomes']['hospitalized']['currently']['value']
        deaths = date[i]['outcomes']['death']['total']['value']
        ## CALC 1 
        ### data is cumulative so needed to find the daily increase in cases 
        ### subtracted current day from the day before to find the increase in cases

        if date[i] == date[-1] or total_cases == None:
            dailychg_cases = 'No Previous Data'
        else:
            dailychg_cases = int(total_cases) - int(date[i+1]['cases']['total']['value'])

        data.append((id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases))
    return data
###################### data calculation by month #########################

def new_cases_per_month(cur, conn):
    ### data is pulled from the data base
    cur.execute('SELECT * FROM Covidtest3')
    results = cur.fetchall()
    conn.commit()
    ### the data on increases in covid cases is aggregated based on year and month from daily increases 
    ### interating through the selected inputs and 
    average = {}
    lst = []
    for i in results:
        year = i[2]
        month = i[3]
        year_m_tup = (year, month)
        dailychg_cases = i[-2]
        if year_m_tup in average:
            if type(dailychg_cases) == int:
                new_c = average[year_m_tup] + dailychg_cases
                average[year_m_tup] = new_c
        else: 
            average[year_m_tup] = dailychg_cases
    id_num = 0
    for m in average.keys():
        id_num += 1
        year = m[0]
        month = m[1]
        new_cases = average[m]
        lst.append((id_num, year, month, new_cases))
    return lst

###################### insert data into table and limit to 25 #########################

def add_Info(data, cur, conn):
    id = None 
    cur.execute('SELECT id_num FROM Covidtest3 WHERE id_num = (SELECT MAX(id_num) from Covidtest3)')
    id = cur.fetchone()
    if  id != None:
        id = id[0] + 1
    else:
        id = 1
    stop =  id  + 25
    print("id after grabbing max", id)
    print('stop at', stop)
    for (id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases) in data:
        # if id_num == 26:
        #     print(id_num, "printing start id num\n")
        if  id <= id_num < stop: 
            cur.execute('INSERT OR IGNORE INTO Covidtest3(id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases))
            conn.commit()
            if  id_num == data[-1][0]:
                print('all data is entered')
        elif id_num == stop: 
            print('so far '+ str(id_num - 1) + ' days have been entered')
            if  id_num == data[-1][0]:
                print('all data is entered')
    

def add_Info_months(data, cur, conn):
    id = None 
    cur.execute('SELECT id_num FROM CovidM2 WHERE id_num = (SELECT MAX(id_num) from CovidM2)')
    id = cur.fetchone()
    if id != None:
        id = id[0] + 1
    else:
        id = 1 
    stop = id + 13 
    #### ONLY 13 MONTHS OF DATA NEEDED TO LIMIT SO DATA WAS NOT DUPLICATED 
    print(data)
    for id_num, year, month, new_cases in data:
        if  id <= id_num < stop:
            cur.execute("""INSERT OR IGNORE INTO CovidM2 VALUES (?, ?, ?, ?)""", (id_num, year, month, new_cases))
            conn.commit()
            if  id_num == data[-1][0]:
                print('all data is entered')
        elif id_num == stop: 
            print('so far '+ str(id_num - 1) + ' number of days have been entered')
            if  id_num == data[-1][0]:
                print('all data is entered')


#################################################################
# Write out the calculated data to a file as text 

def change_case_calc(filename, cur, conn):
    path = os.path.abspath(os.path.dirname(__file__))
    file = os.path.join(path, filename) 

    cur.execute(
    """ SELECT CovidM2.new_cases, Months.month, CovidM2.month, CovidM2.year
    FROM CovidM2 JOIN Months
    ON CovidM2.month = Months.id
    """)
    results = cur.fetchall()
    conn.commit()
    year_dict = {}

    for i in results:
        key = str(i[1]) + " " + str(i[-1])
        value = int(i[0])
        year_dict[key] = value

    with open(file, 'w') as f:
        w = csv.writer(f)
        w.writerow(["month and year","monthly increase in cases"])
        for combo in year_dict.keys():
            row = [combo, year_dict[combo]]
            w.writerow(row)

    return year_dict

####################### Write out the calculated data to a file as text ##########################

def get_all_covid_data(filename, cur, conn):
    path = os.path.abspath(os.path.dirname(__file__))
    file = os.path.join(path, filename) 
    cur.execute('SELECT * FROM Covidtest3')
    results = cur.fetchall()
    conn.commit()
    dict = {}
    for i in results:
        key = str(i[1])
        value = int(i[-1])
        dict[key] = value
    with open(file, 'w') as f:
        w = csv.writer(f)
        w.writerow(["day"," increase in cases"])
        for combo in dict.keys():
            row = [combo, dict[combo]]
            w.writerow(row)
    return dict

############################ VISUAL 1 #########################


def daily_covid_vis(filename, cur, conn):
    data = get_all_covid_data(filename, cur, conn)
    x_values = list(data.keys())
    y_values = list(data.values())
    plt.scatter(x_values, y_values)
    plt.xticks(rotation = -90) 
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.grid(axis = 'y', color = 'green', linestyle = '--', linewidth = 0.5)
    plt.xlabel('Days')
    plt.ylabel('Number of New Daily Cases')
    plt.title('Number of New Confirmed Case per Day')
    plt.tight_layout()
    plt.show()
    return 
############################ VISUAL 2 #########################


def get_covid_data_visual(filename, cur, conn):
    data = change_case_calc(filename, cur, conn)
    x_values = list(data.keys())
    y_values = list(data.values())
    plt.bar(x_values, y_values, color ='blue', width = 0.4)
    plt.xticks(rotation = -90) 
    plt.grid(axis = 'y', color = 'green', linestyle = '--', linewidth = 0.5)
    plt.ylabel('Number of New Monthly Cases')
    plt.xlabel('Months Recorded')
    plt.title('Number of Confirmed Case by Month')
    plt.tight_layout()
    plt.show()
    return 

############################ MAIN #########################
def main():
    cur, conn = setUpDatabase('joint_data_bases.db')
    create_table2(cur, conn)
    create_table1(cur, conn)
    data = get_data('CT')

    add_Info(data, cur, conn)
    time.sleep(1)

    data2 = new_cases_per_month(cur, conn)
    add_Info_months(data2, cur, conn)

    get_all_covid_data('daily_covid_data.csv', cur, conn)
    daily_covid_vis('daily_covid_data.csv', cur, conn)
    get_covid_data_visual('change_in_cases.csv', cur, conn)


if __name__ == '__main__':
    main()