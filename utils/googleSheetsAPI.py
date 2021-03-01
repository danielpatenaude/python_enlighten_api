# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class googleSheetsAPI:
    # Refer to https://developers.google.com/sheets/api/quickstart/python for Google Sheets API documentation

    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']

    def __connect(self, spreadsheet_id):
        '''
        Private function to connect to the google sheet API
            Parameters:
                spreadsheet_id (string):    google sheet ID (e.g.: pz2I46A6k7b197szhc91wKMkaXiOVpuiPk)
        '''
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        return service

    def readRange(self, spreadsheet_id, range_name):
        '''
        Initialize the googleSheetsRead class
            Parameters:
                spreadsheet_id (string):    google sheet ID (e.g.: pz2I46A6k7b197szhc91wKMkaXiOVpuiPk)
                range_name (string):        range in which to read data (e.g.: a named range or a sheet and columns/rows [Class Data!A2:E])
        '''
        service = self.__connect(spreadsheet_id)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            return values

    def appendDataToRange(self, spreadsheet_id, range_name, body):
        '''
        Initialize the googleSheetsRead class
            Parameters:
                spreadsheet_id (string):    google sheet ID
                range_name (string):        range in which to read data (e.g.: a named range or a sheet and columns/rows [Class Data!A2:E])
                data (string []):           data to append to the specified range
        '''
        service = self.__connect(spreadsheet_id)
        
        # Call the Sheets API
        result = \
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption='USER_ENTERED', body=body).execute()
        print('{0} cells appended.'.format(result \
                                               .get('updates') \
                                               .get('updatedCells')))

    def getSheetList(self, spreadsheet_id):
        '''
        Initialize the googleSheetsRead class
            Parameters:
                spreadsheet_id (string):    google sheet ID
        '''
        service = self.__connect(spreadsheet_id)
        
        result = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets(properties(sheetId,title))").execute()
        sheets = result.get('sheets', [])
        return sheets

    def getSheetId(self, spreadsheet_id, sheet_title):
        '''
        Initialize the googleSheetsRead class
            Parameters:
                spreadsheet_id (string):    google sheet ID
                sheet_title (string):       Sheet's title to get ID for
        '''
        sheets = self.getSheetList(spreadsheet_id)

        if not sheets:
            print('No data found.')
        for sheet in sheets:
            if sheet['properties']['title'] == sheet_title:
                return sheet['properties']['sheetId']
        print(f'Unable to find sheetId for sheet: {sheet_title}')

    def duplicateSheet(self, spreadsheet_id, source_sheet_id, new_sheet_title, insert_after_index):
        '''
        Initialize the googleSheetsRead class
            Parameters:
                spreadsheet_id (string):    google sheet ID
                source_sheet_id (string):   id of the sheet to duplicate
                new_sheet_title (string):   title of the new sheet        
                insert_after_index (int):   Position where the new sheet should be inserted
        '''

        service = self.__connect(spreadsheet_id)

        requests = []
        requests.append({
            'duplicateSheet': {
                "sourceSheetId": source_sheet_id,
                "insertSheetIndex": insert_after_index,
                "newSheetName": new_sheet_title
            }
        })
        body = {
            'requests': requests
        }
        # Call the Sheets API
        response = \
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body).execute()

# if __name__ == '__main__':
#     main()