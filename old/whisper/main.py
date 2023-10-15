import whisper

model = whisper.load_model('base')
result = model.transcribe("C:\\Users\\robin\\Desktop\\Bachelorarbeit\\whisper\\2m_6269.wav", fp16 = False)

print(result['text'])

# from os.path import exists

# file_exists = exists("C:\\Users\\robin\\Desktop\\Bachelorarbeit\\whisper\\2m_6269.wav")

# print(file_exists)



# whisper

# model = whisper.load_model('base')
# result = model.transcribe("experements_datasets\\Whisper\\2m_6269.wav", fp16 = False)

# print(result['text'])

# audioclient
# open terminal in audioclient directory
# python client.py -I ffmpeg -f D:\Bachelorarbeit-Code\experements_datasets\Whisper\2m_6269.wav --no-textsegmenter --token "EQqkUt3y4gnvky0Zk580nAlBjilU8llXd109fuB749A=|1695822909|uejan@student.kit.edu"

str = "you don't want to be recorded oh I don't care hhh  all right so ah this is for the University of Pensylvannia hhh oh I I still don't mind oh and we've got thirty minutes to talk we've thirty minutes to talk oh ok yeah we've got to talk thirty minutes alright well hhh &=cough er do you have that time I I know I'm I'm prattling with a pro here huh I say I know I'm prattling with a pro here hhh o:kay hhh now"
print(str.lower())
