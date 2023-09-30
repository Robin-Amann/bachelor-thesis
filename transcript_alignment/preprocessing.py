import re

def process(transcript, start, end, patterns, trim_chars, clean_chars, remove_space_before, remove_space_after) :

# trim
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

    # remove characters
    chars = set(trimmed)
    wanted = set(trim_chars + clean_chars)
    unwanted = chars - wanted
    for c in unwanted :
        trimmed = re.sub(c, '', trimmed)

# spaces
    # remove multiple spaces
    trimmed = ' '.join(trimmed.split())

    # remove space before special character
    for sub in remove_space_after :
        trimmed = trimmed.replace(sub + " ", sub)
    
    # remove space after special character
    for sub in remove_space_before :
        trimmed = trimmed.replace(" " + sub, sub)

# clean
    # lower
    clean = trimmed.lower()
       
    # remove unwanted characters
    unwanted = set(trim_chars)
    for c in unwanted :
        clean = re.sub(c, '', clean)

    return trimmed, clean


# preprocess transcripts and stone them in the lists
def read_file(path) :

    transcript = ""
    with open(path, "r", encoding="utf8") as file :
        transcript = file.read()
    
    return transcript