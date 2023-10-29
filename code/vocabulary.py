import utils.constants as constants
import utils.file as utils
import tasks.vocabulary_extraction as vocabulary_extraction

# create vocabulary
fisher_english_patterns = ["# Transcribed at the LDC", "# Transcribed by BBN/WordWave", "# fe_[0-9]{2}_[0-9]{5}.sph", "A:", "B:", "\t", "[0-9]{1,3}.[0-9]{2}", "\(\(", "\)\)", '\.', ',', '!', '\?']
whisper_patterns = ['\.', ',', '!', '\?']

# vocabulary_extraction.get_vocabulary_set(
#     source_directory=constants.fe_transcripts, 
#     destination_directory=constants.vocabulary_manual_dir, 
#     patterns=fisher_english_patterns
# )
# vocabulary_extraction.get_vocabulary_set(
#     source_directory=constants.segmented_transcript_dir,
#     destination_directory=constants.vocabulary_manual_000_dir, 
#     patterns=fisher_english_patterns
# )
vocabulary_extraction.get_vocabulary_set(
    source_directory=constants.whisper_dir, 
    destination_directory=constants.vocabulary_whisper_000_dir, 
    patterns=whisper_patterns
)


# combine hesitations
# manual_hesitations = utils.read_vocabulary( constants.vocabulary_manual_dir + '\\hesitations.txt')
# whisper_hesitations = utils.read_vocabulary(constants.vocabulary_whisper_000_dir + '\\hesitations.txt')
# hesitations = manual_hesitations.copy()
# for w, c in whisper_hesitations.items() :
#     if hesitations.get(w) == None :
#         hesitations[w] = c
#     else :
#         hesitations[w] += c
# utils.write_vocabulary(constants.hesitations, hesitations)


## by hand : filter hesitations
