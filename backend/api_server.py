from typing import Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from cashflow import generate_cashflow_doc
from placement import generate_files
from database import update_general_info, update_market_info, update_liquidity_cos, create_stock_list
import datetime
import couchdb

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

@app.get("/reboot_database")
async def reboot_database(background_tasks: BackgroundTasks):
    create_stock_list(200000000)


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

            results.append({
                "stock_code": doc_id,
                "name": doc.get('name'),
                "cap": doc.get('cap'),
                "liquidity_score": doc.get('liquidity_score'),
                "EMA_amount": doc.get('EMA_amount'),
                "industry": doc['info'].get('industry') if 'info' in doc else None,
                "price": close_price
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/')
async def root():
    return {'name': 'api to connect to react'}

@app.get("/database/stocks/cashflow")
async def get_all_stock_cashflows():
    cashflows = {}
    try:
        for doc_id in db:
            doc = db[doc_id]
            cashflow = doc.get('cashflow')
            if cashflow:
                cashflow["stock_code"] = doc_id
                cashflows[doc_id] = cashflow
                
        return cashflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/cashflow/{cap}/{day}")
async def generate_cashflow(background_tasks: BackgroundTasks, cap: int, day: int):
    global cap_temp
    cap_temp = cap
    global day_temp
    day_temp = day

    background_tasks.add_task(generate_cashflow_doc, cap, day)

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
    file = "./result.csv"
    return FileResponse(file, media_type="text/csv", filename=f"cashflow_template_cap_{cap_temp}_day_{day_temp}.csv")


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



