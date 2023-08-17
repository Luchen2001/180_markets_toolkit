import requests
import csv
import yfinance as yf
import datetime
import couchdb
from concurrent.futures import ThreadPoolExecutor
from config import host_ip

no_company = 1414

'''''
# Connect to CouchDB server
couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')  # Assuming the server is locally hosted

# Access existing database or create it
# Access existing database or create it
db_name = 'stocks'  # Replace 'db_name' with your actual database name
if db_name in couch:
    db = couch[db_name]
else:
    db = couch.create(db_name)

'''''
def update_msg(text: str):
    msg = {'msg': text}
    
    try:
        response = requests.post(f'http://{host_ip}:8000/update_database/status', json=msg)
        response.raise_for_status()  # This will raise a Python exception if the response returned a HTTP error status code
    except requests.exceptions.RequestException as e:
        print(f"Request failed with error: {e}")

def create_stock_list(max_limit: int):
    # The URL of the CSV file
    url = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response content to string
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(content.splitlines(), delimiter=',')

        # Read the header
        header = next(csv_reader)

        # Connect to server
        couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/') 

        # Access existing database or create it
        db_name = 'stocks'
        if db_name in couch:
            db = couch[db_name]
        else:
            db = couch.create(db_name)

        # Loop through each row
        for row in csv_reader:
            # Get the code, name, and cap
            code = row[0]
            name = row[1]
            cap_str = row[-1]

            # Convert cap to int, if not "SUSPENDED"
            cap = int(cap_str) if cap_str.isdigit() else 0

            # Only store the data if the cap is <60,000,000 and the length of code is 3
            if cap < max_limit and len(code) == 3 and cap != 0:
                # Create a new document for each stock
                doc = {'name': name, 'cap': cap}
                try:
                    # Check if the document already exists
                    existing_doc = db[code]
                    print(f"Document with id {code} already exists.")
                except couchdb.http.ResourceNotFound:
                    # If not, create a new document
                    db[code] = doc
                    print(f"Created new document with id {code}.")

        print("Stock information stored successfully.")
    else:
        print("Failed to download CSV file.")

def get_stock_info(ticker: str) -> dict:
    try:
        ticker = ticker+'.AX'
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except (KeyError, requests.exceptions.HTTPError):
        return "not found"

# Use the threading to concurrently updating the geneal information from Yahoo Finance
def general_info(args):
    db, doc_id = args
    try:
        # Get the stock information
        updated_info = get_stock_info(doc_id)
        # If the stock information is found, update the document
        if updated_info != "not found":
            doc = db[doc_id]
            doc['info'] = updated_info  # store the updated_info in 'info' field
            db.save(doc)
            print(f"{doc_id} updated")
            return 1
        else:
            with open("errors.txt", "a") as error_file:  # open the file in append mode
                error_file.write(f"{doc_id} not found\n")  # write the error to the file
            return 0

    except requests.exceptions.ReadTimeout:
        print(f"Request for {doc_id} timed out. Continuing to next document.")
        with open("errors.txt", "a") as error_file:
            error_file.write(f"Request for {doc_id} timed out\n")
        return 0
    except Exception as e:
        print(f"An error occurred for {doc_id}: {str(e)}")
        with open("errors.txt", "a") as error_file:
            error_file.write(f"An error occurred for {doc_id}: {str(e)}\n")
        return 0

def update_general_info():
    # Connect to server
    update_msg(f"Updating the database - Updating General Info - This may take a while... (~3 mins)")
    couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')  # Replace 'username' and 'password' with your actual credentials

    # Access existing database or create it
    db_name = 'stocks'
    if db_name in couch:
        db = couch[db_name]
    else:
        raise ValueError(f"Database '{db_name}' does not exist!")

    args = [(db, doc_id) for doc_id in db]
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(general_info, args)

    count = sum(results)
    update_msg(f"General Information Updated - Updated {count}/{no_company} of companies general information")

# Update the market info e.g. price and market cap, using ASX endpoint
def market_info(doc_id, db, days):
    base_url = 'https://www.asx.com.au/asx/1/share/'
    suffix = f'/prices?interval=daily&count={days}'
    url = base_url + doc_id + suffix
    try:
        response = requests.get(url, timeout=10).json()
        if 'data' in response.keys():
            doc = db[doc_id]
            doc['price_data'] = response['data']  # store the fetched price data in 'price_data' field

            # calculate the new 'cap' if 'sharesOutstanding' and 'close_price' are available
            if 'info' in doc and 'sharesOutstanding' in doc['info']:
                shares_outstanding = doc['info']['sharesOutstanding']
                if response['data']:
                    latest_price_data = response['data'][0]  # assume the first element is the most recent
                    if 'close_price' in latest_price_data:
                        close_price = latest_price_data['close_price']
                        doc['cap'] = shares_outstanding * close_price  # update 'cap'

            db.save(doc)
            print(f'{doc_id} updated')
            return 1, doc_id
        return 0, doc_id

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {doc_id}: {e}")
        return 0, doc_id

