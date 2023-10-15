# install nemo:
# pip install setuptools --upgrade
# pip install wget
# pip install text-unidecode
# pip install git+https://github.com/NVIDIA/NeMo.git
# pip install torchaudio>=0.10.0 -f https://download.pytorch.org/whl/torch_stable.html

import nemo.collections.asr as nemo_asr


# https://huggingface.co/nvidia/stt_en_conformer_transducer_xlarge
asr_model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained("nvidia/stt_en_conformer_transducer_xlarge")

