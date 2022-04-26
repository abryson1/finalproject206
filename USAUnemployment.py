import requests
import json
import os
import matplotlib
import sqlite3
import matplotlib.pyplot as plt
import csv


def getUnemployment(): 
    """ 
    Getting data from survey results Bureau of Labor Statistics API 
    """
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": ['LNS14000000'],"startyear":"2012", "endyear":"2021"})
    p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    return json_data


def sortData(responseD):
    """
    Cleaning api response data into a list of tuples in the form [(idNum, year, month, unemployment rate), ...]
    These will eventually be the rows in database table called UnemploymentRates
    """
    month_dict = {'January':1,'February':2,'March':3 ,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    tup_l = []
    series_info = responseD['Results']['series'][0]['data']
    idNum = 1
    for d in series_info:
        year = int(d['year']) 
        month = month_dict[d['periodName']]
        rate = float(d['value'])
        tup_l.append((idNum,year,month,rate))
        idNum += 1
    return tup_l 
    
def dataCSV(tupL):
    """
    Writing the cleaned api response into a CSV file in case of api access issues
    """
    path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(path, 'usblsData.csv') 
    with open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["id","year","month", "rate"])
        for id, year, month, rate in tupL:
            new_row = [id, year, month, rate]
            writer.writerow(new_row)
        
def setUpDatabase(db_name):
    """
    Connecting with database
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def createUnemploymentTable(cur, conn):
    """
    Creating UnemploymentRates table in team database
    """
    cur.execute('CREATE TABLE IF NOT EXISTS UnemploymentRates (id INTEGER UNIQUE, year INTEGER, month_id INTEGER, rate INTEGER)')
    conn.commit()


def addRates(data, cur, conn):
    """
    Adding list of tuples into the Unemployment table
    25 rows added at a time
    """
    curId = None

    #checking the max id from the current table, setting to be 1 if no rows in table yet
    cur.execute('SELECT id FROM UnemploymentRates WHERE id = (SELECT MAX(id) from UnemploymentRates)')
    curId = cur.fetchone()
    if curId != None:
        curId = curId[0] + 1
    else:
        curId = 1
    
    #specifying id number to stop insertion
    stopNum = curId + 25
    
    #adding tuples into table if their idNum is in the appropriate range to control flow
    for (idNum, year, month, rate) in data:
        if curId <= idNum < stopNum:
            cur.execute('INSERT OR IGNORE INTO UnemploymentRates (id, year, month_id, rate) VALUES (?,?,?,?)', (idNum, year, month, rate))
            conn.commit()
            if idNum == data[-1][0]:
                print('Finsihed with data insertion into DB!')

        elif idNum == stopNum:
            print(f'Inserted data up to the row at index {stopNum - 1}!\n')
            if idNum == data[-1][0]:
                print('Finsihed with data insertion into DB!')


def createMonthTable(cur, conn): 
    """
    Creating table for the months and keys to reduce wordiness
    Adding months and keys into Month table
    """
    cur.execute('CREATE TABLE IF NOT EXISTS Months (id INTEGER PRIMARY KEY, month TEXT)')
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

##################### CALCULATION ############################
def calcDataSummary(filename, cur, conn):
    """
    Calculating the average, min and max monthly unemployment rate per year
    Takes in file name to write the calculations into
    Selects data from the UnemploymentRates table in DB joined with Months table for key pairs
    Returns dict with {year: {'avg': .., 'max': .., 'min': ..}, year: {'avg': ....}, year: {}..}
    """

    path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(path, filename) 
    
    cur.execute(
    """ SELECT UnemploymentRates.year, Months.month, UnemploymentRates.rate
    FROM UnemploymentRates JOIN Months
    ON UnemploymentRates.month_id = Months.id
    """)
    res_l = cur.fetchall()
    conn.commit()

    # iterating through the select response to make a dictionary
    # where keys = years & values = list of monthly unemployment rates
    data_d = {}
    for year, month, rate in res_l:
        data_d[year] = data_d.get(year, [])
        data_d[year].append(rate)

    # iterating through the above dictionary to calculate the stats on the list of monthly rates for each year
    # to make a dictonary where {year: {'avg': .., 'max': .., 'min': ..}, year:{}, ...}
    summary_d = {}
    with open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["year","average","max", "min"])

        for year in data_d.keys():
            year_d = {}
            year_rates_l = data_d[year]
            lavg = round((sum(year_rates_l) / len(year_rates_l)), 2)
            lmax = max(year_rates_l)
            lmin = min(year_rates_l)
            year_d['avg'] = lavg
            year_d['max'] = lmax
            year_d['min'] = lmin

            new_row = [year,lavg,lmax,lmin]
            writer.writerow(new_row)

            summary_d[year] = year_d

    return summary_d
    

 ########################### VISUAL 4 ############################
def createDataSummaryGraph(data): #call this with summary_d
    y_values = []
    
    for year in data.keys():
        avg_rate = data[year]['avg']
        y_values.append(avg_rate)

    x_values = list(data.keys())

    plt.bar(x_values, y_values, width = 0.3, color = 'green')
    plt.xticks(rotation = -90) 
    plt.grid(axis = 'y', color = 'green', linestyle = '--', linewidth = 0.3)
    plt.ylabel('Average Unemployment Rate')
    plt.xlabel('Years')
    plt.title('Average Unemployment Rate per Year')
    plt.tight_layout()
    plt.show()


def main(): 

    # --grabbing and cleaning data from api--
    response_data = getUnemployment() 
    cleaned_l = sortData(response_data)
    
    # --loading API results into CSV in case reach daily limit--
    # UNCOMMENT TO CREATE CSV ----> dataCSV(cleaned_l)
   
    # --connecting to database--
    cur, conn = setUpDatabase("joint_data_bases.db") 
    
    # --creating main table--
    createUnemploymentTable(cur, conn)

    # --creating key pair table--
    createMonthTable(cur, conn)

    # --adding data in 25 items at a time--
    addRates(cleaned_l, cur, conn)

    # --checking that join statment works--
    summary_d = calcDataSummary('usblsDataSummary.csv', cur, conn)

    # --making visualization--
    # UNCOMMENT TO CREATE ANOTHER GRAPH ----> createDataSummaryGraph(summary_d)

if __name__ == '__main__':
    main()