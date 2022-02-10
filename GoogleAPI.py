from __future__ import print_function
from googleapiclient.discovery import build

# go to the project and import service account
from google.oauth2 import service_account

# type of service we need an access to
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # read and write premission
# credentials to access this service
SERVICE_ACCOUNT_FILE = 'keys.json'
creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# full spreadsheet URL:
# https://docs.google.com/spreadsheets/d/1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8
SAMPLE_SPREADSHEET_ID = '1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8'


def clear_filter(sheet_id):
    batch_update_spreadsheet_request_body = {
        'requests': [
            {
                'clearBasicFilter': {
                    'sheetId': sheet_id
                }
            }
        ],
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()


def filter_spreadsheet(sheet_id, column_number, sort_by_str):
    # clear filter before adding one
    clear_filter(sheet_id)

    batch_update_spreadsheet_request_body = {
        # A list of updates to apply to the spreadsheet.
        # Requests will be applied in the order they are specified.
        'requests': [
            {
                'setBasicFilter': {
                    'filter': {
                        'range': {
                            'sheetId': sheet_id,  # sheet id, come after "gid=" in the URL
                            'startRowIndex': 0,
                            'startColumnIndex': 0
                        },
                        'sortSpecs': [
                            {
                                'dimensionIndex': column_number,  # number of column we filter
                                'sortOrder': 'ASCENDING'
                            }
                        ],
                        'filterSpecs': [
                            {
                                'filterCriteria': {
                                    'hiddenValues': [

                                    ]
                                },
                                'columnIndex': column_number  # number of column we filter
                            },
                            {
                                'filterCriteria': {
                                    'condition': {
                                        'type': 'TEXT_EQ',
                                        'values': [
                                            {
                                                'userEnteredValue': sort_by_str
                                            }
                                        ]
                                    },
                                },
                                'columnIndex': column_number  # number of column we filter by condition
                            }
                        ]
                    }
                }
            }
        ],
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()


def read_from_spreadsheet(tab_name, start_cell, end_cell):
    SAMPLE_RANGE_NAME = str(tab_name + '!' + start_cell + ':' + end_cell)  # the column with the description
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()

    values = result.get('values', [])
    return values


def write_to_spreadsheet(input_list_of_lists, tab_name, start_cell):
    range = str(tab_name + '!' + start_cell)
    # Call the Sheets API
    sheet = service.spreadsheets()
    body_input = {"values": input_list_of_lists}
    insert_request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                           range=range, valueInputOption="USER_ENTERED",
                                           body=body_input).execute()
