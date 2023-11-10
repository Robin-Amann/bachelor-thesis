import tasks.audio_segmentation as segmentation
import tasks.audio_transcription as transcriptor
import tasks.transcript_normalization as normalizer
import tasks.transcript_alignment.transcript_alignment as transcript_alignment
import tasks.switchboard_transcript_preprocessing.preprocessing as pre
import tasks.audio_transcript_alignment.audio_transcript_alignment as audio_transcript_alignment
import tasks.voice_detection_silero_vad as vad
import utils.constants as dir


# works
pre.process_dir(dir.sb_annotation_dir, dir.sb_timing_dir, dir.sb_manual_transcript_dir, ann_patterns=['<+[^<>]*>+'])

# works
segmentation.sb_segment_directory(dir.sb_manual_transcript_dir, dir.sb_segmented_manual_transcript_dir)

# works
transcriptor.sb_transcribe_dir(dir.sb_segmented_manual_transcript_dir, dir.sb_speech_dir, dir.sb_segmented_automatic_transcript_dir, dir.sample_rate, 'whisper')

# not ready
# normalizer.normalize_directory(dir.sb_segmented_manual_transcript_dir)

# not ready
# normalizer.normalize_directory(dir.sb_segmented_automatic_transcript_dir)

# works
transcript_alignment.sb_align_directory(dir.sb_segmented_manual_transcript_dir, dir.sb_segmented_automatic_transcript_dir, dir.sb_transcript_alignment_dir, True)


audio_transcript_alignment.sb_align_automatic_directory(dir.sb_segmented_manual_transcript_dir, dir.sb_speech_dir, dir.sb_segmented_automatic_transcript_dir, dir.sb_audio_transcript_alignment_dir, dir.sample_rate)

# not ready
# vad.