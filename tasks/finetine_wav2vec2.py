from transformers import AutoFeatureExtractor
import evaluate
import numpy as np
from huggingface_hub import login
from datasets import load_dataset, Audio, ClassLabel
from transformers import AutoModelForAudioClassification, TrainingArguments, Trainer

def download_and_preprocess_dataset() :
    login(token='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')

    ds = load_dataset("Robin-Amann/my_fist_dataset", split='train')
    label_column = [ 1 if x else 0 for x in ds['transcript']]
    ds = ds.add_column('label', label_column)
    ds = ds.remove_columns(['audio_length', 'transcript'])
    ds = ds.cast_column('label', ClassLabel(names=['silence', 'hesitation']))
    ds = ds.cast_column('audio', Audio(sampling_rate=16_000))
    ds = ds.train_test_split(test_size=0.2)

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
        'accuracy' : accuracy_metric.compute(predictions=predictions, references=eval_pred.label_ids),
        'precision' : precision_metric.compute(predictions=predictions, references=eval_pred.label_ids),
        'recall' : recall_metric.compute(predictions=predictions, references=eval_pred.label_ids),
        'f1' : f1_metric.compute(predictions=predictions, references=eval_pred.label_ids)
    }

def train_model(encoded_ds, labels) :

    feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base")

    # conversion
    label2id = { label : i for i, label in enumerate(labels) }
    id2label = { i : label for i, label in enumerate(labels) }
    
    # train model
    num_labels = len(labels)
    model = AutoModelForAudioClassification.from_pretrained(
        "facebook/wav2vec2-base", num_labels=num_labels, label2id=label2id, id2label=id2label
    )

    training_args = TrainingArguments(
        output_dir="audio_hesitation_classification_model",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=32,
        gradient_accumulation_steps=4,
        per_device_eval_batch_size=32,
        num_train_epochs=10,
        warmup_ratio=0.1,
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
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

    trainer.train()

    trainer.push_to_hub()