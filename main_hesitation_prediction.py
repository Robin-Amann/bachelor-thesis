import tasks.hesitation_predition as prediction
import utils.constants as c

prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.automatic_align_dir, c.retranscibed_dir / 'wav2vec2_custom_LM_hesitations', c.sample_rate, model=prediction.MODELS.wav2vec2_custom_LM_hesitations)