import utils.statistics as stats
import utils.constants as constants

manual_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Transcripts_Segmented"
automatic_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Whisper_Segmented"
alignment_dir = "D:\\Robin_dataset\\Switchboard\\Example\\Transcript_Alignment"

stats.sb_hesitation_translation(manual_dir, automatic_dir, alignment_dir)
