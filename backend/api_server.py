from typing import Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from cashflow import generate_cashflow_doc
from placement import generate_files
from database import update_general_info, update_market_info, update_liquidity_cos, create_stock_list, update_mining_companies
import datetime
import couchdb
from statistics import mean

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

cashflow_msg = {'msg': 'backend is running'}
placement_msg = {'msg': 'backend is running'}
database_msg = {'msg': 'backend is running'}
cap_temp = 0
day_temp = 0


couch = couchdb.Server('http://admin:admin@localhost:5984/')
db_name = 'stocks'
if db_name in couch:
    db = couch[db_name]
else:
    raise ValueError(f"Database '{db_name}' does not exist!")


@app.get('/')
async def root():
    return {'name': 'api to connect to react'}

@app.post('/update_database/status')
async def update_data(update_data: dict):
    global database_msg
    database_msg = update_data

@app.get('/database/status')
async def get_cashflow_status():
    global database_msg
    print(database_msg)
    return database_msg

@app.get("/update_database/general_info")
async def update_general_information(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_general_info)

@app.get("/update_database/market_info")
async def update_market_information(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_market_info)

@app.get("/update_database/liquidity_cos")
async def update_liquidity_course_of_sales(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_liquidity_cos)

@app.get("/update_database/mining_comp")
async def update_mining_companies_list(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_mining_companies)

@app.get("/update_database/new_day_update")
async def update_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_general_info)
    background_tasks.add_task(update_market_info)
    background_tasks.add_task(update_liquidity_cos)

@app.get("/update_database/realtime_liquidity_update")
async def update_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_general_info)
    background_tasks.add_task(update_liquidity_cos)

@app.get("/reboot_database")
async def reboot_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(create_stock_list, 200000000)

