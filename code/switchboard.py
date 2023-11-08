import tasks.switchboard_transcript_preprocessing.preprocessing as pre

# annotated_file = "D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd\\2\\sw2012.mgd"
# word_timing_file_A = "D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts\\word alignments\\20\\2012\\sw2012A-ms98-a-word.text"
# word_timing_file_B = "D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts\\word alignments\\20\\2012\\sw2012B-ms98-a-word.text"

# a, b = pre.process_file(annotated_file, word_timing_file_A, word_timing_file_B, ann_patterns=['<+[^<>]*>+']) # <...>, <<...>>, <<<...>>>, ...


pre.process_dir(
    annotation_dir = "D:\\Robin_dataset\\Switchboard\\LDC99T42 Treebank 3\\treebank_3\\dysfl\\mgd\\swbd", 
    timing_dir = "D:\\Robin_dataset\\Switchboard\\Switchboard-1 Release 2 Transcripts", 
    desination_dir = "D:\\Robin_dataset\\Switchboard\\Example", 
    ann_patterns=['<+[^<>]*>+']
)


