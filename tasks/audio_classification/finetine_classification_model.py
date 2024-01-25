from transformers import AutoFeatureExtractor, AutoModelForAudioClassification, TrainingArguments, Trainer
from huggingface_hub import login
from datasets import load_dataset
import numpy as np
import evaluate
import utils.constants as c

def preprocess_dataset() :
    login(token='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')

    ds = load_dataset("Robin-Amann/my_first_dataset")
    # label_column = [ 1 if x else 0 for x in ds['transcript']]
    # ds = ds.add_column('label', label_column)
    ds = ds.remove_columns(['audio_length', 'transcript'])
    # ds = ds.cast_column('label', ClassLabel(names=['silence', 'hesitation']))
    # ds = ds.cast_column('audio', Audio(sampling_rate=16_000))
    # ds = ds.train_test_split(test_size=0.2)

    labels = ds["train"].features["label"].names

    # preprocess dataset
    feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base")

    def preprocess_function(examples):
        audio_arrays = [x["array"] for x in examples["audio"]]
        inputs = feature_extractor(
            audio_arrays, sampling_rate=feature_extractor.sampling_rate, max_length=16000, truncation=True
        )
        return inputs
    encoded_ds = ds.map(preprocess_function, remove_columns="audio", batched=True)

    return encoded_ds, labels


accuracy_metric = evaluate.load('accuracy')
precision_metric = evaluate.load('precision')
recall_metric = evaluate.load('recall')
f1_metric = evaluate.load('f1')


def compute_metrics(eval_pred):
    predictions = np.argmax(eval_pred.predictions, axis=1)
    return {
        'accuracy' : accuracy_metric.compute(predictions=predictions, references=eval_pred.label_ids)['accuracy'],
        'precision' : precision_metric.compute(predictions=predictions, references=eval_pred.label_ids)['precision'],
        'recall' : recall_metric.compute(predictions=predictions, references=eval_pred.label_ids)['recall'],
        'f1' : f1_metric.compute(predictions=predictions, references=eval_pred.label_ids)['f1']
    }

def train_model(encoded_ds, labels) :

    feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base")

    # conversion
    label2id = { label : i for i, label in enumerate(labels) }
    id2label = { i : label for i, label in enumerate(labels) }
    
    # train model
    num_labels = len(labels)
    # https://github.com/huggingface/transformers/blob/83f9196cc44a612ef2bd5a0f721d08cb24885c1f/src/transformers/models/wav2vec2/modeling_wav2vec2.py#L4
    # line 2161
    # uses linear layer for classification
    # pipeline uses max output value

    # https://huggingface.co/docs/transformers/training#trainer
    # triner only trains classification head
    model = AutoModelForAudioClassification.from_pretrained(
        "facebook/wav2vec2-base", num_labels=num_labels, label2id=label2id, id2label=id2label
    )

    training_args = TrainingArguments(
        output_dir= str(c.data_base / 'classification_model'),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=32,
        gradient_accumulation_steps=4,
        per_device_eval_batch_size=32,
        num_train_epochs=10,
        warmup_ratio=0.1,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        push_to_hub=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=encoded_ds["train"],
        eval_dataset=encoded_ds["test"],
        tokenizer=feature_extractor,
        compute_metrics=compute_metrics,
    )

    print('\n\n', '# # # Start # # #', '\n\n', sep='')    
    trainer.train()

    print('\n\n', '# # # Upload # # #', '\n\n', sep='')
    trainer.push_to_hub()
