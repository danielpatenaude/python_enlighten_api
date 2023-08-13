# Author:   Daniel Patenaude
# Date:     10/13/2020
# Desc:     API utilities for calling the Enphase Enlighten API v4

import datetime
import json
import requests
from base64 import b64encode
from datetime import date

class enlightenAPI_v4:

    def __assert_success(self, res, exit_on_failure = True):
        '''
        Determine if the web request was successful (HTTP 200)
            Returns:
                If exit_on_failure, returned whether the web request was successful
        '''
        if res.status_code != 200:
            print("Server Responded: " + str(res.status_code) + " - " + res.text)
            if exit_on_failure:
                quit()
            else:
                return False
        return True

    def __log_time(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S') + ": "

    def fetch_systems(self):
        '''
        Run the enlighten API Fetch Systems route
            Returns:
                Returns a list of systems for which the user can make API requests. By default, systems are returned in batches of 10. The maximum size is 100.
        '''
        url = f'{self.config["api_url"]}api/v4/systems/?key={self.config["app_api_key"]}'
        response = requests.get(url, headers={'Authorization': 'Bearer ' + self.config["access_token"]})
        self.__assert_success(response)
        result = json.loads(result.text)
        return result

    def __refresh_access_token(self):
        '''
        Refresh the access_token (1 day expiration) using the refresh_token (1 week expiration) using the steps detailed 
        at: https://developer-v4.enphase.com/docs/quickstart.html#step_10.
        This will override the current self.config and save the new config to local disk to ensure we have the latest access
        and refresh tokens for the next use.
        
        Note: It's unclear from the Enlighten API docs how to refresh the refresh_token once it expires. If the refresh_token expires 
        we're unable to call this route. Generating an access/refresh token via the API (https://developer-v4.enphase.com/docs/quickstart.html#step_8) 
        seems to only be usable once per app auth_code.
            Returns:
                The full web request result of the token refresh
        '''
        print(self.__log_time() + "Refreshing access_token...")
        url = f'{self.config["api_url"]}/oauth/token?grant_type=refresh_token&refresh_token={self.config["refresh_token"]}'
        # Enlighten API v4 Quickstart says this should be a GET request, but that seems to be incorrect. POST works.
        response = requests.post(url, auth=(self.config['app_client_id'], self.config['app_client_secret']))
        refresh_successful = self.__assert_success(response, False)
        if not refresh_successful:
            print("Unable to refresh access_token. Please set a new access_token and refresh_token in the enlighten_v4_config.json. Quitting...")
            quit()

        result = json.loads(response.text)
        
        self.config['access_token'] = result['access_token']
        self.config['refresh_token'] = result['refresh_token']

        with open('enlighten_v4_config.json', 'w') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

        return result

    def inverter_summary(self):
        '''
        Run the enlighten API inverters_summary_by_envoy_or_site route (https://developer-v4.enphase.com/docs.html).
        This route returns the detailed information for each inverter (including lifetime power produced). Note: if your Envoy is connected via low
        bandwidth Cellular, data only refreshes to Enlighten every 6 hours. So perform this route the next day in the early morning to ensure you get
        complete data.
            Returns:
                Returns the microinverters summary based on the specified active envoy serial number or system.
        '''
        print(self.__log_time() + "Pulling EnlightenAPI inverter summary...")
        url = f'{self.config["api_url"]}api/v4/systems/inverters_summary_by_envoy_or_site?key={self.config["app_api_key"]}&site_id={self.config["system_id"]}'
        response = requests.get(url, headers={'Authorization': 'Bearer ' + self.config["access_token"]})
        self.__assert_success(response)
        result = json.loads(response.text)
        return result

    def production_telemetry(self):
        '''
        Run the enlighten API telemetry/production_micro route (https://developer-v4.enphase.com/docs.html).
        This route returns the telemetry for all the production micros of a system.
        It will return the default 'day' granularity i.e. start from midnight today in 5 minutes increments
        '''
        print(self.__log_time() + "Pulling EnlightenAPI inverter summary...")
        url = f'{self.config["api_url"]}api/v4/systems/{self.config["system_id"]}/telemetry/production_micro?key={self.config["app_api_key"]}'
        response = requests.get(url, headers={'Authorization': 'Bearer ' + self.config["access_token"]})
        self.__assert_success(response)
        result = json.loads(response.text)
        return result

    def __init__(self, config):
        '''
        Initialize the englightAPI class
            Parameters:
                The API configuration (as a dictionary). Must contain api_url, api_key, and secrets
        '''
        self.config = config

        # It seems the v4 API allows you to only call the OAuth POST route with grant_type=authorization_code a SINGLE time for a auth_code.
        # So we need to make sure those already exist.
        if not self.config["access_token"] or not self.config["refresh_token"]:
            print('Error: access_token or refresh_token not set in the enlighten_v4_config.json')
            quit()

        # Refresh and save out the new config with the refreshed access_token/refresh_token
        self.__refresh_access_token()