
import tasks.preprocessing.preprocessing as pre
import utils.constants as c

# annotated_file= "D:\\Robin_dataset\\Switchboard\\Example\\Disfluencies\\treebank_3\\dysfl\\mgd\\swbd\\2\\sw2005.mgd"
# word_timing_file_A = "D:\\Robin_dataset\\Switchboard\\Example\\Timings\\word_alignments\\20\\2005\\sw2005A-ms98-a-word.text"
# word_timing_file_B = "D:\\Robin_dataset\\Switchboard\\Example\\Timings\\word_alignments\\20\\2005\\sw2005B-ms98-a-word.text"

# a, b = pre.process_file(annotated_file, word_timing_file_A, word_timing_file_B, ann_patterns=c.manual_annotation_patterns)

# i = 0
# for x in a:
#     if i == 20 : 
#         break
#     print('is_restart', x['is_restart'], 'pause_type', x['pause_type'], 'word', x['word'])
#     i+=1

# annotation_dir= "D:\\Robin_dataset\\Switchboard\\Example\\Disfluencies\\treebank_3\\dysfl\\mgd\\"
# timing_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Timings\\"
# desination_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Trans"
# pre.process_dir(annotation_dir, timing_dir, desination_dir, ann_patterns=c.manual_annotation_patterns )

# [(('sw2005', WindowsPath('D:/Robin_dataset/Switchboard/Example/Disfluencies/treebank_3/dysfl/mgd/swbd/2/sw2005.mgd')), 
# [('sw2005A-ms98-a-word', WindowsPath('D:/Robin_dataset/Switchboard/Example/Timings/word_alignments/20/2005/sw2005A-ms98-a-word.text')), 
# ('sw2005B-ms98-a-word', WindowsPath('D:/Robin_dataset/Switchboard/Example/Timings/word_alignments/20/2005/sw2005B-ms98-a-word.text'))]), 
# 
# (('sw2154', WindowsPath('D:/Robin_dataset/Switchboard/Example/Disfluencies/treebank_3/dysfl/mgd/swbd/2/sw2154.mgd')), 
# [('sw2154A-ms98-a-word', WindowsPath('D:/Robin_dataset/Switchboard/Example/Timings/word_alignments/21/2154/sw2154A-ms98-a-word.text')), 
# ('sw2154B-ms98-a-word', WindowsPath('D:/Robin_dataset/Switchboard/Example/Timings/word_alignments/21/2154/sw2154B-ms98-a-word.text'))])]


x = "okay<|>UH<|><|>False<|>0.0<|>0.48"
x = x.split('<|>')
print('<|>'.join(x))