@app.get("/database/stocks/")
async def read_stocks(max_cap: Optional[int] = None, min_liquidity: Optional[int] = None, max_liquidity: Optional[int] = None):
    results = []
    try:
        for doc_id in db:
            doc = db[doc_id]
            if max_cap is not None and 'cap' in doc and doc['cap'] > max_cap:
                continue
            if min_liquidity is not None and 'liquidity_score' in doc and doc['liquidity_score'] < min_liquidity:
                continue
            if max_liquidity is not None and 'liquidity_score' in doc and doc['liquidity_score'] > max_liquidity:
                continue
            
            price_data = doc.get('price_data')
            close_price = price_data[0]['close_price'] if price_data else None

            ##volume 2.0
            yesterday_volume = price_data[0]['volume'] if len(price_data) > 0 else None
            yesterday_mean_price = mean([price_data[0]['day_high_price'], price_data[0]['day_low_price']]) if len(price_data) > 0 else None
            yesterday_amount = round(yesterday_mean_price * yesterday_volume, 1) if yesterday_mean_price and yesterday_volume else None

            today_volume = doc['info'].get('volume') if 'info' in doc else None
            today_price = doc['info'].get('currentPrice') if 'info' in doc else None
            if today_volume == yesterday_volume:
                today_volume = ''
                today_amount = ''
            else:
                today_amount = round(today_price * today_volume, 1) if today_price and today_volume else None

            last_5_days_amounts = [(mean([day['day_high_price'], day['day_low_price']]) * day['volume']) for day in price_data[:5]]  # get amounts for the last 5 days
            avg_5_days_amount = round(mean(last_5_days_amounts), 1) if last_5_days_amounts else None  # calculate average amount

            last_5_days_volumes = [day['volume'] for day in price_data[:5]]  # get volumes for the last 5 days
            avg_5_days_volume = round(mean(last_5_days_volumes), 1) if last_5_days_volumes else None  # calculate average volume

            ##volume 2.0

            cashflow = doc['cashflow'].get('cash_flow') if 'cashflow' in doc else None
            debt = doc['cashflow'].get('debt') if 'cashflow' in doc else None
            if debt == '' or debt == 'check':
                debt = 0
            if isinstance(cashflow, str):
                try:
                    cashflow = float(cashflow)
                except ValueError:
                    cashflow = None
            if isinstance(debt, str):
                try:
                    debt = float(debt)
                except ValueError:
                    debt = None

            market_cap = doc.get('cap')

            debt_temp = debt if isinstance(debt, (int, float)) else 0
            ev = int(market_cap - cashflow + debt_temp) if isinstance(cashflow, (int, float)) and isinstance(market_cap, (int, float)) and market_cap else 'N/A'
            results.append({
                "stock_code": doc_id,
                "name": doc.get('name'),
                "cap": market_cap,
                "liquidity_score": doc.get('liquidity_score'),
                "EMA_amount": doc.get('EMA_amount'),
                "price": close_price,
                "cashflow": cashflow,
                "debt": debt,
                "EV": ev,
                "price_today": today_price,
                "volume_today": today_volume,
                "volume": yesterday_volume,
                "volume_5d": avg_5_days_volume,
                "amount_today": today_amount,
                "amount": yesterday_amount,
                "amount_5d": avg_5_days_amount,
                "industry": doc['info'].get('industry') if 'info' in doc else None,
                "isMining": doc.get('isMiningComp'),
                "commodities": doc.get('commodities'),
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/stocks/cashflow")
async def get_all_stock_cashflows():
    cashflows = []
    try:
        for doc_id in db:
            doc = db[doc_id]
            cashflow = doc.get('cashflow')
            if cashflow:
                cashflow["stock_code"] = doc_id
                cashflow["name"] = doc["name"]
                cashflow["cap"] = doc["cap"]
                cashflows.append(cashflow)
            else:
                cashflows.append({
                    "stock_code": doc_id,
                    "name": doc["name"],
                    "cap": doc["cap"],
                    "document_date": "",
                    "url": "",
                    "header": "",
                    "cash_flow": "check",
                    "debt":"",
                    "dollar_sign": ""
                })
        return cashflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/database/stocks/update_cashflow/{code}")
async def update_stock_cashflow(code: str, cashflow_data: dict):
    try:
        # Find the document with the provided code as the document ID
        if code in db:
            doc = db[code]
        else:
            raise HTTPException(status_code=404, detail="Document not found")

        # Add or replace the cashflow attribute with the provided data
        cashflow_keys = ["document_date", "url", "header", "cash_flow", "debt", "dollar_sign"]

        # Check if the 'cashflow' attribute exists in the document
        if 'cashflow' not in doc:
            doc['cashflow'] = {}

        # Update each attribute in cashflow data
        for key in cashflow_keys:
            if key in cashflow_data and cashflow_data[key]:  # If the key exists and its value is not empty
                doc['cashflow'][key] = cashflow_data[key]  # Update the value
            elif key not in doc['cashflow']:
                doc['cashflow'][key] = None  # Set default value as None if no old value exists

        # Update the document in the database
        db.save(doc)

        return {"message": "Cashflow data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cashflow/{cap}/")
async def generate_cashflow(background_tasks: BackgroundTasks, cap: int):
    global cap_temp
    cap_temp = cap
    background_tasks.add_task(generate_cashflow_doc, cap)

@app.get('/cashflow/status')
async def get_cashflow_status():
    global cashflow_msg
    return cashflow_msg

@app.post('/update_cashflow/status')
async def update_data(update_data: dict):
    global cashflow_msg
    cashflow_msg = update_data

@app.get("/download/cashflow")
async def download_csv():
    file = "./output.csv"
    return FileResponse(file, media_type="text/csv", filename=f"cashflow_template_cap_{cap_temp}_day_{day_temp}.csv")

# API endpoint for generating the placement performance tracking file
@app.post("/upload_hubspot")
async def update_hubspot_file(file: UploadFile = File(...)):
    with open("hubspot.csv", "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": "hubspot.csv"}


# API endpoint for generating the placement performance tracking file
@app.post("/upload_placement")
async def create_upload_file(file: UploadFile = File(...)):
    with open("placement.csv", "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": "placement.csv"}

@app.get("/placement/generate")
async def call_generate_files(background_tasks: BackgroundTasks):
    if os.path.isfile("placement.csv"):
        background_tasks.add_task(generate_files, "placement.csv")
        return {"message": "Processing in the background"}
    else:
        return {"message": "File not found"}

@app.post('/update_placement/status')
async def update_data(update_data: dict):
    global placement_msg
    placement_msg = update_data

@app.get('/placement/status')
async def get_placement_status():
    global placement_msg
    return placement_msg

@app.get("/download/placement/{file_type}")
async def download_placement_file(file_type: str):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if file_type == "csv":
        file = "./placement_export.csv"
        return FileResponse(file, media_type="text/csv", filename=f"placement_update_on_{today}.csv")
    elif file_type == "json":
        file = "./placement.json"
        return FileResponse(file, media_type="application/json", filename=f"placement_update_on_{today}.json")

@app.get("/download/example")
async def download_placement_file():
    file = "./example.csv"
    return FileResponse(file, media_type="text/csv", filename=f"placement_input_example.csv")



