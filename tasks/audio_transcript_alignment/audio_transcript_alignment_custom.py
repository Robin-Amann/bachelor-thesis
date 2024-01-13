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
            "transcript": w.label, 
            "start": w.start * ratio / sample_rate, 
            "end": w.end * ratio / sample_rate, 
            "score": round(w.score, decimals)
            } )
    return result


def align(audio_file, transcript_file, sample_rate, wav2vec2_model, start=-1, end=-1, whitespace_stay_default_value = []) :
    audio = utils.read_audio(audio_file, sample_rate)  # [ [...] ]
    original_transcript = utils.read_file(transcript_file)
    if start >= 0 and end > 0 and start < end :
        audio = audio[:, start : end]
        if (end - start) / sample_rate < 0.5 :
            print("\naudio too small:", (end - start) / sample_rate)
            print("transcript:     ", original_transcript)
            print(audio_file)
            return [ [] for _ in range(len(whitespace_stay_default_value)) ]
    transcript = original_transcript.split()
    simple = [ word_utils.simplify(w) for w in transcript ]
    if not all(simple) : # if simple contains empty words
        raise ValueError('transcript contains non words', transcript_file.stem)
    transcript = '|' + '|'.join(simple).upper() + '|'
    labels, emission = ctc.get_emission(audio, device, wav2vec2_model)
    results = []
    for value in whitespace_stay_default_value :
        words, trellis_width = ctc.ctc(emission, transcript, labels, whitespace_stay_default_value=value)
        ratio = audio[0].size(0) / trellis_width
        words = transform_result(ratio, words, sample_rate)
        if words :
            for word, t in zip(words, original_transcript.split()) :
                word['word'] = t
        results.append(words)
    return results


def align_file(audio_file, transcript_file, sample_rate, wav2vec2_model=None, start=-1, end=-1, whitespace_stay_default_value = []) :
    if wav2vec2_model == None :
        bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
        model = bundle.get_model(dl_kwargs=model_args).to(device)
        wav2vec2_model = (bundle, model)

    transcript = utils.read_file(transcript_file)
    
    # if transcript is empty so there can be made no alignment
    if transcript and not transcript.isspace() :
        results = align(audio_file, transcript_file, sample_rate, wav2vec2_model, int(start*sample_rate), int(end*sample_rate), whitespace_stay_default_value=whitespace_stay_default_value)
        if not all( ws for ws in results ) :
            utils.write_file(constants.error_dir / 'audio_transcript_alignment.txt', "could not align: " + transcript_file.stem + "\n", mode='a')
            # divide words equally in audio and five inf score
            transcript = transcript.split()
            n = len(transcript)
            l = end - start
            for words in results :
                words = []
                for i, t in  enumerate(transcript):
                    words.append( {
                        "transcript": t, 
                        "start": i/n * l, 
                        "end": (i+1)/n * l, 
                        "score": float('inf')
                        } )
        return results
    else :
        return [ [] for _ in range(len(whitespace_stay_default_value)) ]


def align_dir(segments_dir, audio_dir, transcript_dir, destination_dir: list, sample_rate, whitespace_stay_default_value : list) :
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
    model = bundle.get_model(dl_kwargs=model_args).to(device)
    wav2vec2_model = (bundle, model)
    print('device:', device)
    print('os:', os.name)

    files = utils.get_dir_tuples([ (segments_dir, lambda f : f.stem[2:7], lambda f : 'Speech' in f.stem), (audio_dir, lambda f : f.stem[3:8], None, 'wav'), (transcript_dir, lambda f : f.stem[2:7])] )
    grouped = utils.group_files(files, 3)

    for p in [ k for k in grouped.keys() if 32 <= int(k) <= 49 ] :
        print("Align dir", p)
        for segment_file, audio_file, transcript_files in ChargingBar("Align Transcript to Audio").iter(grouped[p]) :
            stem = segment_file.stem
            segments = utils.read_dict(str(segment_file))
            for transcript_file in transcript_files :
                index = int( transcript_file.stem[7:10] )
                segment = segments[index]
                destination_files = []
                for value in whitespace_stay_default_value :
                    destination_file = utils.repath(segment_file, segments_dir, destination_dir / str(-value), [stem[6]], stem=transcript_file.stem, suffix=transcript_file.suffix)
                    destination_files.append(destination_file)
                results = align_file(audio_file, transcript_file, sample_rate, wav2vec2_model, start=segment['start'], end=segment['end'], whitespace_stay_default_value=whitespace_stay_default_value)
                for destination_file, words in zip(destination_files, results) :
                    utils.write_dict(destination_file, words)