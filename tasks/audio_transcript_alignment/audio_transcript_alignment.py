import torch
import torchaudio
import utils.file as utils
import tasks.audio_transcript_alignment.ctc as ctc
from progress.bar import ChargingBar
import os
import utils.constants as constants
import utils.transcript as word_utils


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_args = {'model_dir' : str(constants.model_dir / 'wav2vec2')}

def transform_result(ratio, words, sample_rate) :
    result = []
    decimals = 3
    for w in words :
        result.append( {
            "word": w.label, 
            "start": w.start * ratio / sample_rate, 
            "end": w.end * ratio / sample_rate, 
            "score": round(w.score, decimals)
            } )
    return result


def align(audio_file, transcript_file, sample_rate, wav2vec2_model, start=-1, end=-1) :
    audio = utils.read_audio(audio_file, sample_rate)  # [ [...] ]
    original_transcript = utils.read_file(transcript_file)
    if start >= 0 and end > 0 and start < end :
        audio = audio[:, start : end]
        if (end - start) / sample_rate < 0.5 :
            print("\naudio too small:", (end - start) / sample_rate)
            print("transcript:     ", original_transcript)
            print(audio_file)
            return []
    transcript = original_transcript.split()
    simple = [ word_utils.simplify(w) for w in transcript ]
    if not all(simple) : # if simple contains empty words
        raise ValueError('transcript contains non words', transcript_file.stem)
    transcript = '|' + '|'.join(simple).upper() + '|'
    # transcript = "|I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT|"
    # transcript = "|I|HAD|THAT|CURIOSITY|AT|THIS|MOMENT|"
    labels, emission = ctc.get_emission(audio, device, wav2vec2_model)
    words, trellis_width = ctc.ctc(emission, transcript, labels, whitespace_stay_default_value=0)
    # import tasks.audio_transcript_alignment.visualization as visual
    # trellis, tokens = ctc.get_trellis(emission, transcript, labels, whitespace_stay_default_value=1)
    # visual.plot_alignments(trellis, words, audio[0], sample_rate)

    ratio = audio[0].size(0) / trellis_width
    words = transform_result(ratio, words, sample_rate)
    if words :
        for word, t in zip(words, original_transcript.split()) :
            word['word'] = t
    return words


def align_file(audio_file, transcript_file, sample_rate, wav2vec2_model=None, start=-1, end=-1) :
    if wav2vec2_model == None :
        bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
        model = bundle.get_model(dl_kwargs=model_args).to(device)
        wav2vec2_model = (bundle, model)

    transcript = utils.read_file(transcript_file)
    
    # if transcript is empty so there can be made no alignment
    if transcript and not transcript.isspace() :
        words = align(audio_file, transcript_file, sample_rate, wav2vec2_model, int(start*sample_rate), int(end*sample_rate))
        if not words :
            utils.write_file(constants.error_dir / 'audio_transcript_alignment.txt', "could not align: " + transcript_file.stem + "\n", mode='a')
            # divide words equally in audio and five inf score
            transcript = transcript.split()
            n = len(transcript)
            l = end - start
            for i, t in  enumerate(transcript):
                words.append( {
                    "word": t, 
                    "start": i/n * l, 
                    "end": (i+1)/n * l, 
                    "score": float('inf')
                    } )
        return words
    else :
        return []


def align_dir(segments_dir, audio_dir, transcript_dir, destination_dir, sample_rate) :
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
    model = bundle.get_model(dl_kwargs=model_args).to(device)
    wav2vec2_model = (bundle, model)
    print('device:', device)
    print('os:', os.name)

    files = utils.get_dir_tuples([ (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), (audio_dir, lambda f : f.stem[3:8], None, 'wav'), (transcript_dir, lambda f : f.stem[2:7])] )
    grouped = utils.group_files(files, 3)

    for p in [ k for k in grouped.keys() if int(k) >= 8] :
        print("Align dir", p)
        for segment_file, audio_file, transcript_files in ChargingBar("Align Transcript to Audio").iter(grouped[p]) :
            stem = segment_file.stem
            segments = utils.read_dict(str(segment_file))
            for transcript_file in transcript_files :
                index = int( transcript_file.stem[7:10] )
                segment = segments[index]
                destination_file = utils.repath(segment_file, segments_dir, destination_dir, [stem[6]], stem=transcript_file.stem, suffix=transcript_file.suffix)
                words = align_file(audio_file, transcript_file, sample_rate, wav2vec2_model, start=segment['start'], end=segment['end'])
                utils.write_dict(destination_file, words)