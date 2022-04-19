from calendar import month
import requests
import re 
import json
import matplotlib.pyplot as plt



#### EPL CODE USE THIS 

apikey = "309b5f90-ba8a-11ec-a85d-61050b9d6978"

import requests

def get_data(state_code): 

    state_code = state_code.lower()

    url = 'https://api.covidtracking.com/v2/states/'+ state_code+ '/daily.json'
    response = requests.get(url)
    data = response.text
    contents_d = json.loads(data)
    #print(contents_d.keys())
    data = contents_d['data']
    #print(contents_d['meta'])
    # print(contents_d['data'])
    # for i in data:
    #     #print('new')
    #     #print(i)
    
    return data

def get_days(state_code):
    list_of_days = []
    DICTIONARY = {}
    info = get_data(state_code)
    #print(info)
    for i in info:
        #print(i.keys())
        list = []
        #print(i['date'])
        # can get data from 3/7/2021 - 3/01/2020
        key = i['date']
        value = i['cases']['confirmed']['value']
        DICTIONARY[key] = value
    return DICTIONARY

def get_cleaned_data(state_code): 
    days_cases = get_days(state_code) 
    days = days_cases.keys()
    #print(days)
    has_data = {}
    no_record = []
    regex = r'\d{4}'
    for day in days:
        year = re.findall(regex,day)
        #print(days_cases[day])
        tup = (year, days_cases[day])
        if days_cases[day] == None:
            no_record.append(day)
        else:
            if year in has_data.keys():
                has_data[year].append(tup)
            else:
                #print('not yet')
                has_data[year] = []
                has_data[year].append(tup)
    
    print(has_data.keys())
    return has_data

def num_to_month(date):
    date = str(date)
    if date == '01':
        date = 'January'
    elif date == '02':
        date = 'February'
    elif date == '03':
        date = 'March'
    elif date == '04':
        date = 'April'
    elif date == '05':
        date = 'May'
    elif date == '06':
        date = 'June'
    elif date == '07':
        date = 'July'
    elif date == '08':
        date = 'August'
    elif date == '09':
        date = 'September'
    elif date == '10':
        date = 'October'
    elif date == '11':
        date = 'November'
    elif date == '12':
        date = 'Decemeber'
    return date
 
def monthly_average(state_code):
    yearly_info = get_cleaned_data(state_code)
    average = {}
    for i in yearly_info.keys():
        data = yearly_info[i]
        year_data_by_month = {}

        for entry in data:
            date = entry[0]
            data = entry[1]
            num = str(date[5:7])
            month = num_to_month(num)
            #print(month)
            if month not in average.keys():
                year_data_by_month[month] = []
                year_data_by_month[month].append(data)
            else:
                year_data_by_month[month].append(data)
        average[i] = year_data_by_month
    #print(average)
    return average

def barchart_restaurant_categories(state_code):
    avg = monthly_average(state_code)
    #print(avg)
    dict_num_m = {}
    for x in avg.keys():
        #print(x)
        for m in avg[x]:
            num = int(avg[x][m][0])
            month_yr = m +' '+ x
            # print(month_yr)
            # print(num)
            dict_num_m[month_yr] = num
    #print(dict_num_m)
    plt.barh(list(dict_num_m.keys()), list(dict_num_m.values()))
    plt.xlabel('Number of Confirmed Caes')
    plt.ylabel('Months Recorded')
    plt.title('Number of Confirmed Case by Month')
    plt.tight_layout()
    plt.show()
    return dict_num_m

#print(get_data('CT'))
#print(get_data('NY'))
# print(get_days('CT'))
# print(get_data('NY'))
#print(get_cleaned_data('CT'))
# print(get_cleaned_data('CA'))
# print(monthly_average('CT'))
# print(barchart_restaurant_categories('CT'))
# print(barchart_restaurant_categories('NY'))
print(barchart_restaurant_categories('CA'))

# print(get_data('NY'))
