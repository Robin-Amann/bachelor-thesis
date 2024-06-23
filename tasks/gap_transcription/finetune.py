import re
import json
from transformers import Wav2Vec2CTCTokenizer, Wav2Vec2FeatureExtractor, Wav2Vec2Processor
from transformers import Wav2Vec2ForCTC
from transformers import TrainingArguments, Trainer
from transformers import AutoModelForCTC, Wav2Vec2Processor
import torch
from dataclasses import dataclass
from typing import Dict, List, Union
import numpy as np
from huggingface_hub import login
from datasets import load_dataset
import utils.constants as c
import evaluate


# https://huggingface.co/blog/fine-tune-wav2vec2-english
# https://colab.research.google.com/github/patrickvonplaten/notebooks/blob/master/Fine_tuning_Wav2Vec2_for_English_ASR.ipynb#scrollTo=Gx9OdDYrCtQ1
# finetune wav2vec2

chars_to_ignore_regex = '[\,\?\.\!\-\;\:\"]'
repo_name = "wav2vec2-base-sb-finetune"

# UserWarning: `as_target_processor` is deprecated and will be removed in v5 of Transformers. 
# You can process your labels by using the argument `text` of the regular `__call__` method (either in the same call as your audio inputs, or in a separate call.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  

def load_datset(name='gap_dataset') :
    def remove_special_characters(batch):
        batch["text"] = re.sub(chars_to_ignore_regex, '', batch["transcript"]).lower() + " "
        return batch

    login(token='old token is invalid')

    ds = load_dataset("Robin-Amann/" + name)

    ds = ds.map(remove_special_characters)
    ds = ds.remove_columns(['audio_length', 'transcript', 'label'])
    print(ds)
    return ds


def setup_tokenizer(ds) :
    def extract_all_chars(batch):
        all_text = " ".join(batch["text"])
        vocab = list(set(all_text))
        return {"vocab": [vocab], "all_text": [all_text]}
    
    vocabs = ds.map(extract_all_chars, batched=True, batch_size=-1, keep_in_memory=True, remove_columns=ds.column_names["train"])
    vocab_list = list(set(vocabs["train"]["vocab"][0]) | set(vocabs["test"]["vocab"][0]))
    vocab_dict = {v: k for k, v in enumerate(vocab_list)}
    vocab_dict["|"] = vocab_dict[" "]
    del vocab_dict[" "]
    vocab_dict["[UNK]"] = len(vocab_dict)
    vocab_dict["[PAD]"] = len(vocab_dict)

    with open('vocab.json', 'w') as vocab_file:
        json.dump(vocab_dict, vocab_file)

    tokenizer = Wav2Vec2CTCTokenizer("./vocab.json", unk_token="[UNK]", pad_token="[PAD]", word_delimiter_token="|")
    tokenizer.push_to_hub(repo_name)
    return tokenizer


@dataclass
class DataCollatorCTCWithPadding:
    """
    Data collator that will dynamically pad the inputs received.
    Args:
        processor (:class:`~transformers.Wav2Vec2Processor`)
            The processor used for proccessing the data.
        padding (:obj:`bool`, :obj:`str` or :class:`~transformers.tokenization_utils_base.PaddingStrategy`, `optional`, defaults to :obj:`True`):
            Select a strategy to pad the returned sequences (according to the model's padding side and padding index)
            among:
            * :obj:`True` or :obj:`'longest'`: Pad to the longest sequence in the batch (or no padding if only a single
              sequence if provided).
            * :obj:`'max_length'`: Pad to a maximum length specified with the argument :obj:`max_length` or to the
              maximum acceptable input length for the model if that argument is not provided.
            * :obj:`False` or :obj:`'do_not_pad'` (default): No padding (i.e., can output a batch with sequences of
              different lengths).
    """

    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lenghts and need
        # different padding methods
        input_features = [{"input_values": feature["input_values"]} for feature in features]
        label_features = [{"input_ids": feature["labels"]} for feature in features]

        batch = self.processor.pad(
            input_features,
            padding=self.padding,
            return_tensors="pt",
        )
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(
                label_features,
                padding=self.padding,
                return_tensors="pt"
            )

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        batch["labels"] = labels

        return batch
    

def build_trainer(model, processor, ds) :
    data_collator = DataCollatorCTCWithPadding(processor=processor, padding=True)
    wer_metric = evaluate.load("wer")


    def compute_metrics(pred):
        pred_logits = pred.predictions
        pred_ids = np.argmax(pred_logits, axis=-1)

        pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

        pred_str = processor.batch_decode(pred_ids)
        # we do not want to group tokens when computing the metrics
        label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

        wer = wer_metric.compute(predictions=pred_str, references=label_str)
        
        return {"wer": wer}

    training_args = TrainingArguments(
        output_dir=str(c.data_base / repo_name),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=1e-4,
        per_device_train_batch_size=32,
        gradient_accumulation_steps=4,
        per_device_eval_batch_size=32,
        num_train_epochs=10,
        warmup_ratio=0.1,
        load_best_model_at_end=True,
        gradient_checkpointing=True,
        push_to_hub=True,
    )

    trainer = Trainer(
        model=model,
        data_collator=data_collator,
        args=training_args,
        compute_metrics=compute_metrics,
        train_dataset=ds["train"],
        eval_dataset=ds["test"],
        tokenizer=processor.feature_extractor,
    )

    return trainer


def finetune() :
    ds = load_datset()
    tokenizer = setup_tokenizer(ds)
    feature_extractor = Wav2Vec2FeatureExtractor(feature_size=1, sampling_rate=16000, padding_value=0.0, do_normalize=True, return_attention_mask=False)
    processor = Wav2Vec2Processor(feature_extractor=feature_extractor, tokenizer=tokenizer)

    def prepare_dataset(batch):
        audio = batch["audio"]

        batch["input_values"] = processor(audio["array"], sampling_rate=audio["sampling_rate"]).input_values[0]
        batch["input_length"] = len(batch["input_values"])
        
        with processor.as_target_processor():
            batch["labels"] = processor(batch["text"]).input_ids
        return batch

    ds = ds.map(prepare_dataset, remove_columns=ds.column_names["train"], num_proc=4)

    model = Wav2Vec2ForCTC.from_pretrained(
        "facebook/wav2vec2-base",
        ctc_loss_reduction="mean", 
        pad_token_id=processor.tokenizer.pad_token_id,
    )

    model.freeze_feature_encoder()

    trainer = build_trainer(model, processor, ds)
    trainer.train()
    trainer.push_to_hub()


    
def evaluate_model() :
    login(token='old token is invalid')
    ds = load_dataset("Robin-Amann/gap_dataset")

    processor = Wav2Vec2Processor.from_pretrained("Robin-Amann/wav2vec2-base-sb-finetune")
    model = Wav2Vec2ForCTC.from_pretrained("Robin-Amann/wav2vec2-base-sb-finetune").cuda()

    
    wer_metric = evaluate.load("wer")

    def map_to_result(batch):
        with torch.no_grad():
            input_values = torch.tensor(batch["input_values"], device="cuda").unsqueeze(0)
            logits = model(input_values).logits

        pred_ids = torch.argmax(logits, dim=-1)
        batch["pred_str"] = processor.batch_decode(pred_ids)[0]
        batch["text"] = processor.decode(batch["labels"], group_tokens=False)
        
        return batch

    results = ds["test"].map(map_to_result, remove_columns=ds["test"].column_names)

    print("Test WER: {:.3f}".format(wer_metric.compute(predictions=results["pred_str"], references=results["text"])))
