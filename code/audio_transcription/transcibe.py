import pathlib
from . import whisper_model as whisper
from . import audioclient_model as audioclient
import os

def get_directory_files(directory, filetype) :
    files = [f for f in pathlib.Path(directory).glob("**\*." + filetype)]    
    return files


def transcribe_dir(speech_dir, transcript_dir, model="whisper") :
    files = get_directory_files(speech_dir, 'wav')
    for f in files :
        print(f.stem)
        if model == 'whisper' :
            transcript = whisper.transcribe(str(f))
        else :
            transcript = audioclient.transcribe(str(f))
        transcript_location =  f'{transcript_dir}{str(f.parent)[len(speech_dir) : ]}\\whisper_{f.stem}.txt'
        print(transcript_location)
        os.makedirs(os.path.dirname(transcript_location), exist_ok=True)
        with open(transcript_location, "w", encoding="utf8") as tf :
            tf.write(transcript)


# stub = "D:\\Robin_dataset\\fisher english" 
# speech_dir = stub + "\\training speech 1 only wav\\d1\\audio\\000"
# transcript_dir = stub + "\\whisper transcript\\000"
# transcribe_dir(speech_dir, transcript_dir)
        
# files = get_directory_files('D:\\Robin_dataset\\fisher english', 'html')
# f = files[0]
#                                                   WindowsPath(D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html)                       
# str(f)        --> string representation  (\\)     D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html
# f.as_posix()  --> string representation  (/)      D:/Robin_dataset/fisher english/training speech 2/fe_03_p2_sph1/index.html
# f.parent      --> directory                       D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1
# f.name        --> filename (with extention)       index.html
# f.suffix      --> only suffix                     .html
# f.stem        --> file name                       index