import requests
import couchdb
import csv
import datetime
import json
from config import host_ip
import math
#from scipy.stats import norm
import numpy as np

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

def update_placement(update_data: dict):
    print(update_data)

    code = update_data['code']
    date = update_data['date']
    raised_price = float(update_data['price'])
    discount = update_data['discount']
    amt = update_data['amt']
    option = update_data['option']
    option["strike"] = float(option["strike"])
    option["ttm"] = round(float(option["ttm"])*365, 0)
    option["ratio"] = float(option["ratio"])

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

    target_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    date_plus_280 = target_date + datetime.timedelta(days=280)
    if date_plus_280 < datetime.datetime.now():
        return

    date_diffs = [abs((target_date - datetime.datetime.strptime(d['close_date'][:10], "%Y-%m-%d")).days) for d in data]
    print(date_diffs)

    if 0 in date_diffs:
        match_date_index = date_diffs.index(0)
        print(f"Matched date: {data[match_date_index]}")
    else:
        closest_date = sorted(data, key=lambda d: abs((target_date - datetime.datetime.strptime(d['close_date'][:10], "%Y-%m-%d")).days))[1]
        match_date_index = data.index(closest_date)
        #print(f"Closest date: {closest_date}")

    # Regardless of whether it's a match or closest, get 180 previous records
    if match_date_index >= 130:
        records = data[match_date_index-130:match_date_index+1]
        #print(f"Previous 180 records: {records}")
    else:
        records = data[:match_date_index+2]
        #print(f"Previous {len(records)} records: {records}")

    newRecords= []
    for record in records:
        newRecord = record

        newRecord['ttm'] = option['ttm'] - 'days'
        newRecord["close_date"] = record["close_date"][0:10]
        ##TODO: check on the nullbility and catch the excepetion
        newRecord["return"] = round((record["close_price"] - raised_price)/raised_price, 4)
        option_price = black_scholes_call(record["close_price"], option["strike"], option["ttm"])
        newRecord["option_price"] = round(option_price,4)
        option_value= option_price*option["ratio"]
        newRecord["option_value"] = option_value
        newRecord["actual_return"] = round((record["close_price"] - raised_price + option_value)/raised_price, 4)
        # S: current market price of the asset
        # X: strike price of the option
        # r: the risk-free interest rate
        # v: volatility of the underlying asset's returns
        # t: time left until the option expires
        # def black_scholes_call(S, X, t, r=0.04, v=0.5)
        newRecords.append(newRecord)


    couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')  # Assuming the server is locally hosted
    # Access existing database or create it
    db_name = 'placements'  # Replace 'db_name' with your actual database name
    if db_name in couch:
        db = couch[db_name]
    else:
        db = couch.create(db_name)

    try:
        # Attempt to retrieve the document
        document = db[code]
    except couchdb.http.ResourceNotFound:
        # If not found, create a new document
        document = {'_id': code}
        document['raise'] = {}

    # Add the 'cashflow' attribute and update other fields
    document['code'] = code

    day_price = newRecords[len(newRecords)-1]['close_price']
    raising_list = document['raise']
    raising_list[date]= {
            "raised_price": raised_price,
            "discount": discount,
            "raised_amount": amt,
            "option": option,
            "record":newRecords
        }
    
   

    # Save the updated document back to the database
    db.save(document)

    try:
        # Attempt to retrieve the document
        document = db["LIST"]
    except couchdb.http.ResourceNotFound:
        # If not found, create a new document
        document = {'_id': "LIST"}
        document['List'] = {}
    
    deal_list = document["List"]
    if date not in deal_list:
        deal_list[date] = {}

    deal_list[date][code] = {
        "10_day": newRecords[-10] if len(newRecords) > 10 else None,
        "20_day": newRecords[-20] if len(newRecords) > 20 else None,
        "130_day": newRecords[-130] if len(newRecords) > 130 else None,
    }
    document['List'] = deal_list
    db.save(document)

    print(f"placement of {code} has been updated")
