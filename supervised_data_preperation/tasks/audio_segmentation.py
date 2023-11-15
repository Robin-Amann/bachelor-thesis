import utils.file as utils
import utils.constants as constants
from progress.bar import ChargingBar


JOIN_GAP = 0.5  # in sec

# transcript list of at least {start, end} in seconds (float)
def segment(transcript_p) :
    transcript = transcript_p.copy()
    segments = []
    end = 1
    while end <= len(transcript) :
        start = end - 1
        while end < len(transcript) and transcript[end]['start'] - transcript[end - 1]['end'] < JOIN_GAP :
            end += 1
        segments.append(transcript[start : end])
        end += 1
    
    timestamps = [{'start' : segment[0]['start'], 'end' : segment[-1]['end']} for segment in segments]

    for segment in segments :
        start = segment[0]['start']
        for word in segment:
            word['start'] -= start
            word['end'] -= start
    return segments, timestamps


def segment_dir(transcript_dir, segmented_transcript_dir) :
    manual_transcript_files = [ (f.stem, f) for f in utils.get_directory_files(transcript_dir, 'txt') if not f.stem[2:6] in constants.ignore_files]

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
        