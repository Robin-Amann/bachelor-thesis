import tasks.hesitation_predition as prediction
import utils.constants as c

prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.automatic_align_dir / '0', c.retranscibed_dir / 'whisper_large', c.sample_rate, model=prediction.MODELS.whisper_large)
# prediction.predict_dir(c.manual_seg_dir / '20', c.audio_dir, c.automatic_align_dir / '0', c.retranscibed_dir / 'wav2vec2', c.sample_rate, model=prediction.MODELS.wav2vec2)
# prediction.predict_dir(c.manual_seg_dir / '20', c.audio_dir, c.automatic_align_dir / '0', c.retranscibed_dir / 'wav2vec2LM', c.sample_rate, model=prediction.MODELS.wav2vec2LM)
# prediction.predict_dir(c.manual_seg_dir / '20', c.audio_dir, c.automatic_align_dir / '0', c.retranscibed_dir / 'wav2vec2_custom_LM', c.sample_rate, model=prediction.MODELS.wav2vec2_custom_LM)
# prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.automatic_align_dir / '0', c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations', c.sample_rate, model=prediction.MODELS.wav2vec2_custom_LM_hesitations)
