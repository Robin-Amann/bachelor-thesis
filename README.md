This code is structured in the following way:

data
- error messanges and some metadata

hesitation_prediction
- contains an text file with code. this code can be executed in a jupiter notebook to create an n-gram

statistsics complete
- methods for statistical purposes

supervised_data_preperation
- code snipets used to find damaged or missing data in the switchboard dataset

tasks
- every major task has one file / folder. all of it is self explainatory

utils
- utils and constants
- here is also a list of all damaged or missing files together with a list of all file parts that are not usable due to too much noise
- the file.py script is especially usefull
  
some main files that can be executed.
- each main file contains all comands necessary to execte the whole code.

to execute the code create a conda enviroment and install the following dependencies:
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
  or (with cuda): conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install cython
conda install -c conda-forge pynini=2.1.5
pip install nemo-text-processing
pip install openai-whisper progress soundfile huggingface-hub matplotlib numpy transformers datasets librosa
pip install pyctcdecode==0.3.0 https://github.com/kpu/kenlm/archive/master.zip

