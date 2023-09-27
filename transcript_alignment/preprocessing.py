import re

def process(transcript, start, end, patterns, trim_chars, clean_chars, remove_space_before, remove_space_after) :
    # trim beginning and end
    
    start_index = 0
    if start != "" :
        start_index = transcript.index(start)
    end_index = len(transcript)
    if end != "" :
        end_index = transcript.index(end)
    trimmed = transcript[start_index : end_index]

    # remove patterns
    for pattern in patterns :
        trimmed = re.sub(pattern, ' ', trimmed)

    # remove unwanted characters
        # search for all unwanted characters
    unwanted_chars_str = trimmed
    chars = trim_chars + clean_chars
    for c in chars :
        unwanted_chars_str = ''.join([i for i in unwanted_chars_str if i != c])
    unwanted_chars = set(unwanted_chars_str)
        # remove unwanted chars
    for c in unwanted_chars :
        trimmed = ''.join([i for i in trimmed if i != c])
        # remove multiple spaces
    trimmed = ' '.join(trimmed.split())

    # remove space before special character
    for sub in remove_space_after :
        trimmed = trimmed.replace(sub + " ", sub)
    # remove space after special character
    for sub in remove_space_before :
        trimmed = trimmed.replace(" " + sub, sub)

    # lower
    clean = trimmed.lower()
       
    # remove unwanted characters
    unwanted_chars = set(trim_chars)
    for c in unwanted_chars :
        clean = ''.join([i for i in clean if i != c])

    return trimmed, clean


# preprocess transcripts and stone them in the lists
def read_file(path) :

    transcript = ""
    with open(path, "r", encoding="utf8") as file :
        transcript = file.read()
    
    return transcript