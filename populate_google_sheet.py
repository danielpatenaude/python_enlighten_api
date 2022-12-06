# Author:   Daniel Patenaude
# Date:     12/02/2022
# Desc:     Populate the enphase data into the google sheet template

import datetime
import json
import os
from utils.googleSheetsAPI import googleSheetsAPI

INVERTER_STARTING_CELL = 'A3'

def run(config):
    SPREADSHEET_ID = config["spreadsheet_id"]
    print('Beginning push to Google Sheets...')
    api = googleSheetsAPI()

    # Get our inverter serial numbers from our google sheet
    inverter_sns = []
    result_values = api.readRange(SPREADSHEET_ID, 'InverterSerialNumbers')
    for row in result_values:
        for cell in row:
            #print(cell)
            inverter_sns.append(cell)

    # Grab the historical data from the data store
    inverter_historical_data = {}
    datafile = f'data/inverter_daily_data-{config["system_id"]}.json'
    if os.path.isfile(datafile) and os.access(datafile, os.R_OK):
        with open(datafile) as json_file:
            inverter_historical_data = json.load(json_file)
    else:
        print(f'Missing {datafile}')
        exit(1)

    yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
    daily_data_to_populate = yesterday.strftime('%Y-%m-%d') #"2020-10-15" 
    values = [ [yesterday.strftime("%m/%d/%Y")] ]

    # Ensure we can find the sheet 'Panel Data-<YEAR>' to insert data into. If not, duplicate one
    # from the template sheet
    year = yesterday.strftime('%Y')
    # Check if the sheet for the current year exists. If not, make it
    sheets = api.getSheetList(SPREADSHEET_ID)
    target_sheet_found = False
    for sheet in sheets:
        if sheet['properties']['title'] == f'Panel Data-{year}':
            target_sheet_found = True
            break
    if target_sheet_found is False:
        template_sheet_id = api.getSheetId(SPREADSHEET_ID, "Panel Data-TEMPLATE")
        api.duplicateSheet(SPREADSHEET_ID, template_sheet_id, f'Panel Data-{year}', 6)

    # Match up inverter serial numbers from the google sheet to 
    for serial_num in inverter_sns:
        if serial_num in inverter_historical_data["micro_inverters"]:
            inverter_data = inverter_historical_data["micro_inverters"][serial_num]
            if daily_data_to_populate in inverter_data:
                values.append([inverter_data[daily_data_to_populate]["daily_energy"]])
            else:
                print(f'Date data: {daily_data_to_populate} missing from {datafile}')
                exit(1)
        else:
            print(f'Serial Number: {serial_num} missing from google sheet')
            exit(1)

    body = {
        'majorDimension': 'COLUMNS',
        'values': values
    }
    # Add our daily data to our 'Panel Data' sheet
    api.appendDataToRange(SPREADSHEET_ID, f'Panel Data-{year}!{INVERTER_STARTING_CELL}', body)

if __name__ == '__main__':
    run(config)
