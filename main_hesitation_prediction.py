import tasks.audio_classification.dataset_creation as dataset
import tasks.audio_classification.finetine_classification_model as finetune
import tasks.audio_classification.classification_interference as classification
import tasks.hesitation_predition as prediction
import utils.constants as c



# # create dataset
# dataset.create_dataset_files(upper_bound=c.DATA_SPLIT)
# dataset.create_dataset()

# # classify gaps
# encoded_ds, labels = finetune.preprocess_dataset()
# finetune.train_model(encoded_ds, labels)
# classification.classify_audio_dir(c.manual_seg_dir, c.audio_dir, c.automatic_align_dir / 'custom ctc' / '0_01', c.classification_dir / 'custom ctc', c.sample_rate, lower_bound=c.DATA_SPLIT, start_dir=40, end_dir=40)

# retranscribe
# prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.classification_dir / 'custom ctc', 
#                        c.retranscibed_dir / 'custom ctc' / prediction.MODELS.whisper_large.name, c.sample_rate, model=prediction.MODELS.whisper_large,
#                        start=41)
# prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.classification_dir / 'custom ctc', 
#                        c.retranscibed_dir / 'custom ctc' / prediction.MODELS.wav2vec2.name, c.sample_rate, model=prediction.MODELS.wav2vec2)
prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.classification_dir / 'custom ctc', 
                       c.retranscibed_dir / 'custom ctc' / prediction.MODELS.wav2vec2LM.name, c.sample_rate, model=prediction.MODELS.wav2vec2LM)
for model in [prediction.MODELS.wav2vec2_custom_LM, prediction.MODELS.wav2vec2_custom_LM_hesitations] :
    prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.classification_dir / 'custom ctc', c.retranscibed_dir / 'custom ctc' / model.name, c.sample_rate, model=model, end_dir=40)
