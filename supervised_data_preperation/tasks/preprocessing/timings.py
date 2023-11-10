import re

def extract_timing(timing_content, timing_patterns) :
    for pattern in timing_patterns :
        timing_content = re.sub(pattern, ' ', timing_content)
    timing_content = timing_content.split('\n')
    
    timing_content = [l for l in timing_content if l and not l.isspace()]
    x = []
    for line in timing_content :
        _, s, e, w = line.split()
        if not (w.startswith('[') and w.endswith(']')) :
            x.append({'word': w, 'start': float(s), 'end': float(e)})
    return x