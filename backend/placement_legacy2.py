import requests
import csv
import datetime
import json

def update_msg(text: str):
    msg = {'msg': text}
    host_ip = 'localhost'
    requests.post(f'http://{host_ip}:8000/update_placement/status', json= msg)

def generate_files(file):
    update_msg('Starting placement file generating')
    j = open("placement.json", "w")
    json_list = []

    placement_list = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            placement_list.append(row)
    # print(placement_list)

    base_url = 'https://www.asx.com.au/asx/1/share/'
    code = ''
    suffix = '/prices?interval=daily&count=255'
    today = datetime.datetime.today()

    f = open('placement_export.csv', 'w')
    writer = csv.writer(f)

    header = ["Company name", 'Placement Date', "Code", "Placement price", "Type",
              "2 weeks before", '',
              "4 weeks before", '',
              "3 months before", '',
              "6 months before", '',
              "2 weeks after",  '',
              "4 weeks after",  '',
              "3 months after",  '',
              "6 months after", '',
              "Recovered days", "Rec.d date", "Rec.d Price"]
    writer.writerow(header)

    total = len(placement_list)
    count = 0
    for p in placement_list:
        code = p[2]
        price = p[3]
        type = p[4]
        name = p[0]

        count = count + 1
        update_msg(f'Updating on {code}, process {count}/{total}')

        completion= True

        date = datetime.datetime.strptime(p[1], '%Y-%m-%d')
        date_2w_b = date - datetime.timedelta(days=14)
        date_4w_b = date - datetime.timedelta(days=28)
        date_3m_b = date - datetime.timedelta(days=84)
        date_6m_b = date - datetime.timedelta(days=168)

        date_2w_a = date + datetime.timedelta(days=14)
        date_4w_a = date + datetime.timedelta(days=28)
        date_3m_a = date + datetime.timedelta(days=84)
        date_6m_a = date + datetime.timedelta(days=168)

        json_obj = {"code": code,"palcement_date": str(date)[:10], "placement_price": price, "type": type, "name": name}


        date_dict = {}
        date_dict['date_2w_b'] = {"date": str(date_2w_b)[:10], "price": 'NA'}
        date_dict['date_4w_b'] = {"date": str(date_4w_b)[:10], "price": 'NA'}
        date_dict['date_3m_b'] = {"date": str(date_3m_b)[:10], "price": 'NA'}
        date_dict['date_6m_b'] = {"date": str(date_6m_b)[:10], "price": 'NA'}
        date_dict['date_2w_a'] = {"date": str(date_2w_a)[:10], "price": 'NA'}
        date_dict['date_4w_a'] = {"date": str(date_4w_a)[:10], "price": 'NA'}
        date_dict['date_3m_a'] = {"date": str(date_3m_a)[:10], "price": 'NA'}
        date_dict['date_6m_a'] = {"date": str(date_6m_a)[:10], "price": 'NA'}
        print(date_dict)

        for key in date_dict:
            date_tem = date_dict[key]['date']
            date_tem = datetime.datetime.strptime(date_tem, '%Y-%m-%d')
            if date_tem > today:
                date_dict[key]['price'] = "TBD"

        url = base_url + code + suffix
        print(url)
        r = requests.get(url, timeout=10)
        price_data = r.json()

        data = {}
        if 'data' in price_data.keys():
            data = price_data['data']

        recovered_date = None
        recovered_price = None
        for d in data:
            for key in date_dict.keys():
                if d['close_date'][:10] == date_dict[key]["date"]:
                    # print(date_dict[key]['date'], key, d["close_price"])
                    date_dict[key]['price'] = d["close_price"]
                    # print(date_dict)
                date_temp = datetime.datetime.strptime(d['close_date'][:10], '%Y-%m-%d')
                # print(date_temp)
                # print(date)
                # print((date - date_temp).days)
                # print("-----")
                if (date_temp - date).days > 0 and float(d['close_price']) <= float(price):
                    recovered_date = date_temp
                    recovered_price = d['close_price']
        recovered_days = None
        if recovered_date != None:
            recovered_days = (recovered_date - date).days
        else:
            completion = completion and False
        print("recovered date: ", recovered_date)
        print("price on that day: ", recovered_price)
        print("recovered days: ", recovered_days)

        deviation = 1
        while (deviation <= 4):
            for key in date_dict.keys():
                if date_dict[key]['price'] == 'NA':
                    old_date = date_dict[key]['date']
                    old_date = datetime.datetime.strptime(old_date, '%Y-%m-%d')
                    new_date = old_date - datetime.timedelta(days=deviation)
                    date_dict[key]['date'] = str(new_date)[:10]
                    for d in data:
                        for key in date_dict.keys():
                            if d['close_date'][:10] == date_dict[key]["date"]:
                                # print(date_dict[key]['date'], key, d["close_price"])
                                date_dict[key]['price'] = d["close_price"]
            deviation = deviation + 1

        deviation = 5
        while (deviation <= 8):
            for key in date_dict.keys():
                if date_dict[key]['price'] == 'NA':
                    old_date = date_dict[key]['date']
                    old_date = datetime.datetime.strptime(old_date, '%Y-%m-%d')
                    new_date = old_date + datetime.timedelta(days=deviation)
                    date_dict[key]['date'] = str(new_date)[:10]
                    for d in data:
                        for key in date_dict.keys():
                            if d['close_date'][:10] == date_dict[key]["date"]:
                                # print(date_dict[key]['date'], key, d["close_price"])
                                date_dict[key]['price'] = d["close_price"]
            deviation = deviation + 1

        for key in date_dict.keys():
            if date_dict[key]['price'] == 'NA' or date_dict[key]['price']=="TBD":
                completion = completion and False


        if date_dict['date_2w_b']['price'] != 'NA' and date_dict['date_2w_b']['price'] != 'TBD':
            cg_2w_b = round((float(price) - date_dict['date_2w_b']['price']) / date_dict['date_2w_b']['price'] * 100, 2)
        else:
            cg_2w_b = 0

        if date_dict['date_4w_b']['price'] != 'NA' and date_dict['date_4w_b']['price'] != 'TBD':
            cg_4w_b = round((float(price) - date_dict['date_4w_b']['price']) / date_dict['date_4w_b']['price'] * 100, 2)
        else:
            cg_4w_b = 0

        if date_dict['date_3m_b']['price'] != 'NA' and date_dict['date_3m_b']['price'] != 'TBD':
            cg_3m_b = round((float(price) - date_dict['date_3m_b']['price']) / date_dict['date_3m_b']['price'] * 100, 2)
        else:
            cg_3m_b = 0

        if date_dict['date_6m_b']['price'] != 'NA' and date_dict['date_6m_b']['price'] != 'TBD':
            cg_6m_b = round((float(price) - date_dict['date_6m_b']['price']) / date_dict['date_6m_b']['price'] * 100, 2)
        else:
            cg_6m_b = 0

        if date_dict['date_2w_a']['price'] != 'NA' and date_dict['date_2w_a']['price'] != 'TBD':
            cg_2w_a = round((float(price) - date_dict['date_2w_a']['price']) / date_dict['date_2w_a']['price'] * 100, 2)
        else:
            cg_2w_a = 0

        if date_dict['date_4w_a']['price'] != 'NA' and date_dict['date_4w_a']['price'] != 'TBD':
            cg_4w_a = round((float(price) - date_dict['date_4w_a']['price']) / date_dict['date_4w_a']['price'] * 100, 2)
        else:
            cg_4w_a = 0

        if date_dict['date_3m_a']['price'] != 'NA' and date_dict['date_3m_a']['price'] != 'TBD':
            cg_3m_a = round((float(price) - date_dict['date_3m_a']['price']) / date_dict['date_3m_a']['price'] * 100, 2)
        else:
            cg_3m_a = 0

        if date_dict['date_6m_a']['price'] != 'NA' and date_dict['date_6m_a']['price'] != 'TBD':
            cg_6m_a = round((float(price) - date_dict['date_6m_a']['price']) / date_dict['date_6m_a']['price'] * 100, 2)
        else:
            cg_6m_a = 0

        row = [name, p[1], code, price, type,
               date_dict['date_2w_b']['price'], str(cg_2w_b) + "%",
               date_dict['date_4w_b']['price'], str(cg_4w_b) + "%",
               date_dict['date_3m_b']['price'], str(cg_3m_b) + "%",
               date_dict['date_6m_b']['price'], str(cg_6m_b) + "%",
               date_dict['date_2w_a']['price'], str(cg_2w_a) + "%",
               date_dict['date_4w_a']['price'], str(cg_4w_a) + "%",
               date_dict['date_3m_a']['price'], str(cg_3m_a) + "%",
               date_dict['date_6m_a']['price'],  str(cg_6m_a) + "%",
               recovered_days,
               recovered_date,
               recovered_price]

        writer.writerow(row)

        json_obj['date_2w_b'] = date_dict['date_2w_b']
        json_obj['date_4w_b'] = date_dict['date_4w_b']
        json_obj['date_3m_b'] = date_dict['date_3m_b']
        json_obj['date_6m_b'] = date_dict['date_6m_b']
        json_obj['date_2w_a'] = date_dict['date_2w_a']
        json_obj['date_4w_a'] = date_dict['date_4w_a']
        json_obj['date_3m_a'] = date_dict['date_3m_a']
        json_obj['date_6m_a'] = date_dict['date_6m_a']
        json_obj["recovered_days"] = recovered_days
        json_obj["recovered_date"] = str(recovered_date)
        json_obj["recovered_price"] = recovered_price
        json_obj["completion"] = completion
        json_list.append(json_obj)
        json_object = json.dumps(json_list, indent=4)
    j.write(json_object)
    f.close()
    update_msg('placement file is ready')