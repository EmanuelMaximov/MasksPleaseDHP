from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# go to the project and import service account
from google.oauth2 import service_account

# type of service we need an access to
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # read and write premission
# credentials to acces this service
SERVICE_ACCOUNT_FILE = 'keys.json'
creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID spreadsheet.
# full spreadsheet URL:
# https://docs.google.com/spreadsheets/d/1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8/edit#gid=263391688
SAMPLE_SPREADSHEET_ID = '1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8'
SAMPLE_RANGE_NAME = "Sheet2!B2:B"  # the column with the description


def main():
    ######## Read ########
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    print(values)

    ######## Write ########
    input = [[True,False,True], [True]] #list of lists
    body_input = {"values": input}
    insert_request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                           range="Sheet2!C5", valueInputOption="USER_ENTERED",
                                           body=body_input).execute()


if __name__ == '__main__':
    main()
