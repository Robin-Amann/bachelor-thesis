import audio_transcription.transcibe as transcriber

data_directory = "code\\sample_data\\segmented"
transcriber.transcribe_dir(data_directory, data_directory)