def update_market_info(days: int = 20):
    update_msg(f"Updating the database - Updating Market Info - This may take a while... (~2 mins)")
    # Connect to server
    couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')  # Replace 'username' and 'password' with your actual credentials

    # Access existing database or create it
    db_name = 'stocks'
    if db_name in couch:
        db = couch[db_name]
    else:
        raise ValueError(f"Database '{db_name}' does not exist!")

    no_company = len(db)

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(market_info, db, [db]*no_company, [days]*no_company)
        count = sum(1 for result in results if result[0] == 1)
        percentage = round(count / no_company * 100, 1)
        update_msg(f"Updating the database - Updated {count} / {no_company} of market info ({percentage}%)")

def update_liquidity_cos(days: int = 20):
    count = 0

    # Connect to server
    couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')  # Replace 'username' and 'password' with your actual credentials

    # Access existing database or create it
    db_name = 'stocks'
    if db_name in couch:
        db = couch[db_name]
    else:
        raise ValueError(f"Database '{db_name}' does not exist!")

    data = []
    EMA_traded_dollar_amounts = []
    fibonacci = [0.5, 1.5, 2.5, 3.5, 8, 13, 21, 34, 55, 89]
    update_msg(f"Updating the database - Calculating liquidity scores")

    for doc_id in db:
        try:
            doc = db[doc_id]
            if 'price_data' in doc.keys():
                sum_volume = 0
                smoothing_factor = 2 / (days + 1)
                EMA_amount = 0

                for daily_data in reversed(doc['price_data'][:days-1]):
                    sum_volume += daily_data['volume']
                    daily_avg_price = (daily_data['day_high_price'] + daily_data['day_low_price']) / 2
                    current_amount = daily_avg_price * daily_data['volume']

                    # Calculate the EMA
                    if EMA_amount == 0:  # first day
                        EMA_amount = current_amount
                    else:
                        EMA_amount = (current_amount * smoothing_factor) + (EMA_amount * (1 - smoothing_factor))

                today_volume = doc['live_data'].get('volume') if 'live_data' in doc else 0
                today_price = doc['live_data'].get('last_price') if 'live_data' in doc else 0
                yesterday_volume = doc['price_data'][0].get('volume') if 'price_data' in doc else 0
                today_amount = 0
                if today_volume == yesterday_volume:
                    today_volume = 0

                else:
                    today_amount = round(today_price * today_volume, 1) if (today_price is not None) and (today_volume is not None) else 0
                EMA_amount = (today_amount * smoothing_factor) + (EMA_amount * (1 - smoothing_factor))

                sum_volume = sum_volume + today_volume
                average_volume = int(round(sum_volume / days))

                # Update the document with the new fields
                doc['EMA_amount'] = int(round(EMA_amount))
                doc['average_volume'] = average_volume

                data.append((doc_id, EMA_amount))
                db.save(doc)
                EMA_traded_dollar_amounts.append(EMA_amount)
                print(f"{doc_id} EMA calculated")

        except Exception as e:
            print(f"Error calculating for {doc_id}: {e}")

    # Sort the data by EMA_amount
    data.sort(key=lambda x: x[1], reverse=True)

    # Find the 10th highest EMA_traded_dollar_amount
    EMA_traded_dollar_amounts.sort(reverse=True)
    min_value = min(EMA_traded_dollar_amounts)
    max_limit = EMA_traded_dollar_amounts[9] if len(EMA_traded_dollar_amounts) >= 10 else min_value

    # Assign scores
    for doc_id, EMA_amount in data:
        if EMA_amount >= max_limit:
            score = 11  # score is 11 for top 10 stocks
        else:
            percentage = (EMA_amount - min_value) / (max_limit - min_value)
            score = 1
            for index, fib in enumerate(fibonacci):
                if percentage < fib / 89:
                    score = index + 1
                    break

        # Add the liquidity score and update date to the document
        try:
            doc = db[doc_id]
            doc['liquidity_score'] = score
            doc['date_of_update'] = datetime.datetime.now().strftime("%Y-%m-%d")

            # Save the updated document
            db.save(doc)
            print(f"{doc_id} score updated")
            count = count + 1
            percentage = round(count / no_company * 100, 1)
            update_msg(f"Updating the database - Updating liquidity scores ({percentage}%) - {doc_id} updated")
        except couchdb.http.ResourceConflict:
            print(f"Conflict while saving changes to document {doc_id}. Please resolve manually.")
    update_msg(f"Liquidity Update Finished - {percentage}% of which updated")

