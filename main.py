import GoogleAPI as ga
import DropDownPieCharts as ddpc
import requests
import json


def process_text(text):
    headers = {'Content-Type': 'text/plain;charset=utf-8'}
    params = {
        "task": "nakdan",
        "genre": "modern",
        "data": text,
        "addmorph": True,
        "matchpartial": True,
        "keepmetagim": False,
        "keepqq": False,
    }
    r = requests.post("https://nakdan-4-0.loadbalancer.dicta.org.il/addnikud", headers=headers, json=params)
    r.encoding = "UTF-8"
    x = json.loads(r.text)
    ds = []
    for item in x:
        y = {}
        if (('word' in item) and item['sep'] == False) or (
                ('word' in item) and item['word'] == '!' and item['sep'] == True):
            y['word'] = item['word']
            if item['word'] == '!':
                y['morph'] = '0x{0:0{1}X}'.format(int(0), 16)
        for inner in item['options']:
            y['morph'] = '0x{0:0{1}X}'.format(int(inner['morph']), 16)
        if len(y) > 0:
            ds.append(y)

    return ds


# check if male that it's not Preposition, like:
# check how to recognize word: מכם/מכן
# def suffix_gender(item):
#     if item['morph'][7] == '9' or item['morph'][7:9] == '10':
#         item['gender'] = 'female'
#     elif item['morph'][7] == '8' or item['morph'][8] == '8':
#         item['gender'] = 'male'
#     else:
#         item['gender'] = 'none'


def gender(item):
    if item['morph'][12] == '4' or item['morph'][12] == '5':
        return 'female'
    elif item['morph'][12] == '2' or item['morph'][12] == '3':
        return 'male'
    elif item['morph'][12] == '6':
        return 'both'


def rec_gender(ds):
    x = 'יקרה'
    for item in ds:
        # check for pos VERB
        if item['morph'][13] == 'D' and item['word'] != x:
            if gender(item) == 'female':
                return 'female'
            elif gender(item) == 'male':
                return 'male'
            elif gender(item) == 'both':
                return 'both'

    for i in range(len(ds) - 1):
        # check if in i is noun and i+1 is adjective
        if ((ds[i])['morph'])[13] == '6' and (((ds[i + 1])['morph'])[13] == '1') or ((ds[i + 1])['word'] == x):
            if gender(ds[i + 1]) == 'female' or ((ds[i + 1])['word'] == x):
                return 'female'
            if gender(ds[i + 1]) == 'male':
                return 'male'
    return 'none'


# יחיד רבים
# def suffix_number(item):
#     if item['morph'][7] == '4':
#         item['number'] = 'singular'
#     elif item['morph'][7] == '8' or item['morph'][7] == '9':
#         item['number'] = 'plural'
#     else:
#         item['number'] = 'none'


def number(item):
    if item['morph'][11] == '1':
        return 'singular'
    elif '2' <= item['morph'][11] < '5' or item['morph'][11] == 'A':
        return 'plural'
    else:
        return 'none'


def rec_number(ds):
    for item in ds:
        # check for pos VERB
        if item['morph'][13] == 'D':
            if number(item) == 'plural':
                return 'plural'
            if number(item) == 'singular':
                return 'singular'
    for item in ds:
        # check for pos ADJECTIIVE
        if item['morph'][13] == '1':
            if number(item) == 'plural':
                return 'plural'
            if number(item) == 'singular':
                return 'singular'
    return 'none'


# חיוב ושלילה
def rec_pos_neg(ds):
    for item in ds:
        x = 'אין'
        y = 'אסור'
        z = 'ללא'
        # if item['morph'][13] == '5':
        #     item['pos'] = 'negative'
        if (item['morph'][12:14] == '13') or (x in item['word']):
            item['pos'] = 'negative'
        elif item['morph'][12:14] == '14' or (y in item['word']):
            item['pos'] = 'negative'
        elif item['morph'][14] == '8' or (z in item['word']):
            item['pos'] = 'negative'
        else:
            item['pos'] = 'positive'

    for item in ds:
        if item['pos'] == 'negative':
            return 'negative'
    return 'positive'


# ציווי ובקשה
def rec_imperative(ds):
    for item in ds:
        if item['morph'][9] == 'A':
            item['imperative'] = 'imperative'
        # elif '!' in item['word']:
        #     item['imperative'] = 'imperative'
        else:
            item['imperative'] = 'none'
    for item in ds:
        if item['imperative'] == 'imperative':
            return 'imperative'
    return 'not imperative'


def test_output(text):
    # for testing:
    pt = process_text(text)
    print("Text: ", text, "\n",
          "Gender: ", rec_gender(pt),
          ", Number: ", rec_number(pt),
          ", Imperative: ", rec_imperative(pt),
          ", Negative: ", rec_pos_neg(pt))


if __name__ == '__main__':
    # print(process_text('חובה לעטות מסכה king'))
    # test_output('KING שים מסכה מהר KING')

    sheet_tab_name = 'Sheet2'
    sheet_tab_id = 1759206245

    # Clear all filters
    ga.clear_filter(sheet_tab_id)

    # Reset to 0 if the file is empty or it's the first run over the spreadsheet
    f = open("SpreadsheetSize.txt", "r")
    if f == '' or ga.read_from_spreadsheet(sheet_tab_name, 'B2', 'E2') == []:
        f = open("SpreadsheetSize.txt", "w")
        f.write(str(0))
        f.close()
        f = open("SpreadsheetSize.txt", "r")

    # Check if there is a need to run code
    old_num_of_signs = int(f.read())
    current_num_of_signs = int(ddpc.num_of_signs)

    if old_num_of_signs < current_num_of_signs:

        start_cell = str(old_num_of_signs + 2)

        # Read 'description' cells from spreadsheet
        description_cells = ga.read_from_spreadsheet(sheet_tab_name, 'A' + start_cell, 'A')

        default_list = []

        for cell in description_cells:
            for text in cell:
                # Process text with Dicta API
                processed_text = process_text(text)
                # in case the whole text is in foreign language or empty
                if not processed_text:
                    arr = ['NULL', 'NULL', 'NULL', 'NULL']
                else:
                    # Making a row with the information
                    arr = [rec_gender(processed_text), rec_number(processed_text),
                           rec_imperative(processed_text), rec_pos_neg(processed_text)]
                default_list.append(arr)

        # Write into the spreadsheet
        ga.write_to_spreadsheet(default_list, sheet_tab_name, 'B' + start_cell)

        # Update current spreadsheet size
        f = open("SpreadsheetSize.txt", "w")
        f.write(str(current_num_of_signs))
        f.close()

    # Run the Dashboard with the Pie Charts
    ddpc.app.run_server(debug=True)

    # Clear all filters before exiting
    ga.clear_filter(sheet_tab_id)
