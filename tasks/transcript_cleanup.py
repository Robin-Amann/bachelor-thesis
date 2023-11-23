import re

def process(transcript, start = "", end = "", patterns = [], additional_trim_chars = "", additional_clean_chars = "", additional_remove_space_before = "", additional_remove_space_after = "") :

    clean_chars = set("abcdefghijklmnopqrstuvwxyz' " + additional_clean_chars)
    remove_space_before = set(".:,;!?)]>" + additional_remove_space_after)
    remove_space_after = set("([<" + additional_remove_space_before)
    trim_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ" + additional_trim_chars).union(clean_chars, remove_space_after, remove_space_before)

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
    unwanted = chars - trim_chars
    for c in unwanted :
        trimmed = trimmed.replace(c, '')
# spaces
    # remove multiple spaces
    trimmed = ' '.join(trimmed.split())

    # remove space before special character
    for sub in remove_space_after :
        trimmed = trimmed.replace(sub + ' ', sub)
    
    # remove space after special character
    for sub in remove_space_before :
        trimmed = trimmed.replace(' ' + sub, sub)
# clean
    # lower
    clean = trimmed.lower()
       
    # remove unwanted characters
    unwanted = trim_chars - clean_chars
    for c in unwanted :
        clean = clean.replace(c, '')

    if len(trimmed.split()) != len(clean.split()) :
        print("Transcript Cleanup unforseen event: trimmed word deleted")
        print("original:", transcript)
        print("trimmed: ", trimmed)
        print("clean:   ", clean)
    return trimmed, clean


def remove_non_words(transcript) :
    pattern = "(?<!\S)[^A-Za-z\s]+(?!\S)"
    transcript = ' '.join(re.sub(pattern, '', transcript).split())
    return transcript