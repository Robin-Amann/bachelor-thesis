import tasks.audio_segmentation as segmentation
import tasks.audio_transcription as transcriptor
import tasks.transcript_normalization as normalizer
import tasks.transcript_alignment as transcript_alignment
import tasks.preprocessing.preprocessing as pre
import tasks.audio_transcript_alignment.audio_transcript_alignment as audio_transcript_alignment
import tasks.voice_detection_silero_vad as vad
import utils.constants as constants


# pre.process_dir(constants.disfluencies_dir, constants.timing_dir, constants.manual_dir, ann_patterns=constants.manual_annotation_patterns)

# segmentation.segment_dir(constants.manual_dir, constants.manual_seg_dir)

# transcriptor.transcribe_dir(constants.manual_seg_dir, constants.audio_dir, constants.automatic_dir , constants.sample_rate, transcriptor.MODELS.whisper)
# transcriptor.transcribe_dir(constants.manual_seg_dir, constants.audio_dir, constants.data_base / 'automatic' / 'version3', constants.sample_rate, transcriptor.MODELS.whisper_large_v3)

# # normalizer.normalize_dir(constants.manual_seg_dir, dataset= 'switchboard')
# normalizer.normalize_dir(constants.automatic_dir, dataset= 'whisper')

audio_transcript_alignment.align_dir(constants.manual_seg_dir, constants.audio_dir, constants.automatic_dir, constants.automatic_align_dir, constants.sample_rate)

