from __future__ import print_function
from googleapiclient.discovery import build

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
SAMPLE_RANGE_NAME = "Sheet2!A2:A"  # the column with the description


def read_from_spreadsheet():
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    return values


def write_to_spreadsheet(input_list_of_lists):
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    # input = [['female', 'female', 'male', 'none'], ['female', 'female', 'male', 'none']]  # list of lists
    body_input = {"values": input_list_of_lists}
    insert_request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                           range="Sheet2!B1", valueInputOption="USER_ENTERED",
                                           body=body_input).execute()
