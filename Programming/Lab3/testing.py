# If you downloaded words from the course website,
# change me to the path to the downloaded file.
import io
from collections import OrderedDict
_DICTIONARY_FILE = 'words'

import re
def extract_word(raw_text):
    raw_text = raw_text.replace("à", '1')
    raw_text = raw_text.replace("á", '1')
    raw_text = raw_text.replace("â", '1')
    raw_text = raw_text.replace("ã", '1')
    raw_text = raw_text.replace("ä", '1')
    raw_text = raw_text.replace("å", '1')

    raw_text = raw_text.replace("è", '1')
    raw_text = raw_text.replace("é", '1')
    raw_text = raw_text.replace("ê", '1')
    raw_text = raw_text.replace("ë", '1')

    raw_text = raw_text.replace("ì", '1')
    raw_text = raw_text.replace("í", '1')
    raw_text = raw_text.replace("î", '1')
    raw_text = raw_text.replace("ï", '1')

    raw_text = raw_text.replace("ò", '1')
    raw_text = raw_text.replace("ó", '1')
    raw_text = raw_text.replace("ô", '1')
    raw_text = raw_text.replace("õ", '1')
    raw_text = raw_text.replace("ö", '1')

    raw_text = raw_text.replace("ù", '1')
    raw_text = raw_text.replace("ú", '1')
    raw_text = raw_text.replace("û", '1')
    raw_text = raw_text.replace("ü", '1')

    raw_text = raw_text.replace("ý", '1')
    raw_text = raw_text.replace("ÿ", '1')

    raw_text = raw_text.replace("ß", '1')
    raw_text = raw_text.replace("ñ", '1')
    return raw_text

def load_english():
    # open_file = open(_DICTIONARY_FILE, 'r')
    words_list=[]
    open_file = io.open(_DICTIONARY_FILE, mode="r", encoding="utf-8")
    contents = open_file.readlines()
    test_str = "'"
    test_str_1 = '1'
    for i in range(len(contents)):

        check_1 = contents[i].find(test_str)
        check_2 = contents[i].isascii()
        contents[i] = extract_word(contents[i])
        check_3 = contents[i].find(test_str_1)
        if (check_1 < 0) & (check_2 >= 0) & (check_3 < 0):
            words_list.append(contents[i].lower().strip('\n'))

         # words_list.lower()
    words_list = list(dict.fromkeys(words_list))
    return words_list

    open_file.close()


english = load_english()

with open(r'sales.txt', 'w') as fp:
    for item in english:
        # write each item on a new line
        fp.write("%s\n" % item)
    print('Done')
print(len(english))
# print(english)


# import math
# def is_triangle_number(num):
#     """Returns whether a number is a triangle number. """
#     discrim = 8 * num + 1
#     base = int(math.sqrt(discrim))
#     return base * base == discrim
#
# def is_triangle_word(word):
#     """Return whether a word is a triangle word."""
#     count = 0
#     count_old=[]
#     i = 1;
#     for ch in word.upper().strip():
#         ord_1 = ord(ch)
#         ord_2 = ord('A')
#         cal = ord(ch) - ord('A') + 1
#         count = count + cal
#         count_old.append(count)
#     return is_triangle_number(count)
#
#
# #%%
# all_triangle_words: list = [w for w in english if is_triangle_word(w)]
# print(len(all_triangle_words))