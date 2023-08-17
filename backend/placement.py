import requests
import csv
from datetime import datetime, timedelta
from config import host_ip
import math
#from scipy.stats import norm
import numpy as np
import json

def update_msg(text: str):
    msg = {'msg': text}
    host_ip = 'localhost'
    requests.post(f'http://{host_ip}:8000/update_placement/status', json= msg)

# S: current market price of the asset
# X: strike price of the option
# r: the risk-free interest rate
# v: volatility of the underlying asset's returns
# t: time left until the option expires
# def black_scholes_call(S, X, t, r=0.04, v=0.5)
def black_scholes_call(S, X, t, r=0.04, v=0.5):
    d1 = (np.log(S / X) + (r + 0.5 * v ** 2) * t) / (v * np.sqrt(t))
    d2 = d1 - v * np.sqrt(t)

    call_price = S * 0.5 * (1 + math.erf(d1 / np.sqrt(2))) - X * np.exp(-r * t) * 0.5 * (1 + math.erf(d2 / np.sqrt(2)))
    return call_price

def calculate_returns_old(code, cap_raise_price, due_date, ratio, strike_price, expiry, BASE_DAYS):
    return_list = {}
    for day in BASE_DAYS:
        return_list[day] = 'N/A'

    base_url = 'https://www.asx.com.au/asx/1/share/'
    suffix = f'/prices?interval=daily&count=255'
    url = base_url + code + suffix
    try:
        response = requests.get(url, timeout=10).json()
        if 'data' in response.keys():
            data = response['data']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {code}: {e}")
        return
    option_value = black_scholes_call(S,strike_price, t)



def calculate_returns(code, cap_raise_price, due_date, ratio, strike_price, expiry, BASE_DAYS, hasOption):
    cap_raise_price = float(cap_raise_price)
    return_list = {}
    base_url = 'https://www.asx.com.au/asx/1/share/'
    suffix = f'/prices?interval=daily&count=255'
    url = base_url + code + suffix
    try:
        response = requests.get(url, timeout=10).json()
        if 'data' in response.keys():
            data = response['data']
            due_date = datetime.strptime(due_date, '%d/%m/%Y %H:%M')
            # Function to find record with offset
            def find_record_with_offset(target_date):
                for offset in [0, 1, 2, 3, -1, -2, -3]:
                    search_date = target_date + timedelta(days=offset)
                    search_date_str = search_date.strftime('%Y-%m-%d')
                    for record in data:
                        if record['close_date'][0:10] == search_date_str:
                            return record
                return None
            # Find expiry record
            due_date_record = find_record_with_offset(due_date)
            if due_date_record:
                return_list[0] = due_date_record

            # Search for additional dates in BASE_DAYS
            for base_day in BASE_DAYS:
                target_date = due_date + timedelta(days=base_day)
                base_day_record = find_record_with_offset(target_date)
                if base_day_record:
                    return_list[base_day] = base_day_record
            #print(f'-------- {code} --------')
            for key, record in return_list.items():
                #print(f'---- for {key} days ----')
                entry_price = cap_raise_price
                normal_return = (record['close_price']-entry_price)/entry_price
                if hasOption:
                    option_expiry_date = due_date + timedelta(days=float(expiry) * 365)
                    ratio = float(ratio)
                    S = record['close_price']
                    X = float(strike_price)
                    close_date_obj = datetime.strptime(record['close_date'][0:10], '%Y-%m-%d')
                    t = (option_expiry_date - close_date_obj).days / 365.0
                    #print(f'time to maturity : {t*365}')
                    option_price = black_scholes_call(S, X, t)
                    #print(f"Option price for index {key}: {option_price}")
                    effective_entry_price = cap_raise_price-(option_price*ratio)
                    print(f"effective entry price is: {effective_entry_price}")
                    print(f"close price is: {record['close_price']}")
                    effective_return = (record['close_price']-effective_entry_price)/effective_entry_price
                    print(f"for {code}, the effective return are: {effective_return}")
                    return_list[key] = {
                        'close_date': record['close_date'],
                        'close_price': record['close_price'],
                        'option_value': option_price,
                        'effective_entry_price': effective_entry_price,
                        'effective_return': effective_return,
                        'normal_return': normal_return
                    }
                else:
                    return_list[key] = {
                        'close_date': record['close_date'],
                        'close_price': record['close_price'],
                        'normal_return': normal_return
                    }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {code}: {e}")
        return

    return return_list


