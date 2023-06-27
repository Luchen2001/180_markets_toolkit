import requests
import os
import csv
import fitz
import re
import couchdb

company_no = 0

def update_msg(text: str):
    msg = {'msg': text}
    host_ip = 'localhost'
    requests.post(f'http://{host_ip}:8000/update_cashflow/status', json= msg)

def get_market_cap(max_limit: str):
    # The URL of the CSV file
    url = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file"

    # Directory to save the csv file
    dir_name = "csv"

    # Create the directory if it doesn't exist
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Full path for the file
    file_path = os.path.join(dir_name, "ASX_Listed_Companies.csv")

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the content of the response to a CSV file
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("CSV file downloaded successfully.")
    else:
        print("Failed to download CSV file.")

    # Open the CSV file for reading
    with open(file_path, "r") as f:
        reader = csv.reader(f)

        # Read the header
        header = next(reader)

        # Create a dictionary to store the data
        data = {}

        # Loop through each row
        # Open the CSV file for reading
        with open(file_path, "r") as f:
            reader = csv.reader(f)

            # Read the header
            header = next(reader)

            # Create a dictionary to store the data
            data = {}

            # Loop through each row
            for row in reader:
                # Get the code, name, and cap
                code = row[0]
                name = row[1]
                cap_str = row[-1]

                # Convert cap to int, if not "SUSPENDED"
                cap = int(cap_str) if cap_str.isdigit() else 0

                # Only store the data if the cap is <60,000,000 and the length of code is 3
                if cap < max_limit and len(code) == 3 and cap != 0:
                    data[code] = {
                        'name': name,
                        'cap': cap,
                    }
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1]['cap'], reverse=False))
        # Print the data
        for code, info in sorted_data.items():
            print(f"Code: {code}, Name: {info['name']}, Cap: {info['cap']}")
        return sorted_data

def get_annoucement(company_list: dict):
    no_company = len(company_list)
    global company_no
    company_no = no_company
    url_head = "https://www.asx.com.au/asx/1/company/"
    url_tail = "/announcements?count=20&market_sensitive=false"
    keywords = ["4c", "5b", "cash", "cashflow"]

    count = 0
    with open('output.csv', 'w', newline='') as csvfile:
        fieldnames = ['key', 'name', 'cap', 'document_date', 'url', 'header']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        
        writer.writeheader()
        for key in company_list:
            count = count + 1
            # Generate the URL for the company
            url = url_head + key + url_tail

            # Fetch the webpage
            response = requests.get(url)

            # If the request was successful
            if response.status_code == 200:
                # Load the response as JSON
                data = response.json()

                # Loop through each item in the data
                for item in data['data']:
                    # Check if 'header' field contains any of the keywords
                    if any(keyword in item['header'].lower() for keyword in keywords):
                        # Add the new information to the company dictionary
                        company_list[key]['document_date'] = item['document_date'][0:10]
                        company_list[key]['url'] = item['url']
                        company_list[key]['header'] = item['header']

                        # Write the company's data to the CSV file
                        writer.writerow({'key': key, **company_list[key]})
                        print('progress: ', count, '/', no_company)
                        msg = f'retrieving progress: {count}/{no_company}'
                        update_msg(msg)
                        break
            else:
                print(f"Failed to fetch announcements for {key}")
                writer.writerow({'key': key, 'name': company_list[key]['name'], 'cap': company_list[key]['cap'], 'document_date': None, 'url': None, 'header': None})

def find_word_after_position(text, phrase):
    words = text.split()
    phrase_words = phrase.split()
    phrase_length = len(phrase_words)
    for index, current_word in enumerate(words[:-phrase_length + 1]):
        if words[index : index + phrase_length] == phrase_words:
            if index + phrase_length < len(words):
                return words[index + phrase_length]
            else:
                return None
    return None

def find_line_after_phrases(text, phrases):
    lines = text.split('\n')
    phrase_idx = 0  # The index of the current phrase we're looking for

    for i, line in enumerate(lines):
        # If the current line contains the current phrase
        if phrases[phrase_idx] in line:
            # Increment the phrase index
            phrase_idx += 1

            # If we have found all phrases, return the next line
            if phrase_idx == len(phrases) and i + 1 < len(lines):
                return lines[i + 1]

    # If we get here, we did not find all the phrases in sequence
    return None

