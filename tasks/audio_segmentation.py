import utils.file as utils
import utils.constants as constants
from progress.bar import ChargingBar


# rules:
# seg between min and max
# split seg at first max silence gap
# split seg over max in middle third


MIN_LENGTH = 10
MAX_LENGTH = 30 # at least 2 * MIN_LENGTH
PADDING = 0.5
MAX_SILENCE = 5 # at least 2 * PADDING

# transcript list of at least {start, end} in seconds (float)
def subsegment(segment, time) : # list of words; dict
    if time['end'] - time['start'] < MAX_LENGTH :
        return [segment], [time]
    
    segments_rest = [] 
    timestamps_rest = []

    start_index = segment.index( next( (x for x in segment if x['end'] - time['start'] > MIN_LENGTH), segment[-1] ))
    end_index = segment.index( next( (x for x in segment if x['end'] - time['start'] > MAX_LENGTH), segment[-1] ))

    # can't slice between same element
    # should not occour
    if start_index == end_index :
        print("segmentation error")
        print(segment)
        print(time)
        return [segment], [time]

    max_gap = (0, 0) # index, gap
    for i in range(start_index, end_index) :
        gap = segment[i + 1]['start'] - segment[i]['end']
        if gap > max_gap[1] :
            max_gap = (i+1, gap)
    
    seg = segment[ : max_gap[0]] # list of words
    rest = segment[max_gap[0] : ] # list of words
    padding_between = min(rest[0]['start'] - seg[-1]['end'], PADDING)
    time_seg = {
        'start': time['start'], 
        'end' : seg[-1]['end'] + padding_between
        }
    time_rest = {
        'start' : rest[0]['start'] - padding_between, 
        'end' : time['end']
    }
    segments_rest, timestamps_rest = subsegment(rest, time_rest)
            
    return [seg] + segments_rest, [time_seg] + timestamps_rest


def segment(transcript_p) :
    transcript = transcript_p.copy()
    segments = []
    end = 1
    while end <= len(transcript) :
        start = end - 1
        while end < len(transcript) and transcript[end]['start'] - transcript[end - 1]['end'] < MAX_SILENCE :
            end += 1
        segments.append(transcript[start : end])
        end += 1
    
    timestamps = [{'start' : segment[0]['start'] - PADDING, 'end' : segment[-1]['end'] + PADDING} for segment in segments]

    if timestamps[0]['start'] < 0 :
        timestamps[0]['start'] = 0
        
    timestamps[-1]['end'] = segments[-1][-1]['end']

    temp_segments = []
    temp_timestamps = []
    for s, t in zip(segments, timestamps) :
        x, y = subsegment(s, t)
        temp_segments += x
        temp_timestamps += y
    segments = temp_segments
    timestamps = temp_timestamps

    for s, t in zip(segments, timestamps) :
        for word in s:
            word['start'] -= t['start']
            word['end'] -= t['start']
    return segments, timestamps


def segment_dir(transcript_dir, segmented_transcript_dir) :
    manual_transcript_files = [ (f.stem, f) for f in utils.get_directory_files(transcript_dir, 'txt') if not f.stem[2:6] in constants.ignore_files]

    print(len(manual_transcript_files))
    for stem, transcript_file in ChargingBar("Segment Audio and Transcripts").iter(manual_transcript_files) :
        number = stem[2:6]
        speaker = stem[6]

        transcript = utils.read_label_timings_from_file(transcript_file)
        segments, timestamps = segment(transcript)
        for index, seg in enumerate(segments) :
            seg_file = utils.repath(transcript_file, transcript_dir, segmented_transcript_dir, [number, speaker], stem= stem + "{:03d}".format(index))
            utils.write_label_timings_to_file(seg_file, seg)
        timestamps_file = utils.repath(transcript_file, transcript_dir, segmented_transcript_dir, [number], stem= stem + "Speech")
        utils.write_timestamps_to_file(timestamps_file, timestamps)
        