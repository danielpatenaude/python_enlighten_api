# python_enlighten_api (v4)

_Note: this repository has been updated to include using the new Enphase Enlighten v4 API (https://developer-v4.enphase.com/aboutproduct.html)._

Enphase Enlighten API & Google Sheets application to pull data and monitor panel performance and populate a Google Sheet with historical and visual data. This allows tracking individual panel performance over the lifetime of the system. Most of the functionlaity provided here is also provided by the Enphase Enlighten website and app, but this allows for granular panel tracking and performance over time.

For example: the panel underperforming (red) is partially blocked by a neighbor's tree during the morning hours. So it's reporting performance outside a few standard deviations.

<p align="center">
   <img src="solar_performance_example.png" width="500">
</p>


## Known Limitations
1. Token Expiration:
    * The Enlighten v4 API does not provide any documentation on what happens whe `refresh_token` expires (1 week validity) and how a new one is generated. The step to generate the original `access_token` and `refresh_token` in [Generate OAuth2 access_token and refresh_token](https://developer-v4.enphase.com/docs/quickstart.html#step_8) seems to only allow the route to be used a single time for an authorization code (auth_code).
    * As such, _the enlightenAPI_v4_ constructor provided in this repository will refresh the tokens using the [Generate new access_token and refresh_token using refresh_token](https://developer-v4.enphase.com/docs/quickstart.html#step_10) and update the _enlighten_v4_config.json_ to contain the new tokens. This ensures that each day when the script is run, the tokens are refreshed and kept well within the refresh_token's 1 week validity.
2. Inverter Telemetry Reporting:
    * It appears there's a new v4 route (/api/v4/systems/{System_id}/devices/micros/{serial_no}/telemetry) that can get microinverter data based on a date range. This seems the more ideal way to get daily inverter data than my current way of having to get the current lifetime data minus the stored value. Unfortunately, this route requires [paid plans and is not available using the free 'Watt' plan](https://github.com/danielpatenaude/python_enlighten_api/issues/4). For users of the free developer 'Watt' plan, you'll always receive a `401 - Not Authorized`.

## Requirements
Requires Python 3.6.8 or later installed. Much effort has been taken to ensure this application does not require additional modules besides what is included standard with Python.

    pip install -r requirements.txt

This will install the following:
1. requests
2. google-api-python-client 
3. google-auth-httplib2 
4. google-auth-oauthlib

## Getting Started

### Postman Scripts
The _Enpahse Enlighten v4.postman_collection.json_ is provided to assist setting up the `access_token` and `refresh_token`. In addition, you can use the GET routes to test your API connectivity and configuration.

### Script/API Setup
1. [Enlighten API] Allow app access to your Enlighten Account:
    * Follow the Enlighten [Quickstart instructions Steps 1-4](https://developer-v4.enphase.com/docs/quickstart.html#step_1) to add a new application to your developer account
2. [Enlighten API] Open the _enlighten_v4_config.json_ and set the following:
    * `name`: a generic name to identify this system.
    * `system_id`: (previously known as `Site ID`) Within MyEnlighten the System ID should be displayed (or if using the web browser should be in the URL [https://enlighten.enphaseenergy.com/web/:SYSTEM_ID/today/graph/hours].
    * `app_api_key`: Within the [Enlighten API App Page](https://developer-v4.enphase.com/admin/applications) page, copy your app's API key.
    * `app_client_id`: Within the [Enlighten API App Page](https://developer-v4.enphase.com/admin/applications) page, copy your app's Client ID.
    * `app_client_secret`: Within the [Enlighten API App Page](https://developer-v4.enphase.com/admin/applications) page, copy your app's Client Secret.
    * `access/refresh_token`: See step 3 below.
    * `spreadsheet_id`: The SpreadSheet ID from Google Sheets. See step 5.
3. [Enlighten API] Generate access_token and refresh_token (this condenses some of the Enlighten API [Quickstart Guide](https://developer-v4.enphase.com/docs/quickstart.html)
    * Follow the Enlighten [Quickstart instructions Steps 6-7](https://developer-v4.enphase.com/docs/quickstart.html#step_6), generate the auth_code for your application
    * Using the _Enpahse Enlighten v4.postman_collection.json_ open the _Generate OAuth2 access_token_ request:
      * Update the Postman environment variables to set the: auth_code, client_id, and client_secret
      * Run the request. The resulting access_token and refresh_token should be added to your enlighten_v4_config.json
      * _Note: it appears that you can only run this request ONCE per app authorization code (auth_code). Once you have the tokens generated for this auth_code, it appears you will be unable to run this route again. So make sure to save them. The Enlighten v4 API does not provide any details on this, but this appears to be the case._
    * You can call the Postman _Fetech Systems_ request using your new tokens to ensure proper configuration of your application and API tokens.
4. [Google Sheets] Setup a Google API key for your python script and put the following files in your main working script directory: credentials.json, token.pickle.
    * Follow the [Google Python Quickstart Guide](https://developers.google.com/sheets/api/quickstart/python)
    * Allow your API token to access your Google Sheets account: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?
5. [Google Sheets] Google Sheet Setup
    * The _'Solar Performance'_ Google sheet can be accessed from the [Solar Performance (Template)](https://docs.google.com/spreadsheets/d/1JPnT5T4xvDIKaefL8Z7AoxRNFv6HnVBF7SH-J9Yqfdk). It is a working copy of an example system setup. You will need to manually clear and remove the demo data to use.
    * How to Setup the _'Solar Perforance'_ Sheet: 
        1. You'll need to make a copy of this sheet to your personal Google Drive.
        2. Populate each of your inverter serial numbers into the _'Panel Data-Template'_ Sheet. 
          * This template sheet will automatically be created into a _'Panel Data-<YEAR>'_ sheet where the historical data for each panel per day will be stored.
        3. Copy and Paste, using values and transpose, your inverter serial numbers into the 'Last 7 Days' sheet from the _'Panel Data-Template'_ sheet.
        4. Update the _'Dashboard'_ Sheet panel layout to match your panels.
        5. Update the _'Dashboard'_ Sheet panel numbers and serial numbers to match your panel data
            * Note: Enphase Enlighten did not provide a good way to do this. So I manually had to match up each inverter serial number with the panel number in the layout by tracking panel energy produced over a few days on the _'Panel Data-<Year>'_ sheet vs the Enphase Enlighten website/app. After a few days each panel's historical data output allowed me to match up each panel on the Dashboard/Panel Data Sheet with the layout of the Enphase app.

### Running
The Enlighten API has a long lag time between when data is updated on their end. If you run these scripts once a day after the Enlighten data updates AND before your solar is producing power (e.g.: 4am) you get the total lifetime power produced by each inverter, including the previous day.

Run with run_inverter_daily_stats.sh or copy the logic this script is using.

#### Linux: Setting Automated Cron Jobs
If you're using Linux, you can add these scripts to crontab jobs to run automatically at night by:

Run:

    >crontab -e
Add a crontab job:

    # At 4am local time run the python script via shell script to ensure we're in the right directory
    0 4 * * * /home/<user>/python_enlighten_api/run_inverter_daily_stats.sh >> /home/<user>/python_enlighten_api/cron.log 2>&1

#### Windows: Scheduled Task
If you're using Windows, you can automate running this by doing similar to what the Linux job is doing:
1. Add a new Windows scheduled task to run at 4am
2. Create and have the scheduled task run a .bat file that performs the directory change and python call from `run_inverter_daily_stats.sh`

## Enphase Enlighten API Documentation

* https://developer-v4.enphase.com/docs.html

## Scripts Explanation

This repository contains a few scripts used to hit the Enphase Enlighten API and collect data. The scripts inclide:

### run_inverter_daily_stats.py

Runs the Enlighten API route 'inverters_summary_by_envoy_or_site' to collect the lifetime energy produced by each inverter. The Enphase API lacks the granularity of seeing per inverter daily stats. So this script provides a means to do that. If you call this route once a day before your solar is producing power (e.g.: 4am) you get the total lifetime power produced by each inverter, including the previous day. If you track this total lifetime energy value every day, you can then subtract the current day's total from the previous day lifetime total. That gives you the daily production value for that inverter. Note: if your Envoy is connected via low bandwidth Cellular, data only refreshes to Enlighten every 6 hours. So perform this route the next day in the early morning to ensure you get complete data.

The resulting data is stashed in a .json file. The file organizes the data by microinverter (by ID), then by day. So you can easily parse this historical data for daily production values.
For example:

    {
        "micro_inverters":
        {
            "12345678":
            {
                "2020-10-14":
                {
                    "daily_energy": 0,
                    "lifetime_energy": 69496
                },
                "2020-10-15":
                {
                    "daily_energy": 2,
                    "lifetime_energy": 69498
                }
            },
            "12345679":
            {
                "2020-10-14":
                {
                    "daily_energy": 0,
                    "lifetime_energy": 68967
                },
                "2020-10-15":
                {
                    "daily_energy": 7,
                    "lifetime_energy": 68974
                }
            },
        }
    }

### populat_google_sheet.py
Is run after the Englighten API data has been captured to the specified sheet by:
1. Grab all inverter serial numbers from the linked google sheet's Named Range 'InverterSerialNumbers'
2. Load in captured enlighten historical data (from run_inverter_daily_stats.py)
3. Look for the sheet titled 'Panel Data-<Current Year>' or duplicate it from 'Panel Data-Template' if it's not found
4. Match up the Enlighten serial number list order vs the InverterSerialNumber range data and filter the data by the current day
5. Insert the data into the 'Panel Data-<Current Year>' sheet
