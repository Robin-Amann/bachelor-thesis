import torch
import torchaudio
import utils.file as loader
import utils.alignment_metric as metric
import audio_transcript_alignment.ctc_extention as ctc
import voice_detection.voice_detection_silero_vad as voice_activation
# import audio_transcription.whisper_model as whisper
import visualization.visualize as visual
import hesitation_prediction.audio_utils as audio
import hesitation_prediction.model as predictor


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sample_rate = 16000


def process(audio_file, waveform, transcript) :
    words = ctc.full_alignment(waveform, transcript, device)    # list of {transcript, start, end, score}
    # words = ctc.base_ctc(waveform, transcript, device)    # list of {transcript, start, end, score}
    speech_timestamps = voice_activation.voice_activation_detection(audio_file, sample_rate) # list of {start, end}
    audio_fragments = audio.get_untranscribed_audio(waveform, words, speech_timestamps, sample_rate)    # list of {start, end, audio, speech = {start, end}}   speech is relative
    hesitations = predictor.predict(audio_fragments)    # list of {start, end, label}   speech is relative
    return words, speech_timestamps, hesitations


# example
audio_file = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript_manual = "I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT"
transcript_whisper = "I|HAD|THAT|BESIDE|ME|AT|THIS|MOMENT"  # metric: 0.964

print("audiofile sample rate:", torchaudio.info(audio_file).sample_rate)
waveform = loader.load_audio(audio_file, sample_rate)

words_manual, speech_timestamps_manual, hesitations_manual = process(audio_file, waveform, transcript_manual)
words_whisper, speech_timestamps_whisper, hesitations_whisper = process(audio_file, waveform, transcript_whisper)

manual_metric = [{'transcript': i['transcript'], 'start': i['start'] / sample_rate, 'end': i['end'] / sample_rate,} for i in words_manual[:3] + words_manual[4:]]
whisper_metric = [{'transcript': i['transcript'], 'start': i['start'] / sample_rate, 'end': i['end'] / sample_rate,} for i in words_whisper]
print(metric.alignment_error(manual_metric, whisper_metric))
visual.plot_alignment_comparison(waveform[0], [words_manual, words_whisper], [speech_timestamps_manual, speech_timestamps_whisper], ["Manual", "Whisper"], sample_rate)

# visual.plot_words_and_speech(waveform[0], words, speech_timestamps, sample_rate)
# visual.plot_gaps(waveform[0], audio_fragments, sample_rate)



# examples
audio_file = torchaudio.utils.download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
transcript = "I|HAD|THAT|CURIOSITY|BESIDE|ME|AT|THIS|MOMENT"

audio_file = ".\\audio_alignment\\data\\sample_data\\4s.wav"
transcript = "ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"

audio_file = ".\\audio_alignment\\data\\sample_data\\10s.wav"
transcript = "THEY|MIGHT|CANCEL|MY|INSURANCE|WELL|I|THINK|THAT'S|THE|BEST|THING|POSSIBILITY|ALTHOUGH|UH|SOMETIME|AGO|I|GO|UH"


audio_file = ".\\audio_alignment\\data\\sample_data\\fisher_english\\fe_03_00001_78_to_82.wav"
transcript_manual = "MY|FRIEND|IS|ACTUALLY|UM|PAR-|ONE|OF|THE|PEOPLE|RUNNING|THIS|STUDY|I|GUESS"           # "my friend is actually um par- one of the people running this study i guess"  manual
transcript_whisper = "MY|FRIEND|IS|ACTUALLY|PART|ONE|OF|PEOPLE|RUNNING|THIS|STUDY|I|GUESS"                  # "My friend is actually part, one of people running this study, I guess."      whisper

audio_file = ".\\audio_alignment\\data\\sample_data\\fisher_english\\fe_03_00003_420_to_438.wav"
transcript_manual = "OKAY|AND|OF|COURSE|I|ALWAYS|LIKE|TO|EAT|THE|UM|WINE|DO|YOU|DO|WINE|UM|NOT|REALLY"                             # "okay and of course i always like to eat the [laugh] [laugh] [laugh] [breath] um wine, do you do wine um not really"   manual
transcript_whisper = "BECAUSE|I|ALWAYS|LIKE|TO|EAT|SWEET|FATS|KIM|MM-HMM|MM-HMM|MM-HMM|UM|WINE|DO|YOU|DO|WINE|UM|NOT|REALLY"        # "Because I always like to eat sweet fats, Kim. Mm-hmm. Mm-hmm. Mm-hmm. Um... Wine? Do you do wine? Um, not really."   whisper


audio_file = ".\\audio_alignment\\data\\sample_data\\fisher_english\\fe_03_00003_58_to_70.wav"
transcript_manual = "YOU|DON'T|I'VE|YOU|DON'T|HAVE|TO|UM|ORDER|AND|WAIT|RIGHT|OF|COURSE|YOU|DO|HAVE|TO|STAND|IN|THE|KITCHEN|AND|COOK|THE|FOOD"          # you don't (( )) i've you don't have to um order and wait [laugh] right of course you do have to stand in the kitchen and cook the food        # manual
transcript_whisper = "YOU|DON'T|HAVE|TO|FIVE|YOU|DON'T|HAVE|TO|ORDER|AND|WAIT|RIGHT|OF|COURSE|YOU|DO|HAVE|TO|STAND|IN|THE|KITCHEN|AND|COOK|THE|FOOD"    # You don't have to... five. You don't have to order and wait. Right. Of course you do have to stand in the kitchen and cook the food.


audio_file = ".\\audio_alignment\\data\\sample_data\\fisher_english\\fe_03_00003_26_to_42.wav"
transcript_manual = "I|LIKE|YEAH|I|LIKE|THE|RELAXED|ATMOSPHERE|AND|UM|WOULD|RIGHT|UM|WELL|UM|IT'S|JUST|YOU|CAN|JUST|REALLY|RELAX|AND|TALK|WITH|YOUR|SPOUSE|IF|YOU|HAVE|A|SPOUSE"    #"i like yeah i like the relaxed atmosphere and um would right um well  um it's just you can just really relax and talk with your spouse if you have a spouse"
transcript_whisper = "I|LIKE|THE|RELAXED|ATMOSPHERE|WELL|YOU|CAN|JUST|REALLY|RELAX|AND|TALK|WITH|YOUR|SPOUSE|IF|YOU|HAVE|A|SPOUSE"                                                  # "I like the relaxed atmosphere. Well, you can just really relax and talk with your spouse if you have a spouse."


