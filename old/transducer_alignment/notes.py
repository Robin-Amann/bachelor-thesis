import nemo.collections.asr as nemo_asr
import nemo.collections.nlp as nemo_nlp
import nemo.collections.tts as nemo_tts

asr_models = [model for model in dir(nemo_asr.models) if model.endswith("Model")]
nlp_models = [model for model in dir(nemo_nlp.models) if model.endswith("Model")]
tts_models = [model for model in dir(nemo_tts.models) if model.endswith("Model")]

# ASR
#  'ASRModel',
#  'AudioToAudioModel',
#  'EncDecCTCModel',
#  'EncDecClassificationModel',
#  'EncDecDiarLabelModel',
#  'EncDecFrameClassificationModel',
#  'EncDecHybridRNNTCTCBPEModel',
#  'EncDecHybridRNNTCTCModel',
#  'EncDecK2RnntSeqModel',
#  'EncDecK2SeqModel',
#  'EncDecRNNTBPEModel',
#  'EncDecRNNTModel',
#  'EncDecSpeakerLabelModel',
#  'EncMaskDecAudioToAudioModel',
#  'SLUIntentSlotBPEModel',
#  'SpeechEncDecSelfSupervisedModel'

# NLP
#  'BERTLMModel',
#  'BertDPRModel',
#  'BertJointIRModel',
#  'DuplexDecoderModel',
#  'DuplexTaggerModel',
#  'DuplexTextNormalizationModel',
#  'EntityLinkingModel',
#  'GLUEModel',
#  'IntentSlotClassificationModel',
#  'MTEncDecModel',
#  'MegatronGPTPromptLearningModel',
#  'MultiLabelIntentSlotClassificationModel',
#  'PunctuationCapitalizationLexicalAudioModel',
#  'PunctuationCapitalizationModel',
#  'QAModel',
#  'SpellcheckingAsrCustomizationModel',
#  'Text2SparqlModel',
#  'TextClassificationModel',
#  'ThutmoseTaggerModel',
#  'TokenClassificationModel',
#  'TransformerLMModel',
#  'ZeroShotIntentModel'

# TTS
#  'AlignerModel',
#  'FastPitchModel',
#  'GriffinLimModel',
#  'HifiGanModel',
#  'MelPsuedoInverseModel',
#  'MixerTTSModel',
#  'RadTTSModel',
#  'SpectrogramEnhancerModel',
#  'Tacotron2Model',
#  'TwoStagesModel',
#  'UnivNetModel',
#  'VitsModel',
#  'WaveGlowModel'