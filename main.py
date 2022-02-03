if __name__ == '__main__':
    # Send a POST request to: https:##nakdan-4-0.loadbalancer.dicta.org.il/addnikud
    # Header: Content-Type: text/plain;charset=UTF-8
    # [Note: Encoding of your web client should be set to UTF8]

    # The POST request should be in JSON format, with the following parameters:
    # "task" = "nakdan"
    # "genre" = "modern" or "rabbinic" or "premodern" ## for handling text with interspersed Aramaic, use "rabbinic"; for Haskalah-period texts, use "premodern"
    # "data" = "טקסט טקסט טקסט"  ## here is where you put your text (maximum of 30000 characters; if your text is longer, please break it up into chunks)
    # "addmorph" = True/False ## choose whether to return morphological tagging for each word (part of speech, lexeme, gender, number, person, etc.)
    # "matchpartial" = True/False  ## choose whether the system should take advantage of partial nikud in the input text in order to constrain options
    # "keepmetagim" = True/False  ## if True, marks matres lectionis with meteg. If False, removes the matres lectionis
    # "keepqq" = True/False    ## to use the Qamatz Qatan character where relevant (otherwise regular qamatz is always used)

    # The speed of the server depends on the load at any given moment, but probably averages around a few hundreds words/sec plus transfer time for the request. Please space out requests with a 10-20 second wait between requests, so as not to overload our server (and please do not send multiple requests in parallel) . If you have a particularly large text to process, send it over to us and we will be happy to run it locally on a dedicated machine, to avoid network transfer times, and to avoid server overload.

    # *** The Return Packet ***
    # The return value is a JSON list of objects, where each object is either a word or a separator (denoted by the flag "sep"). For each word, you'll receive the predicted vocalized form and the predicted morphological tag.  We mark the separation between prefix and word (if any) with a vertical pipe.
    # If it is a separator, the value is in the "word" field. Otherwise, the relevant information will be the first entry in the "options" field: "w" is the vocalized word with prefix segmentation; "lex" is the lemma; "morph" is a bitfield indicating the morphological characteristics (see below for details).
    # Note that anything that isn't a Hebrew word is considered a separator.

    # *** Sample Python Code for calling Dicta API ***

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


def rec_gender(ds):
    x = 'יקרה'
    for item in ds:
        # check for pos VERB
        if item['morph'][13] == 'D' and item['word'] != x:
            if gender(item) == 'female':
                return 'female'
            if gender(item) == 'male':
                return 'male'

    for i in range(len(ds) - 1):
        # check if in i is noun and i+1 is adjective
        if ((ds[i])['morph'])[13] == '6' and (((ds[i + 1])['morph'])[13] == '1') or ((ds[i + 1])['word'] == x):
            if gender(ds[i]) == 'female':
                return 'female'
            if gender(ds[i]) == 'male':
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
    elif '2' <= item['morph'][11] < '5':
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
        if (item['morph'][12:14] == '13') and (x in item['word']):
            item['pos'] = 'negative'
        elif item['morph'][12:14] == '14' and (y in item['word']):
            item['pos'] = 'negative'
        elif item['morph'][14] == '8' and (z in item['word']):
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
        elif '!' in item['word']:
            item['imperative'] = 'imperative'
        else:
            item['imperative'] = 'none'
    for item in ds:
        if item['imperative'] == 'imperative':
            return 'imperative'
    return 'not imperative'