def process_announcements(filename: str):
    global company_no
    count = 0
    search_phrase = "(should equal item 4.6 above)"
    phrases_sequence = ["related items in the accounts", "Current quarter"]
    data = []

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            count = count +1
            print(count)
            msg = f'reading progress: {count}/{company_no}'
            update_msg(msg)
            url = row['url']

            # Fetch the PDF document from the URL
            response = requests.get(url)
            response.raise_for_status()  # Will raise an exception if the request failed

            # Open the PDF file with PyMuPDF
            pdf_data = response.content
            pdf_stream = fitz.open("pdf", pdf_data)

            # Extract the text from the PDF
            text = ""
            for page in pdf_stream:
                text += page.get_text()

            # Find the word after the search phrase
            next_word = find_word_after_position(text, search_phrase)
            if next_word:
                print(f"For {row['key']}, the word after '{search_phrase}' in '{row['header']}' is '{next_word}'.")
                row['next_word'] = next_word
            else:
                print(
                    f"For {row['key']}, the phrase '{search_phrase}' was not found in '{row['header']}' or it's the last word.")
                row['next_word'] = None

            # Find the line after 'phrases_sequence'
            line_after_phrases = find_line_after_phrases(text, phrases_sequence)
            if line_after_phrases:
                print(f"For {row['key']}, the line after '{phrases_sequence}' in '{row['header']}' is '{line_after_phrases}'.")
                row['line_after_phrases'] = line_after_phrases
            else:
                print(
                    f"For {row['key']}, the sequence '{phrases_sequence}' was not found in '{row['header']}'.")
                row['line_after_phrases'] = None
            data.append(row)

    # Write the updated data back to the CSV file
    fieldnames = list(data[0].keys())
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def process_and_verify_announcements(filename: str):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = []
        total_rows = sum(1 for row in reader)
        csvfile.seek(0)  # Reset CSV reader to the beginning of the file

        for count, row in enumerate(reader, start=1):
            print(f"Processing {count}/{total_rows}...")
            msg = f"Checking process {count}/{total_rows}..."
            update_msg(msg)
            next_word = row.get('next_word', '').strip()
            line_after_phrases = row.get('line_after_phrases', '').strip().replace("‘", "'").replace("’", "'")
            cash_flow = ''
            dollar_sign = ''

            # Check if any of the columns are empty
            if not next_word or not line_after_phrases:
                cash_flow = 'check'
            else:
                # Check if 'next_word' contains other characters than allowed
                if not re.fullmatch(r"[\d,\-\*]*", next_word):
                    cash_flow = 'check'
                elif len(next_word) == 1 and next_word.isdigit():  # Check if 'next_word' is a single digit
                    cash_flow = 'check'
                else:
                    # Delete '*' if 'next_word' have it
                    next_word = next_word.replace('*', '')


                    # Check if $ exists in 'line_after_phrases'
                    if '$' in line_after_phrases:
                        # Check if ' exists in 'line_after_phrases'
                        if "'" in line_after_phrases:
                            parts = line_after_phrases.split("'")
                            dollar_sign = parts[0]
                            cash_flow = next_word
                            if len(parts) > 1:
                                cash_flow = cash_flow + "," + parts[1]
                        else:
                            dollar_sign = line_after_phrases
                            cash_flow = next_word
                    else:
                        cash_flow = 'check'

            row['cash_flow'] = cash_flow
            row['dollar_sign'] = dollar_sign
            data.append(row)

    # Write the updated data back to the CSV file
    fieldnames = list(data[0].keys())
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def formatting_csv(filename: str):
    # Read the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # get the header
        
        rows = list(reader)
        rows = rows[1:]

    # Identify the indices of necessary columns
    cash_flow_index = header.index('cash_flow')
    
    other_columns = ['next_word', 'line_after_phrases']
    other_indices = [header.index(col) for col in other_columns]
    header = [col for col in header if col not in ['next_word', 'line_after_phrases']]
    print(header)
    cash_flow_index = header.index('cash_flow')
    print(cash_flow_index)

    # Remove unnecessary columns and convert 'cash_flow' to numeric
    new_rows = []
    for row in rows:
        new_row = [val for i, val in enumerate(row) if i not in other_indices]
        print(new_row)
        # Convert 'cash_flow' to numeric (assuming it's a string of a number)
        if new_row[cash_flow_index] != 'check':
            new_row[cash_flow_index] = float(new_row[cash_flow_index].replace(',', ''))
            new_rows.append(new_row)
        else:
            new_rows.append(new_row)

    # Write the modified and sorted rows back to the CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # write the header
        writer.writerows(new_rows)  # write the rows

def update_documents_with_cashflow():
    couch = couchdb.Server('http://admin:admin@localhost:5984/')
    db_name = 'stocks'
    if db_name in couch:
        db = couch[db_name]
    else:
        raise ValueError(f"Database '{db_name}' does not exist!")
    with open('output.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            key = row[0]
            name = row[1]
            document_date = row[3]
            url = row[4]
            header = row[5]
            cash_flow = (row[6])
            dollar_sign = row[7]

            if cash_flow.isdigit():
                try:
                    cash_flow = int(float(cash_flow))
                except ValueError:
                    print(f"'{cash_flow}' is not a valid number.")

            # Find the document in the database using the key/id
            if key in db:
                document = db[key]

                # Add the 'cashflow' attribute and update other fields
                document['cashflow'] = {
                    'name': name,
                    'document_date': document_date,
                    'url': url,
                    'header': header,
                    'cash_flow': cash_flow,
                    'dollar_sign': dollar_sign
                }

                # Save the updated document back to the database
                db.save(document)
                print(f"Document with key {key} updated with cashflow information.")
            else:
                print(f"Document with key {key} not found in the database.")

def generate_cashflow_doc(cap: int):
    update_msg('updating the market cap')
    company_list = get_market_cap(cap)

    update_msg('retrieving cashflow announcement')
    get_annoucement(company_list)

    update_msg('reading cashflow announcement')
    process_announcements("output.csv")

    update_msg('checking the reading result')
    process_and_verify_announcements("output.csv")

    update_msg('finalizng the cashflow documents')
    formatting_csv("output.csv")

    update_msg('updating database with cashflow')
    update_documents_with_cashflow()

    update_msg('cashflow template and database is ready')


