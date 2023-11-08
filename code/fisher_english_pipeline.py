import tasks.vocabulary_extraction as vocabulary_extraction
import tasks.audio_segmentation as segmentation
import tasks.audio_transcription as transcriptor
import tasks.transcript_normalization as normalizer
import tasks.transcript_alignment.transcript_alignment as transcript_alignment
import tasks.audio_transcript_alignment.audio_transcript_alignment as audio_transcript_alignment
import tasks.audio_labeling as labeling
import utils.constants as dir


segmentation.fe_segment_directory(dir.speech_dir, dir.transcript_dir, dir.segmented_speech_dir, dir.segmented_transcript_dir, dir.sample_rate)

transcriptor.transcribe_dir(dir.segmented_speech_dir, dir.whisper_dir, 'whisper')

normalizer.normalize_directory(dir.segmented_transcript_dir)

normalizer.normalize_directory(dir.whisper_dir)

transcript_alignment.align_directory(dir.segmented_transcript_dir, dir.whisper_dir, dir.transcript_alignment_dir, True)

audio_transcript_alignment.align_directory(dir.segmented_speech_dir, dir.segmented_transcript_dir, dir.audio_transcript_alignment_dir, dir.sample_rate)

labeling.label_directory(dir.segmented_speech_dir, dir.audio_transcript_alignment_dir, dir.sample_rate)