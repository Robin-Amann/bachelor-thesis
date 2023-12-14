import utils.file as utils
import utils.constants as c
import time
# for dir in [c.manual_dir, c.manual_seg_dir, c.automatic_dir, c.automatic_align_dir, c.retranscibed_dir, c.transcript_align_dir] :
#     print(len(utils.get_dir_files(dir)))

start = time.time()
files = utils.get_dir_tuples([
    (c.manual_seg_dir, lambda f : 'Speech' in f.stem), 
    c.automatic_dir, 
    c.automatic_align_dir, 
    c.transcript_align_dir])

#files = utils.get_dir_tuples_new([c.manual_seg_dir, c.automatic_dir, c.automatic_align_dir, c.transcript_align_dir], [lambda b, f: f.stem[2:7] in b.stem] * 3, lambda f : 'Speech' in f.stem)
end = time.time()
print(len(files))
files = [ (f1.stem, len(f2), len(f3), len(f4)) for f1, f2, f3, f4 in files ]
print(end - start)

for i in range(30) :
    print(files[i])