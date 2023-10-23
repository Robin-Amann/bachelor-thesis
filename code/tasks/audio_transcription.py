import whisper
import utils.file as utils


def transcribe_dir(speech_dir, transcript_dir, model="whisper") :
    # get model
    if model == 'whisper' :
        transcription_model = whisper.load_model('base')
    else :
        transcription_model = whisper.load_model('base')    
    files = utils.get_directory_files(speech_dir, 'wav')
    for f in files :
        print("transcribe:", str(f))
        stem = f.stem
        parent = str(f.parent)[len(speech_dir) : ] + "\\"
        transcript = transcription_model.transcribe(str(f), fp16 = False)
        transcript = transcript['text']       
        utils.write_file(transcript_dir + parent + stem + ".txt", transcript)





#                                                   WindowsPath(D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html)                       
# str(f)        --> string representation  (\\)     D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html
# f.as_posix()  --> string representation  (/)      D:/Robin_dataset/fisher english/training speech 2/fe_03_p2_sph1/index.html
# f.parent      --> directory                       D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1
# f.name        --> filename (with extention)       index.html
# f.suffix      --> only suffix                     .html
# f.stem        --> file name                       index