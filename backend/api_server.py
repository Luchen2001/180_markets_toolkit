from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from cashflow import generate_cashflow_doc
from placement import generate_files
import datetime

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
cap_temp = 0
day_temp = 0

@app.get('/')
async def root():
    return {'name': 'api to connect to react'}

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



