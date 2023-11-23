import torch
from transformers import AutoProcessor, WhisperForConditionalGeneration
from datasets import load_dataset

processor = AutoProcessor.from_pretrained("openai/whisper-tiny.en")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny.en")

ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")

inputs = processor(ds[0]["audio"]["array"], return_tensors="pt")
input_features = inputs.input_features

generated_ids = model.generate(inputs=input_features, return_token_timestamps=True)

print(generated_ids.token_timestamps.shape)
print(generated_ids.sequences.shape)

print(generated_ids.token_timestamps)
print(generated_ids.sequences)

transcription = processor.batch_decode(generated_ids.sequences, skip_special_tokens=True)[0]
print(transcription)

# print(generated_ids2.token_timestamps.shape)
# print(generated_ids2.sequences.shape)