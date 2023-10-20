import whisper

def transcribe(file_path) :
    model = whisper.load_model('base')
    result = model.transcribe(file_path, fp16 = False)
    return result['text']