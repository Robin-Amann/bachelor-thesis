import utils.file as utils
import itertools
manual_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Transcripts_Segmented"
automatic_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Whisper_Segmented"
alignment_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Transcript_Alignment"


def get_dir_tuples(dir_list, type_list, conditions, merge_condition) :
    all_files = []
    for d, t, c in zip(dir_list, type_list, conditions) :
        files = utils.get_directory_files(d, t)
        files = [(f.stem, f) for f in files if c(f.stem)]
        all_files.append(files)
    tuples = []
    for f in all_files[0] :
        suitable = []
        for files in all_files[1 : ] :
            suitable.append([x for x in files if merge_condition(f[0], x[0])])
        if all(len(x) > 0 for x in suitable) :
            tuples.append((f, *suitable))
    return tuples

files = get_dir_tuples([manual_dir, automatic_dir, alignment_dir], ['txt', 'txt', 'txt'], [lambda s : not 'Speech' in s, lambda s : True, lambda s : True], lambda s0, sn : s0 == sn)
files = [(stub, str(file), str(f1[0][1]), str(f2[0][1])) for (stub, file), f1, f2 in files]
for stub, f1, f2, f3 in files :
    print(stub)
