# Author:   Daniel Patenaude
# Date:     10/13/2020
# Desc:     API utilities for calling the Enphase Enlighten API

import datetime
import json
import requests
from datetime import date

class enlightenAPI:

    def __init__(self, config):
        '''
        Initialize the englightAPI class
            Parameters:
                The API configuration (as a dictionary). Must contain api_url, site_id, api_key, and user_id
        '''
        self.config = config

    def __log_time(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S') + ": "

    def __get_authenticated_url(self, route:str):
        '''
        Private class function to get the API url that includes all the authentication params from the local config
            Parameters:
                route (string): the intended route to run (e.g.: summary, stats, inventory, etc)
            Returns:
                The enlighten API expected API url including user/app authentication info
        '''

        # This url more or less looks like this: https://api.enphaseenergy.com/api/v2/systems/:SITE_ID/summary?key=:API_KEY&user_id=:USER_ID"
        return f'{self.config["api_url"]}/{self.config["site_id"]}/{route}?key={self.config["api_key"]}&user_id={self.config["user_id"]}'

    def energy_lifetime(self, start_date:str = None, end_date:str = None):
        '''
        Run the enlighten API energy_lifetime route (https://developer.enphase.com/docs#energy_lifetime). This route
        gets the energy produced for each day (?) over the life of the system.
            Parameters:
                start_date (string):    start date to get a specific energy summary, formatted as 2010-09-17.
                                        If no date is provided, get the summary for all time.
                end_date (string):      end date to get a specific energy summary, formatted as 2010-09-17.
                                        If no date is provided, get the summary for all time.
            Returns:
                The enlighten summary for the system
        '''
        date_range = ""
        if start_date is not None or end_date is not None:
            date_range = f'&start_date={start_date}&end_date={end_date}'

        url = f'{self.__get_authenticated_url("energy_lifetime")}{date_range}'
        result = requests.get(url)
        return json.loads(result.text)

    def inventory(self):
        '''
        Run the enlighten API inventory route (https://developer.enphase.com/docs#inventory). This route
        gets all envoys and inverters in the system.
            Returns:
                The enlighten system inventory summary of all assets
        '''
        url = f'{self.__get_authenticated_url("inventory")}'
        result = requests.get(url)
        return json.loads(result.text)

    def inverter_summary(self):
        '''
        Run the enlighten API inverters_summary_by_envoy_or_site route (https://developer.enphase.com/docs#inverters_summary_by_envoy_or_site).
        This route returns the detailed information for each inverter (including lifetime power produced). Note: if your Envoy is connected via low
        bandwidth Cellular, data only refreshes to Enlighten every 6 hours. So perform this route the next day in the early morning to ensure you get
        complete data.
            Returns:
                The enlighten summary for the system
        '''
        print(self.__log_time() + "Pulling EnlightenAPI inverter summary...")
        url = f'{self.config["api_url"]}/inverters_summary_by_envoy_or_site?key={self.config["api_key"]}&user_id={self.config["user_id"]}&site_id={self.config["site_id"]}'
        result = requests.get(url)
        return json.loads(result.text)

    def summary(self, summary_date:str = None):
        '''
        Run the enlighten API summary route (https://developer.enphase.com/docs#summary)
            Parameters:
                summary_date (string):  date to get a specific summary, formatted as 2010-09-17.
                                        If no date is provided, get the summary for the current day.
            Returns:
                The enlighten summary for the system
        '''
        if summary_date is None:
            summary_date = date.today().strftime("%Y-%m-%d")
        url = f'{self.__get_authenticated_url("summary")}&summary_date={summary_date}'
        result = requests.get(url)
        return json.loads(result.text)

    def stats(self):
        '''
        Run the enlighten API stats route (https://developer.enphase.com/docs#stats)
            Returns:
                The enlighten summary for the system
        '''
        url = f'{self.__get_authenticated_url("stats")}'
        result = requests.get(url)
        return json.loads(result.text)
