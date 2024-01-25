import re


def is_word(word : str) :
    '''
    a word is a collection of characters without whitespace that contains
    - letters : A-Za-z or
    - numbers : 0-9 or
    - literals : %&$€@

    and maybe additional characters
    '''
    return bool( re.search('[A-Za-z0-9%&$€@]', word) )


def contains_special_chars(word : str, additional='') :
    '''
    a special character is everything except
    - letters : A-Za-z
    - numbers : 0-9
    - literals : %&$€@\"*
    - punctuation : '.,:;!?-
    '''
    return bool( re.search('[^A-Za-z0-9%&$€@\"*\'.,:;!?-' + additional + ']', word) )


def replace_anomalies(word : str) :
    '''
    anomalies :
    - …
    '''
    return word.replace('…', '...')


def simplify(word, additional='') :
    'removes every character except [A-Za-z\'] and additional. also lowers word'
    return re.sub('[^A-Za-z\'' + additional + ']', '', word).lower()


def overlap(gap : tuple[float, float], word : dict):
    return max(0, min(gap[1], word['end']) - max(gap[0], word['start']))

# currently not used, maybe deprecated
# # from cleanup
# def remove_non_words(transcript, chars_regex="[^A-Za-z0-9\s]") :
#     pattern = "(?<!\S)" + chars_regex + "+(?!\S)"
#     transcript = ' '.join(re.sub(pattern, '', transcript).split())
#     return transcript
