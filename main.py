import GoogleAPI as ga
import DropDownPieCharts as ddpc
import requests
import json


# Use Dicta Nakdan API
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
        if ('word' in item) and item['sep'] is False:
            y['word'] = item['word']
        for inner in item['options']:
            y['morph'] = '0x{0:0{1}X}'.format(int(inner['morph']), 16)
        if len(y) > 0:
            ds.append(y)

    return ds


# >>>>>>>>>>>>>>>>>>>>>>>>> Text Preparation <<<<<<<<<<<<<<<<<<<<<<<<<

# Remove Verbs that have Definitearticle before them
def remove_definitearticle_verb(ds):
    ds_copy = ds
    i = 0
    ran = len(ds_copy)
    while i < ran:
        # check if in i is Definitearticle ("ה" הידיעה) and i+1 is verb
        # example: החנות מכילה
        if ((ds_copy[i])['morph'])[17] == '4' and i + 1 < ran:
            if ((ds_copy[i + 1])['morph'])[13] == 'D':
                ds_copy.pop(i + 1)
        i = i + 1
        ran = len(ds_copy)
    return ds_copy


# Remove Closing that has name that may be a verb
def remove_closing(ds):
    x = {'בתודה', 'תודה', 'ותודה', 'בברכה', 'בברכת', 'צודה'}
    ds_copy = ds
    for i in range(len(ds_copy)):
        if (ds_copy[i])['word'] in x:
            return ds_copy[0:i]
    return ds_copy


# >>>>>>>>>>>>>>>>>>>>>>>>> Gender <<<<<<<<<<<<<<<<<<<<<<<<<

def adj_gender_number(ds):
    for i in range(len(ds) - 1):
        # check if in i is noun and i+1 is adjective
        if ((ds[i])['morph'])[13] == '6' and \
                ((((ds[i + 1])['morph'])[13] == '1') or (
                        (ds[i + 1])['word'] in {'יקרה', 'יקרים', 'יקרות', 'יקר'})):
            # check there is no definitearticle
            # example: התו הירוק
            if ((ds[i])['morph'])[17] != '4' and ((ds[i + 1])['morph'])[17] != '4':
                return ds[i + 1]
    return 'none'


def gender(item):
    if item['morph'][12] == '4' or item['morph'][12] == '5':
        return 'female'
    elif item['morph'][12] == '2' or item['morph'][12] == '3':
        return 'male'
    elif item['morph'][12] == '6':
        return 'both'


def rec_gender(ds):
    for item in ds:
        # check for pos VERB
        # ensure the verb In imperative
        # or in future and person_2
        if item['morph'][13] == 'D' \
                and (item['morph'][9] == 'A' or
                     (item['morph'][9] == '8' and item['morph'][10:12] == '10')):
            if gender(item) == 'female':
                return 'female'
            elif gender(item) == 'male':
                return 'male'
            elif gender(item) == 'both':
                return 'both'

    for i in range(len(ds) - 1):
        # check if  i+1 is in person_any
        # example: אתם מתבקשים
        if ((ds[i])['word'] in {'את', 'אתה', 'הינכם', 'הינכן', 'הנכם', 'הנכן', 'אתן', 'אתם'}) and \
                (ds[i + 1])['morph'][10] == '2':
            if gender(ds[i + 1]) == 'female':
                return 'female'
            elif gender(ds[i + 1]) == 'male':
                return 'male'
            elif gender(ds[i + 1]) == 'both':
                return 'both'

    # check for specific text
    for i in range(len(ds) - 1):
        if (ds[i])['word'] in {'לקוחות', 'לציבור', 'לקהל', 'לקוח', 'לקוחה'}:
            if (ds[i + 1])['word'] in {'נכבדות', 'נכבדת', 'יקרות', 'יקרה'}:
                return 'female'
            elif (ds[i + 1])['word'] in {'יקרים', 'נכבדים', 'נכבד', 'יקר'}:
                return 'male'
            elif (ds[i + 1])['word'] in {'הלקוחות', 'לקוחותינו', 'המבקרים'}:
                return 'both'

    # # check for pos ADJECTIIVE
    # adj_item = adj_gender_number(ds)
    # if adj_item != 'none':
    #     if gender(adj_item) == 'female' or (adj_item['word'] in {'יקרות', 'יקרה'}):
    #         return 'female'
    #     if gender(adj_item) == 'male' or (adj_item['word'] in {'יקרים', 'יקר'}):
    #         return 'male'
    return 'none'


# >>>>>>>>>>>>>>>>>>>>>>>>> Number <<<<<<<<<<<<<<<<<<<<<<<<<
def number(item):
    if item['morph'][11] == '1':
        return 'singular'
    elif '2' <= item['morph'][11] < '5' or item['morph'][11] == 'A':
        return 'plural'