'''''
# Example usage
cap_raise_price = "0.068"
due_date = "17/01/2023 15:00"
ratio = "0.5"
strike_price = "0.1"
code = "OPN"
expiry = '2'
BASE_DAYS = [30, 60, 90, 120]
result = calculate_returns(code, cap_raise_price, due_date, ratio, strike_price, expiry, BASE_DAYS)
print(result)
'''''

def generate_placement_spreadsheet(BASE_DAYS:list):
    update_msg('start to generate file...')

    with open("deals.csv", "r") as f:
        lead_broker_set = set()
        reader = csv.reader(f)
        # Read the header
        header = next(reader)
        for row in reader:
            lead_broker_string = row[9]
            lead_brokers = lead_broker_string.split(' + ')
            for broker in lead_brokers:
                lead_broker_set.add(broker)
        lead_broker_set.discard('')  # Remove the empty string
        lead_broker_dict = {broker.strip(): None for broker in sorted(lead_broker_set)}  # Sort and remove leading/trailing spaces

        # If you want to assign a specific value to each key, you can replace None with that value.
        json_string = json.dumps(lead_broker_dict, indent=4)
        print(json_string)

    '''''
    data = {}
    with open("deals.csv", "r") as f:
        reader = csv.reader(f)
        # Read the header
        header = next(reader)

        # Loop through each row
        for row in reader:
            hasOption = False
            # Get the code, name, and cap
            name = row[0]
            code = row[1]
            cap_raise_price = row[2]
            raise_amt = row[3]
            due_date = row[4]
            ratio = row[6]
            strike = row[7]
            expiry = row[8]
            lead_broker = row[9]
            print(name)
            print(code)
            print(cap_raise_price)
            print(raise_amt)
            print(due_date)
            print(ratio)
            print(strike)
            print(expiry)
            print(lead_broker)
            if ratio == '':
                hasOption = False
            else:
                hasOption = True

            if expiry == '':
                hasOption = False

            return_list = calculate_returns(code, cap_raise_price, due_date, ratio, strike, expiry, BASE_DAYS, hasOption)

            print(return_list)
            data[code] = {
                'name': name,
                'code': code,
                'lead_broker': lead_broker,
                'cap_raise_price': cap_raise_price,
                'raise_amt': raise_amt,
                'due_date': due_date,
            }
            for index, item in return_list.items():
                if hasOption:
                    data[code][index] = {'effective_return': round(item['effective_return']*100,2), 'normal_return': round(item['normal_return']*100,2) }
                else:
                    data[code][index] = {'effective_return':'', 'normal_return': round(item['normal_return']*100,2) }
            print(data[code])
            print('---------------')

    with open('deals_result.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        BASE_DAYS = [0] + BASE_DAYS
        # Write the header
        header = ['name', 'code', 'lead_broker', 'cap_raise_price', 'raise_amt', 'due_date']
        for day in BASE_DAYS:
            header.extend([f'{day} days effective_return', f'{day} days normal_return'])
        writer.writerow(header)

        # Assuming you have collected the data in a dictionary called data
        for stock, details in data.items():
            row = [details['name'], details['code'], details['lead_broker'], details['cap_raise_price'], details['raise_amt'], details['due_date']]
            for day in BASE_DAYS:
                if day in details:
                    row.extend([details[day]['effective_return'], details[day]['normal_return']])
                else:
                    row.extend(['N/A', 'N/A']) # If data for the day is not available
            writer.writerow(row)
    '''''

    print('CSV file has been written successfully.')
    update_msg('file has been created successfully.')
