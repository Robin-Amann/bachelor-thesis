import utils.file as utils
import utils.constants as c
import utils.wer_alignment as alignment
import utils.transcript as word_utils
import utils.console as console
import utils.alignment_metric as metric

import torchaudio
import tasks.audio_transcript_alignment.audio_transcript_alignment as ctc
from progress.bar import ChargingBar

# SPEECH_FILE = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
# transcript = "|I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT|"
# ctc.align(SPEECH_FILE, None, 16000, None)

# dataset split
def gaps_containing_speech_automatic_time(manual_dir, automatic_dir) :
    files = utils.get_dir_tuples([(manual_dir, lambda f: f.stem[2:7], lambda f: 'Speech' in f.stem), (manual_dir, lambda f: f.stem[2:7], lambda f: not 'Speech' in f.stem), (automatic_dir, lambda f: f.stem[2:7])])
    gaps = [0, 0]

    for segment_f, manual_files, automatic_files in ChargingBar('gaps').iter(files) :
        print(segment_f.stem)
        if int(segment_f.stem[2:6]) < 3916 :
            continue
        segments = utils.read_dict(segment_f)
        for index, segment in enumerate(segments) :
            start, end = segment.values()
            
            manual_f = next( iter(f for f in manual_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            automatic_f = next( iter(f for f in automatic_files if (segment_f.stem[2:7] + '{:03d}'.format(index)) in f.stem), None)
            if not (manual_f and automatic_f) :
                continue

            manual = utils.read_dict(manual_f)
            automatic = utils.read_dict(automatic_f)
            
            for pre, post in zip( [{'end' : 0}] + automatic, automatic + [{'start' : end - start}]) :
                gap = (pre['end'], post['start'])
                if gap[1] - gap[0] >= c.MIN_GAP :
                    if any( word_utils.overlap(gap, w) >= (w['end'] - w['start']) / 2 for w in manual ) :
                        gaps[0] += 1
                    else :
                        gaps[1] += 1
    print(gaps)

[101207, 119137]
gaps_containing_speech_automatic_time(c.manual_seg_dir, c.automatic_align_dir / 'custom ctc' / '1')