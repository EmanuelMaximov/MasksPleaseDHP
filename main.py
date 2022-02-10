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
    # print(x)
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


if __name__ == '__main__':
    # description_cells = ga.read_from_spreadsheet()
    # default_list = [['Gender', 'Number', 'Tense', 'Position']]
    # for cell in description_cells:
    #     for text in cell:
    #         processed_text = process_text(text)
    #         arr = [rec_gender(processed_text), rec_number(processed_text),
    #                rec_imperative(processed_text), rec_pos_neg(processed_text)]
    #         default_list.append(arr)
    #         # print("Text: ", text, "\n",
    #         #       "Gender: ", rec_gender(processed_text),
    #         #       ", Number: ", rec_number(processed_text),
    #         #       ", Imperative: ", rec_imperative(processed_text),
    #         #       ", Negative: ", rec_pos_neg(processed_text))
    # ga.write_to_spreadsheet(default_list)
    ddpc.app.run_server(debug=True)

    # # for cheking:
    # text = 'הכניסה ללא מסיכה אסורה! שמרו על מרחק של שני מטר'
    # processed_text = process_text(text)
    # print("Text: ", text, "\n",
    #       "Gender: ", rec_gender(processed_text),
    #       ", Number: ", rec_number(processed_text),
    #       ", Imperative: ", rec_imperative(processed_text),
    #       ", Negative: ", rec_pos_neg(processed_text))

# לעשות קובץ שאליו ייכתב מאיזו שורה לקרוא פעם הבאה כדי לא להריץ הכול מחדש
# תיקון שגיאות בנוגע לזיהוי ולסיווג
# להבין מה הפלט עבור שלט עם תיאור ריק ועם תאור בשפה זרה בלבד
