import math
import csv
import requests
import json
from typing import List

def update_msg(text: str):
    msg = {'msg': text}
    host_ip = 'localhost'
    requests.post(f'http://{host_ip}:8000/update_cashflow/status', json= msg)

def fetch_and_calculate_points_old(days: int):
    global company_no
    base_url = 'https://www.asx.com.au/asx/1/share/'
    suffix = f'/prices?interval=daily&count={days}'

    # Load the existing data
    with open("output.csv", 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
        original_fieldnames = [f for f in data[0].keys()]

    max_limit = 0
    min_value = math.inf
    average_traded_dollar_amounts = []

    # Fetch data and calculate points
    count = 0
    for row in data:
        count = count +1
        ticker = row['key']
        msg = f'calculating the score for {ticker}, process {count}/{company_no}'
        update_msg(msg)
        url = base_url + ticker + suffix
        print(url)
        try:
            r = requests.get(url, timeout=10)
            response = r.json()

            if 'data' in response.keys():
                sum_volume = sum_amount = 0

                for daily_data in response['data']:
                    sum_volume += daily_data['volume']
                    daily_avg_price = (daily_data['day_high_price'] + daily_data['day_low_price']) / 2
                    sum_amount += daily_avg_price * daily_data['volume']

                row['average volume'] = int(round(sum_volume / days))
                row['average traded dollar amount'] = avg_amount = int(round(sum_amount / days))
                average_traded_dollar_amounts.append(avg_amount)

                # Update min_value
                if avg_amount < min_value:
                    min_value = avg_amount
        except Exception as e:
            print(f"Error fetching data for ticker {ticker}: {e}")
            row['average volume'] = 0
            row['average traded dollar amount'] = 0

        row['points'] = 0  # Initialize points

    # Find the 10th highest avg_traded_dollar_amount
    average_traded_dollar_amounts.sort(reverse=True)
    if len(average_traded_dollar_amounts) >= 10:
        max_limit = average_traded_dollar_amounts[9]

    # Calculate points based on the Fibonacci sequence
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    for row in data:
        if row['average traded dollar amount'] >= max_limit:
            row['points'] = 11
        else:
            percentage = (row['average traded dollar amount'] - min_value) / (max_limit - min_value)
            for index, fib in enumerate(fibonacci):
                if percentage < fib / 89:
                    row['points'] = index + 1
                    break

    # Write the output to a new CSV file
    with open('result.csv', 'w', newline='') as outfile:
        fieldnames = original_fieldnames + ['average volume', 'average traded dollar amount', 'points']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            writer.writerow(row)
    print("Output file 'result.csv' created.")


def fetch_and_calculate_points(days: int):
    global company_no
    base_url = 'https://www.asx.com.au/asx/1/share/'
    suffix = f'/prices?interval=daily&count={days}'

    # Load the existing data
    with open("output.csv", 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
        original_fieldnames = [f for f in data[0].keys()]

    max_limit = 0
    min_value = math.inf
    EMA_traded_dollar_amounts = []

    # Fetch data and calculate points
    count = 0
    for row in data:
        count = count + 1
        ticker = row['key']
        #msg = f'calculating the score for {ticker}, process {count}/{company_no}'
        # update_msg(msg)
        url = base_url + ticker + suffix
        print(url)
        try:
            r = requests.get(url, timeout=10)
            response = r.json()

            if 'data' in response.keys():
                sum_volume = 0
                smoothing_factor = 2 / (days + 1)
                EMA_amount = 0

                for daily_data in reversed(response['data']):
                    print(daily_data)
                    sum_volume += daily_data['volume']
                    daily_avg_price = (daily_data['day_high_price'] + daily_data['day_low_price']) / 2
                    current_amount = daily_avg_price * daily_data['volume']

                    # Calculate the EMA
                    if EMA_amount == 0:  # first day
                        EMA_amount = current_amount
                    else:
                        EMA_amount = (current_amount * smoothing_factor) + (EMA_amount * (1 - smoothing_factor))

                row['average volume'] = int(round(sum_volume / days))
                row['EMA traded dollar amount'] = EMA_amount
                EMA_traded_dollar_amounts.append(EMA_amount)

                # Update min_value
                if EMA_amount < min_value:
                    min_value = EMA_amount

        except Exception as e:
            print(f"Error fetching data for ticker {ticker}: {e}")
            row['average volume'] = 0
            row['EMA traded dollar amount'] = 0

        row['points'] = 0  # Initialize points

    # Find the 10th highest EMA_traded_dollar_amount
    EMA_traded_dollar_amounts.sort(reverse=True)
    if len(EMA_traded_dollar_amounts) >= 10:
        max_limit = EMA_traded_dollar_amounts[9]

    # Calculate points based on the Fibonacci sequence
    fibonacci = [0.5, 1.5, 2.5, 3.5, 8, 13, 21, 34, 55, 89]
    #fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    for row in data:
        if row['EMA traded dollar amount'] >= max_limit:
            row['points'] = 11
        else:
            percentage = (row['EMA traded dollar amount'] - min_value) / (max_limit - min_value)
            for index, fib in enumerate(fibonacci):
                if percentage < fib / 89:
                    row['points'] = index + 1
                    break

    # Write the output to a new CSV file
    with open('result.csv', 'w', newline='') as outfile:
        fieldnames = original_fieldnames + ['average volume', 'EMA traded dollar amount', 'points']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            writer.writerow(row)
    print("Output file 'result.csv' created.")

def fetch_and_calculate_points_volume(days: int):
    global company_no
    base_url = 'https://www.asx.com.au/asx/1/share/'
    suffix = f'/prices?interval=daily&count={days}'

    # Load the existing data
    with open("output.csv", 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
        original_fieldnames = [f for f in data[0].keys()]

    max_limit = 0
    min_value = math.inf
    EMA_volumes = []

    # Fetch data and calculate points
    count = 0
    for row in data:
        count = count + 1
        ticker = row['key']
        #msg = f'calculating the score for {ticker}, process {count}/{company_no}'
        # update_msg(msg)
        url = base_url + ticker + suffix
        print(url)
        try:
            r = requests.get(url, timeout=10)
            response = r.json()

            if 'data' in response.keys():
                sum_volume = 0
                smoothing_factor = 2 / (days + 1)
                EMA_volume = 0

                for daily_data in reversed(response['data']):
                    print(daily_data)
                    sum_volume += daily_data['volume']

                    # Calculate the EMA
                    if EMA_volume == 0:  # first day
                        EMA_volume = daily_data['volume']
                    else:
                        EMA_volume = (daily_data['volume'] * smoothing_factor) + (EMA_volume * (1 - smoothing_factor))

                row['average volume'] = int(round(sum_volume / days))
                row['EMA volume'] = EMA_volume
                EMA_volumes.append(EMA_volume)

                # Update min_value
                if EMA_volume < min_value:
                    min_value = EMA_volume

        except Exception as e:
            print(f"Error fetching data for ticker {ticker}: {e}")
            row['average volume'] = 0
            row['EMA volume'] = 0

        row['points'] = 0  # Initialize points

    # Find the 10th highest EMA_volume
    EMA_volumes.sort(reverse=True)
    if len(EMA_volumes) >= 10:
        max_limit = EMA_volumes[9]

    # Calculate points based on the Fibonacci sequence
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    for row in data:
        if row['EMA volume'] >= max_limit:
            row['points'] = 11
        else:
            percentage = (row['EMA volume'] - min_value) / (max_limit - min_value)
            for index, fib in enumerate(fibonacci):
                if percentage < fib / 89:
                    row['points'] = index + 1
                    break

    # Write the output to a new CSV file
    with open('result.csv', 'w', newline='') as outfile:
        fieldnames = original_fieldnames + ['average volume', 'EMA volume', 'points']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            writer.writerow(row)
    print("Output file 'result.csv' created.")
