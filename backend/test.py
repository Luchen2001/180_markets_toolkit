import requests

symbol = "RR1.AX"  # Replace "XYZ" with the actual ASX stock symbol

# Make a request to Alpha Vantage's API for intraday data
response = requests.get(
    "https://www.alphavantage.co/query",
    params={
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",  # Adjust the interval as per your requirement
        "apikey": "FIYXAYKFFUJSBP0V"  # Replace with your Alpha Vantage API key
    }
)

if response.status_code == 200:
    data = response.json()
    print(data)
    if "Time Series (1min)" in data:
        time_series = data["Time Series (1min)"]
        for timestamp, price_data in time_series.items():
            bid_price = price_data["3. bid price"]
            bid_volume = price_data["4. bid size"]
            ask_price = price_data["5. ask price"]
            ask_volume = price_data["6. ask size"]
            print(f"Timestamp: {timestamp}")
            print(f"Bid Price: {bid_price}, Bid Volume: {bid_volume}")
            print(f"Ask Price: {ask_price}, Ask Volume: {ask_volume}")
            print()
    else:
        print("No intraday data available for the symbol.")
else:
    print("Error fetching intraday data.")
