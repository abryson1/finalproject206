import sqlite3
import os
import requests
import matplotlib.pyplot as plt
import numpy as np


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn 


def joint_visual(cur, conn):
    cur.execute(
    """ SELECT UnemploymentRates.year, CovidM2.month, CovidM2.new_cases, UnemploymentRates.rate
    FROM CovidM2 JOIN UnemploymentRates JOIN Months
    ON CovidM2.month = UnemploymentRates.month_id = Months.id AND UnemploymentRates.year = CovidM2.year

    """)
    results = cur.fetchall()
    # print(results)
    # print(len(results))
    conn.commit()
    lst = []
    for i in results:
        month = str(i[1]) + " " + str(i[0])
        unemploy = i[-1]
        new_cases = i[-2]
        lst.append([month,unemploy, new_cases])

    # print(lst)
    x_values = []
    y_employ = []
    y_cases = []

    for i in lst:
        print(i)
        x_values.append(i[0])
        y_employ.append(i[1])
        y_cases.append(i[2])

    # print(x_values)
    # print(y_employ)
    # print(y_cases)
    # plt.plot(x_values, y_employ, label = 'unemployment rate per month')
    # plt.xticks(rotation = -90) 
    # plt.plot(x_values, y_cases)
    

    fig, ax1 = plt.subplots() 
    fig = plt.figure(figsize=( 12, 8 ))
    plt.title("Unemployment Rate vs Covid Data from 03/2020 to 03/2021")
    ax1.set_xlabel('months')
    ax1.set_ylabel('unemployment rate', color = 'green')
    ax1.plot(x_values, y_employ, color = 'green')
    ax1.tick_params(axis='y')


    ax2 = ax1.twinx() 
    ax2.set_ylabel('number of new cases per month', color = 'blue') 
    ax2.plot(x_values, y_cases, color = 'blue')
    ax2.tick_params(axis='y')

    plt.xticks(rotation = -90) 
    fig.tight_layout()

    plt.show()



def vis_main():
    cur, conn = setUpDatabase('joint_data_bases.db')
    joint_visual(cur, conn)
    
vis_main()