def rec_number(ds):
    for item in ds:
        # check for pos VERB
        # ensure the verb In imperative
        # or in future and person_2
        if item['morph'][13] == 'D' \
                and (item['morph'][9] == 'A' or
                     (item['morph'][9] == '8' and item['morph'][10:12] == '10')):
            if number(item) == 'plural':
                return 'plural'
            if number(item) == 'singular':
                return 'singular'

    for i in range(len(ds) - 1):
        # check if  i+1 is in person_any
        if ((ds[i])['word'] in {'את', 'אתה', 'הינכם', 'הינכן', 'הנכם', 'הנכן', 'אתן', 'אתם'}) and \
                (ds[i + 1])['morph'][10] == '2':
            if number(ds[i + 1]) == 'plural':
                return 'plural'
            if number(ds[i + 1]) == 'singular':
                return 'singular'
    # check for specific text
    for i in range(len(ds) - 1):
        if (ds[i])['word'] in {'לקוחות', 'לקוח', 'לקוחה', 'לקהל'}:
            if (ds[i + 1])['word'] in {'נכבד', 'נכבדת', 'יקר', 'יקרה'}:
                return 'singular'
            elif (ds[i + 1])['word'] in {'הלקוחות', 'נכבדים', 'נכבדות', 'יקרים', 'יקרות'}:
                return 'plural'

    # # check for pos ADJECTIIVE
    # adj_item = adj_gender_number(ds)
    # if adj_item != 'none':
    #     if number(adj_item) == 'singular' or (adj_item['word'] in {'יקר', 'יקרה'}):
    #         return 'singular'
    #     if number(adj_item) == 'plural' or (adj_item['word'] in {'יקרים', 'יקרות'}):
    #         return 'plural'
    return 'none'


# >>>>>>>>>>>>>>>>>>>>>>>>> Positive/Negative  <<<<<<<<<<<<<<<<<<<<<<<<<
def rec_pos_neg(ds):
    words = {'אין', 'אסור', 'ללא', 'בלי'}
    for item in ds:
        # item['morph'][12:14] == '14' or \ #Modal: חובה, צריך
        if (item['morph'][12:14] == '13') or \
                item['morph'][14] == '8' or \
                item['word'] in words:
            return 'negative'
    return 'positive'


# >>>>>>>>>>>>>>>>>>>>>>>>> Imperative  <<<<<<<<<<<<<<<<<<<<<<<<<
def rec_imperative(ds):
    for item in ds:
        # tense is imperative or tense is future and person is 2
        if item['morph'][9] == 'A' or (item['morph'][9] == '8' and item['morph'][10:12] == '10'):
            return 'imperative'
    return 'not imperative'


def run(sheet_tab_name, sheet_tab_id, read_from_cell, write_to_cell):
    # Clear all filters
    ga.clear_filter(sheet_tab_id)

    # Reset to 0 if the file is empty or it's the first run over the spreadsheet
    f = open("SpreadsheetSize.txt", "r")
    if f == '':
        # or ga.read_from_spreadsheet(sheet_tab_name, read_from_cell+'2', read_from_cell) == []:
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
        description_cells = ga.read_from_spreadsheet(sheet_tab_name, read_from_cell + start_cell, read_from_cell)

        default_list = []

        for cell in description_cells:
            for text in cell:
                print(text)
                # Process text with Dicta API
                processed_text = remove_closing(remove_definitearticle_verb(process_text(text)))
                # in case the whole text is in foreign language or empty
                if not processed_text:
                    arr = ['Empty/Foreign', 'Empty/Foreign', 'Empty/Foreign', 'Empty/Foreign']
                else:
                    # Making a row with the information
                    arr = [rec_gender(processed_text), rec_number(processed_text),
                           rec_imperative(processed_text), rec_pos_neg(processed_text)]
                default_list.append(arr)

        # Write into the spreadsheet
        ga.write_to_spreadsheet(default_list, sheet_tab_name, write_to_cell + start_cell)

        # Update current spreadsheet size
        f = open("SpreadsheetSize.txt", "w")
        f.write(str(current_num_of_signs))
        f.close()

    # Run the Dashboard with the Pie Charts
    ddpc.app.run_server(debug=True)

    # Clear all filters before exiting
    ga.clear_filter(sheet_tab_id)


def test_output(text):
    # for testing:
    pt = remove_closing(remove_definitearticle_verb(process_text(text)))
    print(pt)
    print("Text: ", text, "\n",
          "Gender: ", rec_gender(pt),
          ", Number: ", rec_number(pt),
          ", Imperative: ", rec_imperative(pt),
          ", Negative: ", rec_pos_neg(pt))


if __name__ == '__main__':
    # update these 4 parameters according to changes in the spreadsheet in the file "DropDownPieCharts.py"
    # In order to run the script from the beginning - delete the size in "SpreadsheetSize.txt"
    run(ddpc.spreadsheet_tab_name, ddpc.spreadsheet_tab_id, ddpc.spreadsheet_read_from_col,
        ddpc.spreadsheet_write_to_col)
