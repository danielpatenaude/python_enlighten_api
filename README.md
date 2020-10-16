# python_enlighten_api
Enphase Enlighten API application to pull data and monitor panel performance and send alerts on anomalies

## Requirements
Requires Python 3.6.8 or later installed. Much effort has been taken to ensure this application does not require additional modules besides what is included standard with Python.

## Getting Started

1. Allow app access to your Enlighten Account:
    * Follow the instructions here to add a new application to your developer account: https://developer.enphase.com/docs/quickstart.html
2. Open run_inverter_daily_stats.py and set the following in the User Settings section:
    * user_id: within MyEnlighten go to your account Settings and find the API Settings user ID
    * site_id: within MyEnlighten the Site ID should be displayed (or if using the web browser should be in the URL [https://enlighten.enphaseenergy.com/pv/systems/:SITE_ID/overview]
3. Set the following in the Enlighten Settings section:
    * api_key: within the https://developer.enphase.com/admin/applications page copy your app's API Key

## Enphase Enlighten API Documentation

* https://developer.enphase.com/docs

## Scripts

This repository contains a few scripts used to hit the Enphase Enlighten API and collect data. The scripts inclide:

### run_inverter_daily_stats.py

Runs the Enlighten API route 'inverters_summary_by_envoy_or_site' to collect the lifetime energy produced by each inverter. If you call this route once a day before your solar is producing power (e.g.: 4am) you get the total lifetime power produced by each inverter, including the previous day. If you track this total lifetime energy value every day, you can then subtract the current day's total from the previous day lifetime total. That gives you the daily production value for that inverter. Note: if your Envoy is connected via low bandwidth Cellular, data only refreshes to Enlighten every 6 hours. So perform this route the next day in the early morning to ensure you get complete data.

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


## Setting Automated Cron Jobs
If you're using Linux, you can add these scripts to crontab jobs to run automatically at night by:

Run:

    >crontab -e
Add a crontab job:

    # At 4am local time run the python script via shell script to ensure we're in the right directory
    0 4 * * * /home/<user>/python_enlighten_api/run_inverter_daily_stats.sh >> /home/<user>/python_enlighten_api/cron.log 2>&1
