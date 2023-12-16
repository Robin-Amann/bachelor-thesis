import re


def is_word(word : str) :
    '''
    a word is a collection of characters without whitespace that contains
    - letters : A-Za-z or
    - numbers : 0-9 or
    - literals : %&$€@\"*

    and maybe additional characters
    '''
    bool( re.search('[A-Za-z0-9%&$€@\"*]', word) )


def contains_special_chars(word : str, additional='') :
    '''
    a special character is everything except
    - letters : A-Za-z
    - numbers : 0-9
    - literals : %&$€@\"*
    - punctuation : '.,:;!?-
    '''
    bool( re.search('[^A-Za-z0-9%&$€@\"*\'.,:;!?-' + additional + ']', word) )


def replace_anomalies(word : str) :
    '''
    anomalies :
    - …
    '''
    return word.replace('…', '...')

# from cleanup
def remove_non_words(transcript, chars_regex="[^A-Za-z0-9\s]") :
    pattern = "(?<!\S)" + chars_regex + "+(?!\S)"
    transcript = ' '.join(re.sub(pattern, '', transcript).split())
    return transcript


def simplify(word, additional='') :
    return re.sub('[^A-Za-z\'' + additional + ']', '', word).lower()