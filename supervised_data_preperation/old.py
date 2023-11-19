
### find missing and corrupt audio files in dataset ###

timing_dir = "D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts"
disfluencies_dir = "D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd" 
audio_dir = "D:\\Robin_dataset\\Switchboard\\LDC97S62 Switchboard-1 Release 2"

disfluencies_files = [f.stem for f in utils.get_directory_files(disfluencies_dir, 'mgd')]
timing_files = [f.stem[:7] for f in utils.get_directory_files(timing_dir, 'text') if f.stem.endswith('word')]
audio_files_A = [f.stem[:2] + f.stem[3:7] for f in utils.get_directory_files(audio_dir, 'wav') if f.stem.endswith('A') ]
audio_files_B = [f.stem[:2] + f.stem[3:7] for f in utils.get_directory_files(audio_dir, 'wav') if f.stem.endswith('B') ]
audio_files = [f for f in utils.get_directory_files(audio_dir, 'wav') if f.stem.endswith('B') or f.stem.endswith('A') ]

corrupt_files = []
for f in ChargingBar("Read Audio").iter(audio_files)  :
    try :
        utils.read_audio(f, 8000)
    except Exception :
        corrupt_files.append(f.stem[0:2] + f.stem[3:7])

missing_files = []
for stem in disfluencies_files :
    if not (stem + "A") in timing_files :
        missing_files.append(stem)
    if not (stem + "B") in timing_files :
        missing_files.append(stem)
    if not stem in audio_files_A :
        missing_files.append(stem)
    if not stem in audio_files_B :
        missing_files.append(stem)

print("missing:", missing_files)
print("corrupt:", corrupt_files)
print("ignore: ", [f[2:] for f in list(set(missing_files + corrupt_files))] )



