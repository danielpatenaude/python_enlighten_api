# Author:   Daniel Patenaude
# Date:     10/13/2020
# Desc:     Use the Enphase Enlighten API application to pull inverter/panel daily energy production data

import datetime
import json
import requests
import os
from utils.enlightenAPI import enlightenAPI

#-------------------------------------------
# User Settings
#-------------------------------------------
user_id = '<user_id>'
site_id = '<site_id>'

#-------------------------------------------
# Enlighten Settings
#-------------------------------------------
api_url = 'https://api.enphaseenergy.com/api/v2/systems'
api_key = '<api_key>'

config = \
{
    "user_id": user_id,
    "site_id": site_id,
    "api_url": api_url,
    "api_key": api_key
}

api = enlightenAPI(config)

# Get the inverter data from the enlighten API
inverter_summary = api.inverter_summary()[0]

# Read in the existing data or create the folder/file if needed.
# This should be formatted as:
'''
{
    "micro_inverters" : {
        "<ID>": { 
            "<DATE>": {
                "daily_energy" <Wh>, 
                "lifetime_energy": <Wh> 
        }
    }
}
'''
inverter_historical_data = {}
if os.path.isfile("data/inverter_daily_data.json") and os.access("data/inverter_daily_data.json", os.R_OK):
    with open("data/inverter_daily_data.json") as json_file:
        inverter_historical_data = json.load(json_file)
else:
    os.makedirs('data', exist_ok=True)
    inverter_historical_data["micro_inverters"] = {}

# Load the inverter data to the dictionary. 
yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
for inverter in inverter_summary["micro_inverters"]:
    inverter_sn = str(inverter["serial_number"])
    if inverter_sn not in inverter_historical_data["micro_inverters"]:
        inverter_historical_data["micro_inverters"][inverter_sn] = {}
    inverter_historical_data["micro_inverters"][inverter_sn][yesterday] = { "daily_energy": 0, "lifetime_energy": inverter["energy"]["value"]}

# Populate the daily_energy for each inverter for today's date based on the previous day's lifetime_energy and now's lifetime_energy
two_days_ago = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime('%Y-%m-%d')
total_daily_wh = 0
for inverter_sn, inverter_data in inverter_historical_data["micro_inverters"].items():
    if two_days_ago in inverter_data:
        two_days_ago_lifetime_energy = inverter_data[two_days_ago]["lifetime_energy"]
        yesterday_lifetime_energy = inverter_data[yesterday]["lifetime_energy"]
        yesterday_energy = yesterday_lifetime_energy - two_days_ago_lifetime_energy
        inverter_historical_data["micro_inverters"][inverter_sn][yesterday]["daily_energy"] = yesterday_energy
        total_daily_wh = total_daily_wh + yesterday_energy

# Write new data to file
with open('data/inverter_daily_data.json', 'w') as outfile:
    json.dump(inverter_historical_data, outfile)

print(f'Yesterdays\'s Total Energy: {total_daily_wh}Wh')
print('Complete...')