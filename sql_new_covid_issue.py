import unittest
import sqlite3
import json
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
    cur.execute('DROP TABLE IF EXISTS Covid')
    cur.execute('CREATE TABLE IF NOT EXISTS Covid (id_num INTEGER, date_id INTEGER, year TEXT, month INTEGER, state TEXT, total_cases INTEGER, confirmed INTEGER, hospitalized INTEGER, deaths INTEGER, dailychg_cases INTEGER, dailychg_deaths INTEGER)')
    #cur.execute('CREATE TABLE IF NOT EXISTS Covid (id_num INTEGER, year INTEGER, month TEXT, new_cases INTEGER)')
    conn.commit()

def create_table2(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS CovidM2 (id_num INTEGER, year INTEGER, month TEXT, new_cases INTEGER, deaths_per_m INTEGER)')
    conn.commit()

def create_table3(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Months(id INTEGER PRIMARY KEY, month TEXT)')
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
        ### subtracted current day from the day before and 
        if date[i] == date[-1] or total_cases == None:
            dailychg_cases = 'No Previous Data'
        else:
            dailychg_cases = int(total_cases) - int(date[i+1]['cases']['total']['value'])

        if date[i] == date[-1] or deaths == None or date[i+1]['outcomes']['death']['total']['value'] == None:
            dailychg_deaths = 'No Previous Data'
        else:
            dailychg_deaths = int(deaths) - int(date[i+1]['outcomes']['death']['total']['value'])
            #print(dailychg_deaths)
        data.append((id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases, dailychg_deaths))
    #print(data)
    return data
###################### data calcs by month #########################
def new_cases_per_month(state_code):
    data = get_data(state_code)
    average = {}
    lst = []
    for i in data:
        year = i[2]
        month = i[3]
        year_m_tup = (year, month)
        dailychg_cases = i[-2]
        dailychg_deaths = i[-1]
        if year_m_tup in average:
            new_c = average[year_m_tup][0] + dailychg_cases
            new_d = average[year_m_tup][1] + dailychg_cases
            average[year_m_tup] = (new_c, new_d)
        else: 
            average[year_m_tup] = (dailychg_cases, dailychg_deaths)
    id_num = 0
    # print(average)
    for m in average.keys():
        id_num += 1
        year = m[0]
        month = m[1]
        new_cases = average[m][0]
        new_fatalities = average[m][1]
        lst.append((id_num, year, month, new_cases, new_fatalities))
    # print(lst)
    return lst

###################### insert data into table and limit to 25 #########################
def add_Info(state_code, cur, conn):
    id = None 
    cur.execute('SELECT id_num FROM Covid WHERE id_num = (SELECT MAX(id_num) from Covid)')
    id = cur.fetchone()
    data = get_data(state_code)
    if  id != None:
        id =    id[0] + 1
    else:
        id = 1
    stop =  id  + 25
    for (id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases, dailychg_deaths) in data:
        if  id <= id_num < stop: 
            cur.execute('INSERT OR IGNORE INTO Covid (id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases, dailychg_deaths) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (id_num, date_id, year, month, state, total_cases, confirmed, hospitalized, deaths, dailychg_cases, dailychg_deaths))
            conn.commit()
            if  id_num == data[-1][0]:
                print('all data is entered')
        elif id_num == stop: 
            print('so far '+ str(id_num - 1) + ' number of days have been entered')
            if  id_num == data[-1][0]:
                print('all data is entered')
    
def add_Info_monthes(state_code, cur, conn):
    id = None 
    cur.execute('SELECT id_num FROM CovidM2 WHERE id_num = (SELECT MAX(id_num) from CovidM2)')
    id = cur.fetchone()
    data = new_cases_per_month(state_code)
    if id != None:
        id = id[0] + 1
    else:
        id = 1 
    stop = id + 13 

    #### ONLY 13 MONTHS OF DATA NEEDED TO LIMIT SO DATA WAS NOT DUPLICATED 


    for id_num, year, month, new_cases, new_fatalities in data:
        if  id <= id_num < stop:
            cur.execute("""INSERT OR IGNORE INTO CovidM2 VALUES (?, ?, ?, ?,?)""", (id_num, year, month, new_cases, new_fatalities))
            conn.commit()
            if  id_num == data[-1][0]:
                print('all data is entered')
        elif id_num == stop: 
            print('so far '+ str(id_num - 1) + ' number of days have been entered')
            if  id_num == data[-1][0]:
                print('all data is entered')


###################### CREATE MONTHS TABLE BUT WILL DELETE WHEN ADD WITH RACHELS  #########################
def MonthTable(cur, conn): 
   # will remove when working in same db as rachel 
    cur.execute('CREATE TABLE IF NOT EXISTS Months(id INTEGER PRIMARY KEY, month TEXT)')
    conn.commit()
    month_dict = {'January': '01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
    for m in month_dict.keys():
        num_id = month_dict[m]
        month = m
        cur.execute(
            """
            INSERT OR IGNORE INTO Months (id, month)
            VALUES (?, ?)
            """,
            (num_id, month))
        conn.commit()  

###################### MAIN FOR DATA FROM COVID API #########################

def main():
    cur, conn = setUpDatabase('covid_data_TRIAL.db')
    create_table3(cur, conn)
    create_table2(cur, conn)
    create_table1(cur, conn)
    add_Info_monthes('CT', cur, conn)
    MonthTable(cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    add_Info('CT', cur, conn)
    # new_cases_per_month('CT')

main()

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
    # x_values = list(year_dict.keys())
    # # print(x_values)
    # y_values = list(year_dict.values())
    # print(y_values)

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
    cur.execute('SELECT * FROM Covid')
    results = cur.fetchall()
    conn.commit()
    dict = {}
    for i in results:
        key = str(i[1])
        value = int(i[-2])
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
    plt.xlabel('Number of New Daily Cases')
    plt.ylabel('Days')
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
    plt.xlabel('Number of New Monthly Cases')
    plt.ylabel('Months Recorded')
    plt.title('Number of Confirmed Case by Month')
    plt.tight_layout()
    plt.show()
    return 
############################ VISUAL 3 #########################
def get_covid_data_fatalities_visual(cur, conn):
    cur.execute(
    """ SELECT CovidM2.deaths_per_m, Months.month, CovidM2.month, CovidM2.year
    FROM CovidM2 JOIN Months
    ON CovidM2.month = Months.id
    """)
    results = cur.fetchall()
    print(results)
    conn.commit()
    d = {}
    for i in results:
        key = str(i[2]) + " " + str(i[-1])
        value = i[0]
        print(value)
        d[key] = value
    x_values = list(d.keys())
    y_values = list(d.values())
    plt.bar(x_values, y_values, color ='black', width = 0.4)
    plt.grid(axis = 'y', color = 'grey', linestyle = '--', linewidth = 0.5)
    plt.xticks(rotation = -90) 
    plt.xlabel('Number of Fatalities Per Month')
    plt.ylabel('Months Recorded')
    plt.title('Number of Fatalities Case by Month')
    plt.tight_layout()
    plt.show()
    return d
############################ MAIN FOR VISUAL #########################
def vis_main():
    cur, conn = setUpDatabase('joint_data_bases.db')
    get_all_covid_data('daily_covid_data.csv', cur, conn)
    daily_covid_vis('daily_covid_data.csv', cur, conn)
    change_case_calc('change_in_cases.csv', cur, conn)
    get_covid_data_visual('change_in_cases.csv', cur, conn)
    get_covid_data_fatalities_visual(cur, conn)

vis_main()