def update_mining_companies():
    # Connect to server
    couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')

    # Access existing database or create it
    db_name = 'stocks'
    if db_name in couch:
        db = couch[db_name]
    else:
        raise ValueError(f"Database '{db_name}' does not exist!")

    # List of defined mining industries
    mining_industries = [
        'Coking Coal',
        'Uranium',
        'Other Industrial Metals & Mining',
        'Gold',
        'Oil & Gas E&P',
        'Other Precious Metals & Mining',
        'Thermal Coal',
        'Aluminum',
        'Coking Coal',
        'Copper',
        'Silver',
        'Steel'
    ]

    # List of commodities
    commodities = [
    'Coking Coal',
    'Uranium',
    'Gold',
    'Thermal Coal',
    'Coal',
    'Aluminum',
    'Copper',
    'Silver',
    'Steel',
    'Diamonds',
    'Graphite',
    'Tin',
    'Tantalum',
    'Potash',
    'Phosphate',
    'Oil Shale',
    'Mineral Sands',
    'Molybdenum',
    'Cobalt',
    'Lead',
    'Bauxite',
    'Tungsten',
    'Iron Ore',
    'Nickel',
    'Zinc',
    'Lithium',
    'Manganese',
    'Rare Earth',
    'Gas',
    'Oil',
    'Salt',
    'Opals',
    'Kaolin',
    'Gypsum',
    'Peat',
    'Sapphire',
    'Barite',
    'Bentonite',
    'Zircon',
    'Rutile',
    'Ilmenite',
    'Silica',
    'Canadium',
    'Titanium',
    'Iron',
    'Calcium Limestone',
    'Helium',
    'Hydrogen',
    'Vanadium'
    ]

    # Loop through all documents in the database
    for doc_id in db:
        try:
            doc = db[doc_id]

            # Check if 'info' key exists in the document and 'industry' key exists in 'info' 
            if 'info' in doc.keys() and 'industry' in doc['info'].keys():
                # Check if the company's industry matches any of the defined mining industries
                if doc['info']['industry'] in mining_industries:
                    doc['isMiningComp'] = True
                    # Get the company's long business summary
                    summary = doc['info'].get('longBusinessSummary', '').lower()

                    # Check for the presence of each commodity in the summary
                    found_commodities = [commodity for commodity in commodities if commodity.lower() in summary]
                    if found_commodities:
                        doc['commodities'] = ', '.join(found_commodities)
                else:
                    doc['isMiningComp'] = False

                # Save the updated document
                db.save(doc)
                print(f"{doc_id} isMiningComp updated")

        except Exception as e:
            print(f"Error updating for {doc_id}: {e}")

def market_live_data(doc_id, db):
    url = f"https://www.asx.com.au/asx/1/share/{doc_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            doc = db[doc_id]
            data = response.json()

            # calculate the live 'market cap'
            if 'last_price' in data and 'number_of_shares' in data:
                data['cap'] = data['last_price']*data['number_of_shares']

            if 'last_price' in data and 'previous_close_price' in data:
                data['price_change'] = round(100 * (data['last_price'] - data['previous_close_price']) / data['previous_close_price'], 2)
            else:
                data['price_change'] = 0

            doc['live_data'] = data  # store the fetched live data (volume/price/market cap/no_shares) in 'live_data' field

            db.save(doc)
            print(f'{doc_id} updated')
            return 1, doc_id
        return 0, doc_id

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {doc_id}: {e}")
        return 0, doc_id

#function to update the real-time price/volume/no_shares/cap
def update_market_live_data():
    update_msg(f"Updating the database - Updating Live Market Data - This may take one minutes")
    # Connect to server
    couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')  # Replace 'username' and 'password' with your actual credentials

    # Access existing database or create it
    db_name = 'stocks'
    if db_name in couch:
        db = couch[db_name]
    else:
        raise ValueError(f"Database '{db_name}' does not exist!")

    no_company = len(db)

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(market_live_data, db, [db]*no_company)
        count = sum(1 for result in results if result[0] == 1)
        percentage = round(count / no_company * 100, 1)
        update_msg(f"Updating the database - Updated {count} / {no_company} of live market data ({percentage}%)")
    now = datetime.datetime.now()
    update_msg(f"Live data updated at {now} ")

def update_hubspot():
    update_msg("Hubspot spreadsheet has been successfully uploaded")

    # Connect to server
    couch = couchdb.Server(f'http://admin:admin@{host_ip}:5984/')

    # Access existing database or create it
    db_name = 'stocks'
    if db_name in couch:
        db = couch[db_name]
    else:
        raise ValueError(f"Database '{db_name}' does not exist!")
    
    ticker_dict = {}

    with open("hubspot.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        ticker_index = header.index("Ticker")
        rating_index = header.index("Company Rating")
        owner_index = header.index("Company owner")

        for row in reader:
            ticker = row[ticker_index]
            if ticker != '':
                try:
                    rating = int(row[rating_index])
                except ValueError:
                    rating = row[rating_index]
                owner = row[owner_index]
                # Store information in the dictionary using Ticker as the key
                ticker_dict[ticker] = {
                    "Company Rating": rating,
                    "Company owner": owner
                }
    ticker_dict = {k: ticker_dict[k] for k in reversed(ticker_dict)}

    update_msg('Updating the Hubspot data ... this may take ~ 1 min')
    for key in ticker_dict:
        if key in db:
            document = db[key]
            document['hubspot'] = ticker_dict[key]
            db.save(document)
            print(f"Document with key {key} updated with cashflow information.")
        else:
            print(f"Document with key {key} not found in the database.")

    update_msg('[Finished] Hubspot data has been populated to database successfully')
