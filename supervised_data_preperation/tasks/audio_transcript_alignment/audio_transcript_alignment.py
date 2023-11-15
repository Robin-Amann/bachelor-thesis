import torch
import torchaudio
import utils.file as utils
import tasks.audio_transcript_alignment.ctc as ctc
import tasks.transcript_cleanup as cleaning
from progress.bar import ChargingBar
import os
import utils.constants as constants

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_args = {'model_dir' : str(constants.model_dir / 'wav2vec2')}

def transform_result(ratio, words) :
    result = []
    decimals = 3
    for w in words :
        result.append( {
            "transcript": w.label, 
            "start": int(w.start * ratio), 
            "end": int(w.end * ratio), 
            "score": int(w.score * 10**decimals) / (10**decimals) 
            } )
    return result


def align(audio_file, transcript_file, sample_rate, wav2vec2_model, start=-1, end=-1) :
    audio = utils.read_audio(audio_file, sample_rate)  # [ [...] ]
    if start >= 0 and end > 0 and start < end :
         audio = audio[:, start : end]
    transcript = utils.read_file(transcript_file)
    trimmed, clean = cleaning.process(transcript)
    transcript = clean.upper().replace(' ', '|')
    labels, emission = ctc.get_emission(audio, device, wav2vec2_model)
    words, _, trellis_width = ctc.ctc(emission, transcript, labels)
    ratio = audio[0].size(0) / trellis_width
    words = transform_result(ratio, words)
    if words :
        for word, t in zip(words, trimmed.split()) :
            word['transcript'] = t
    return words


def align_file(audio_file, transcript_file, sample_rate, wav2vec2_model=None, start=-1, end=-1) :
    if wav2vec2_model == None :
        bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
        model = bundle.get_model(dl_kwargs=model_args).to(device)
        wav2vec2_model = (bundle, model)

    transcript = utils.read_file(transcript_file)
    if transcript and not transcript.isspace() :
        words = align(audio_file, transcript_file, sample_rate, wav2vec2_model, int(start*sample_rate), int(end*sample_rate))
        if not words :
            utils.write_file(constants.error_dir / 'audio_transcript_alignment.txt', "could not align: " + transcript_file.stem + "\n", mode='a')
        return words
    else :
        return []


def align_dir(segments_dir, audio_dir, transcript_dir, destination_dir, sample_rate) :
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
    model = bundle.get_model(dl_kwargs=model_args).to(device)
    wav2vec2_model = (bundle, model)
    print('device:', device)
    print('os:', os.name)

    files = utils.get_dir_tuples([ 
        (segments_dir, "txt", lambda s : 'Speech' in s), 
        (audio_dir, "wav", lambda s : 'A' in s or 'B' in s), 
        (transcript_dir, "txt", lambda s : True) ], 
        lambda s1, s2: s1[2:7] in s2  # number and speaker
    )
    files = [(s, f1, f2[0][1], [f for _, f in f3]) for (s, f1), f2, f3 in files if not s[2:6] in constants.ignore_files]

    s = 1
    grouped = dict()
    for f in files :
        p = int(f[1].parts[-3])
        if p in grouped :
            grouped[p].append(f)
        else :
             grouped[p] = [f]
    for p in [x for x in grouped.keys() if x >= s].sort() :
        print("Transcribe dir", p)

        for stem, segment_file, audio_file, transcript_files in ChargingBar("Align Transcript to Audio").iter(files) :
            segments = utils.read_timestamps_from_file(str(segment_file))
            
            for index, segment in enumerate(segments) :
                transcript_file = next(f for f in transcript_files if (stem[6] + "{:03d}".format(index)) in f.stem)
                destination_file = utils.repath(segment_file, segments_dir, destination_dir, [stem[6]], stem=transcript_file.stem, suffix=transcript_file.suffix)

                words = align_file(audio_file, transcript_file, sample_rate, wav2vec2_model, start=segment['start'], end=segment['end'])
                utils.write_words_to_file(destination_file, words)