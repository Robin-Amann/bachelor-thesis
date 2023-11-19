import utils.file as utils
import utils.constants as c

files = [f for f in utils.get_directory_files(c.manual_seg_dir, 'txt') if not 'Speech' in f.stem]

for f in files :
    words = utils.read_label_timings_from_file(f)
    if words[-1]['end'] > 50 :
        print(f)
        break
