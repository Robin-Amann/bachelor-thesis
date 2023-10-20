

def predict(fragments) :
    hesitations = [{"start": f["start"], "end": f["end"], "label": ""} for f in fragments]
    return fragments

# labels :
# filled pauses:
  # thinking: 'um', 'er', 'ah', 'uh', ...
  # filling words: 'well', 'you know', 'okay'
  # stutter: 'I I I I..', 'W W W Well'
# empty pauses: 
  # silence
  # pause
