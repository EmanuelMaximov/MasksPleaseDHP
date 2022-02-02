# Press the green button in the gutter to run the script.


# *** Morph Bitfield Explication ***
# The morph bitfield may be understood as follows:
#
#         # Prefix - תחילית: ל|בית ה|ספר
#         # Function
#         # bits 2-3, 5,7, 9-11
PREFIX_FUNCTION_CONJUNCTION = 0x0000000000000002
PREFIX_FUNCTION_DEFINITEARTICLE = 0x0000000000000004
PREFIX_FUNCTION_INTERROGATIVE = 0x0000000000000010
PREFIX_FUNCTION_PREPOSITION = 0x0000000000000040
PREFIX_FUNCTION_RELATIVIZER_SUBORDINATINGCONJUNCTION = 0x00000000000000100
PREFIX_FUNCTION_TEMPORALSUBCONJ = 0x00000000000000200
PREFIX_FUNCTION_ADVERB = 0x00000000000000400
PREFIX_MASK = 0x0000000000000756

# POS
# bits 17-21
POS = 0x1f0000
POS_CONTINUE = 0x0
POS_ADJECTIVE = 0x10000
POS_ADVERB = 0x20000
POS_CONJUNCTION = 0x30000
POS_AT_PREP = 0x40000
POS_NEGATION = 0x50000
POS_NOUN = 0x60000
POS_NUMERAL = 0x70000
POS_PREPOSITION = 0x80000
POS_PRONOUN = 0x90000
POS_PROPERNAME = 0xa0000
POS_CITATION = 0xb0000
POS_INITIALISM = 0xc0000
POS_VERB = 0xd0000
POS_PUNCTUATION = 0xe0000
POS_INTERROGATIVE = 0xf0000
POS_INTERJECTION = 0x100000
POS_UNKNOWN = 0x110000
POS_QUANTIFIER = 0x120000
POS_EXISTENTIAL = 0x130000
POS_MODAL = 0x140000
POS_PREFIX = 0x150000
POS_URL = 0x160000
POS_FOREIGN = 0x170000
POS_JUNK = 0x180000
POS_UNCLEAR = 0x190000
POS_PARTICIPLE = 0x1a0000
POS_COPULA = 0x1b0000
POS_REF = 0x1c0000
POS_TITULAR = 0x1d0000
POS_SHEL_PREP = 0x1e0000
POS_NONSTANDARD = 0x1f0000

# Gender
# bits 22-23
GENDER = 0x0000000000600000
GENDER_MASCULINE = 0x0000000000200000
GENDER_FEMININE = 0x0000000000400000

# Number - רבים/יחיד
# bits 25-27
NUMBER = 0x0000000007000000
NUMBER_SINGULAR = 0x0000000001000000
NUMBER_PLURAL = 0x0000000002000000
NUMBER_DUAL = 0x0000000003000000
NUMBER_DUALPLURAL = 0x0000000004000000
NUMBER_SINGULARPLURAL = 0x0000000005000000

# Person -גוף ראשון/שני...
# bits 28-30
PERSON = 0x0000000038000000
PERSON_1 = 0x0000000008000000
PERSON_2 = 0x0000000010000000
PERSON_3 = 0x0000000018000000
PERSON_ANY = 0x0000000020000000

# Tense (times,Imperative - ציווי)
# bits 34-36
TENSE = 0x0000000e00000000
TENSE_PAST = 0x0000000200000000
TENSE_ALLTIME = 0x0000000400000000
TENSE_PRESENT = 0x0000000600000000
TENSE_FUTURE = 0x0000000800000000
TENSE_IMPERATIVE = 0x0000000a00000000
TENSE_TOINFINITIVE = 0x0000000c00000000
TENSE_BAREINFINITIVE = 0x0000000e00000000

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
        if ('word' in item) and item['sep'] == False:
            y['word'] = item['word']
        for inner in item['options']:
            y['morph'] = '0x{0:0{1}X}'.format(int(inner['morph']), 16)
        if len(y) > 0:
            ds.append(y)

    return ds


# check if male that it's not Preposition, like:
# check how to recognize word: מכם/מכן
def suffix_gender(item):
    if item['morph'][7] == '9' or item['morph'][7:9] == '10':
       item['gender']='female'
    elif item['morph'][7] == '8' or item['morph'][8] == '8':
        item['gender'] = 'male'
    else:
        item['gender'] = 'none'



def gender(item):
    if item['morph'][12] == '4' or item['morph'][12] == '5':
        item['gender'] = 'female'
    elif item['morph'][12] == '2' or item['morph'][12] == '3':
        item['gender'] = 'male'
    else:
        item['gender'] = 'none'


def rec_gender(ds):
    for item in ds:
        gender(item)
        suffix_gender(item)
    return ds


def suffix_number(item):
    if item['morph'][7] == '4':
       item['number'] = 'singular'
    elif item['morph'][7] == '8' or item['morph'][7] == '9':
        item['number'] = 'plural'
    else:
        item['number'] = 'none'

def number(item):
    if item['morph'][11] == '1':
        item['number'] = 'singular'
    elif '2' <= item['morph'][11] < '5':
        item['number'] = 'plural'
    else:
        item['number'] = 'none'

def rec_number(ds):
    for item in ds:
        number(item)
        suffix_number(item)
    print(ds)


rec_number(rec_gender(process_text("בשבילכן")))


#סיווג של חלקי הדיבר


#take פעלים, כינויי גוף, MODALS, שמות תואר
# def des_gender(ds):
#     for arr in ds:
#         for item in arr:
#             if item['gender']='female':
#                 return 'female'
