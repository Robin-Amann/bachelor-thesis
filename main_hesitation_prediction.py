import tasks.audio_classification.dataset_creation as dataset
import tasks.audio_classification.finetine_classification_model as finetune
import tasks.audio_classification.classification_interference as classification
import tasks.hesitation_predition as prediction
import utils.constants as c

DATA_SPLIT = 3916

# # create dataset
# dataset.create_dataset_files(upper_bound=DATA_SPLIT)
# dataset.create_dataset()

# # classify gaps
# encoded_ds, labels = finetune.preprocess_dataset()
# finetune.train_model(encoded_ds, labels)
classification.classify_audio_dir(c.manual_seg_dir, c.audio_dir, c.automatic_align_dir / '0', c.classification_dir, c.sample_rate, lower_bound=DATA_SPLIT)

# retranscribe
for model in [prediction.MODELS.whisper_large, prediction.MODELS.wav2vec2, prediction.MODELS.wav2vec2LM, prediction.MODELS.wav2vec2_custom_LM, prediction.MODELS.wav2vec2_custom_LM_hesitations] :
    # whisper_large and wav2vec2_custom_LM_hesitations is already retranscribed
    if model == prediction.MODELS.whisper_large or model == prediction.MODELS.wav2vec2_custom_LM_hesitations :
        continue
    prediction.predict_dir(c.manual_seg_dir, c.audio_dir, c.classification_dir, c.retranscibed_dir / model.name, c.sample_rate, model=model)
