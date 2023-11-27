import tasks.hesitation_predition as prediction
import utils.constants as c

prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.audio_automatic_align_dir, c.hesitation_dir, c.sample_rate, model='ctc')