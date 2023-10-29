from nemo_text_processing.text_normalization.normalize import Normalizer
import utils.file as utils
import os
from progress.bar import ChargingBar

def normalize(file_path, normalizer = None, filename_extention = None) :
    if normalizer == None :
        normalizer = Normalizer(input_case='cased', lang='en')
    transcipt = utils.read_file(file_path)
    transcipt = transcipt.split('\n')
    transcipt = normalizer.normalize_list(transcipt, punct_post_process=True)
    if filename_extention != None:
        utils.write_file(file_path[:-4] + "_" + filename_extention + ".txt", '\n'.join(transcipt))
    else :
        utils.write_file(file_path, '\n'.join(transcipt))    

def normalize_directory(directory_path, filename_extention = None) :
    files = utils.get_directory_files(directory_path, "txt")
    normalizer = Normalizer(input_case='cased', lang='en')
    for file in ChargingBar("Normalize Transcript").iter(files) :
        normalize(str(file), normalizer, filename_extention)    

# normalized = normalizer.normalize(transcipt, verbose=False, punct_post_process=True)
        