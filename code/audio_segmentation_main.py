import audio_segmentation.audio_segmentation as segmentation
import utils.file as loader

sample_rate = 16000
data_directory = "code\\sample_data\\"
transcript = loader.read_file(data_directory + "manual_fe_03_00001.txt")
waveform = loader.read_audio(data_directory + "fe_03_00001.wav", sample_rate)

speech_A = waveform[0]
speech_B = waveform[1]
transcript_A, transcript_B = segmentation.extract_speaker(transcript)

A = segmentation.segment(transcript_A, speech_A, sample_rate)
B = segmentation.segment(transcript_B, speech_B, sample_rate)

for i, a in enumerate(A[:3]) :
    loader.write_audio(data_directory +  "segmented\\fe_03_00001_" + str(i) + ".wav", a['audio'], sample_rate)
    loader.write_file(data_directory + "segmented\\manual_fe_03_00001_" + str(i) + ".txt", a['transcript'])
