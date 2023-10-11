import torch
import torchaudio

def get_trellis(emission, tokens, blank_id=0):
    num_frame = emission.size(0)
    num_tokens = len(tokens)

    # Trellis has extra diemsions for both time axis and tokens.
    # The extra dim for tokens represents <SoS> (start-of-sentence)
    # The extra dim for time axis is for simplification of the code.
    trellis = torch.empty((num_frame + 1, num_tokens + 1))
    trellis[0, 0] = 0
    trellis[1:, 0] = emission[:, 0]                                             # ignore starting audio
    trellis[0, -num_tokens:] = -float("inf")
    trellis[-num_tokens:, 0] = float("inf")

    for t in range(num_frame):
        trellis[t + 1, 1:] = torch.maximum(
            # Score for staying at the same token
            trellis[t, 1:] + emission[t, blank_id],
            # Score for changing to the next token
            trellis[t, :-1] + emission[t, tokens],
        )
    return trellis

def get_emission(SPEECH_FILE, device) :
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H                
    model = bundle.get_model().to(device)
    labels = bundle.get_labels()                                        
    with torch.inference_mode():
        waveform, _ = torchaudio.load(SPEECH_FILE)                      
        waveform = torchaudio.functional.resample(
            orig_freq=torchaudio.info(SPEECH_FILE).sample_rate, 
            new_freq=bundle.sample_rate, 
            waveform=waveform)
        emissions, _ = model(waveform.to(device))                       
        emissions = torch.log_softmax(emissions, dim=-1)                

    emission = emissions[0].cpu().detach()
    return labels, emission