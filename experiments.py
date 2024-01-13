# # do interference
# from datasets import load_dataset, Audio

# dataset = load_dataset("PolyAI/minds14", name="en-US", split="train")
# dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
# sampling_rate = dataset.features["audio"].sampling_rate
# audio_file = dataset[0]["audio"]["path"]

# from transformers import pipeline

# classifier = pipeline("audio-classification", model="stevhliu/my_awesome_minds_model")

# result = classifier(audio_file)

# print(result)

import evaluate

accuracy_metric = evaluate.load('accuracy')
precision_metric = evaluate.load('precision')
recall_metric = evaluate.load('recall')

print(accuracy_metric)
