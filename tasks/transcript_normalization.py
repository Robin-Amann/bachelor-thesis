from nemo_text_processing.text_normalization.normalize import Normalizer
import utils.file as utils
import utils.constants as c
import utils.transcript as word_utils
import utils.wer_alignment as alignment
from progress.bar import ChargingBar
import re

def normalize_file(file_path, normalizer = None, filename_extention = None) :
    if normalizer == None :
        normalizer = Normalizer(input_case='cased', lang='en')

    transcript = utils.read_file(file_path)
    transcript = normalizer.normalize(transcript, punct_post_process=True)
    write = utils.write_file

    if filename_extention != None:
        write(file_path[:-4] + "_" + filename_extention + ".txt", transcript)
    else :
        write(file_path, transcript)
    
    

def normalize_dir(directory_path, filename_extention = None) :
    files = [ f for f in utils.get_dir_files(directory_path, "txt") if not 'Speech' in f.stem ]
    normalizer = Normalizer(input_case='cased', lang='en')
    for file in ChargingBar("Normalize Transcript").iter(files) :
        normalize_file(str(file), normalizer, filename_extention)    


import re

def before_normalization(old_dir, new_dir) :
    files = utils.get_dir_files(old_dir, filter_condition=lambda f: True)
    j = 0
    for file in files :
        words = [ w['word'] for w in utils.read_dict(file) ]
        i = 0
        while i < len(words) - 1 :
            if re.search('[0-9]', words[i]) and re.search('[0-9]', words[i+1]) :
                if ('$' in words[i] and not '$' in words[i+1]) or words[i+1].startswith(',000') or words[i+1].startswith('.'):
                    x = words[i] + words[i+1]
                    print(x.ljust(15), end='')
                    j += 1
                    if j % 15 == 0 :
                        print()
                    words = words[:i] + [x] + words[i+2:]
                    continue
            i += 1
        new_file = utils.repath(file, old_dir, new_dir)
        utils.write_file(new_file, ' '.join(words))


# go through non-words missed by normalizer and correct them by hand
def after_normalization(old_dir, new_dir, radius = 2) :
    files = utils.get_dir_files(old_dir, filter_condition=lambda f: True)
    changed_files = set()
    incidents = 0
    for file in files :
        words = utils.read_file(file).split()
        incidents += len( [ word for word in words if not word_utils.simplify(word) ])
    print('number of words to be corrected:', incidents)
    
    print('continue? (y/n)', end=' ')
    if input() == 'y' :
        for file in files :
            words = utils.read_file(file).split()
            for i, word in enumerate(words) :
                if not word_utils.simplify(word) :
                    if i > 0 :
                        print(' '.join(words[max(0, i-radius):i]), end='')
                    print(' >', words[i], '< ', sep='', end='')
                    if i < len(words)-1 :
                        print(' '.join(words[i+1: i+1+radius]))
                    user_input = input()
                    if user_input == '>>end<<' :
                        break
                    if user_input :
                        words[i] = user_input
                        changed_files.add(file[2:10])
            else :
                new_file = utils.repath(file, old_dir, new_dir)
                utils.write_file(new_file, ' '.join(words))
                continue
            break
        changed_files = list(changed_files)
        changed_files.sort()
        print(changed_files)

def find_not_normalized_words(manual_dir, automatic_dir) :

    numbers = []
    currency = []
    percentages = []
    weird_i = []
    weird_i2 = []
    rest = []

    files = utils.get_dir_tuples([manual_dir, automatic_dir], lambda f: True)

    for manual_f, automatic_f in ChargingBar('files').iter(files) :
        automatic = utils.read_dict(automatic_f)
        manual = utils.read_dict(manual_f)
        manual, automatic, _ = alignment.align_words(manual, automatic, {'word' : '', 'is_restart' : False, 'pause_type'  : ''})
        for i, word in enumerate(automatic) : 
            if (manual[i]['pause_type'] or manual[i]['is_restart']) and bool( re.search('[^A-Za-zé\'.,:;!?-' + ']', word['word']) ) :
                if not bool( re.search('[^A-Za-zé\'.,:;!?' + '0-9-' + ']', word['word']) ) :
                    # print(word['word'].ljust(10), ' '.join( w['word'] for w in automatic[max(0, i-2) : i+2]))
                    numbers.append(word['word'])
                elif not bool( re.search('[^A-Za-zé\'.,:;!?' + '$€0-9-' + ']', word['word']) ) :
                    currency.append(word['word'])
                elif not bool( re.search('[^A-Za-zé\'.,:;!?' + '%0-9-' + ']', word['word']) ) :
                    percentages.append(word['word'])
                elif not bool( re.search('[^A-Za-zé\'.,:;!?' + 'ì-' + ']', word['word']) ) :
                    weird_i.append(word['word'])
                elif not bool( re.search('[^A-Za-zé\'.,:;!?' + 'í-' + ']', word['word']) ) :
                    weird_i2.append(word['word'])
                else :
                    rest.append(word['word'])

    for label, l in zip(['numbers', 'currency', 'percentages', 'weird_i', 'weird_i2', 'rest'], [numbers, currency, percentages, weird_i, weird_i2, rest]) :
        print(label + ':', len(l))
        print( sorted( list(set(l)) ) )

    # 5000 (0.5%)

    # numbers = {'50', '42', '1920.', '-12', '-30s', '41,', '82', '73,', ',000th', '1910', '32', '401K.', '85,', '3M,', '4.', '97', '11?', '386.', '60s?', "'8", '84', '19?', '16th', '1983,', '-0.', '-20s', '1979,', '1955,', '15th', 'K1.', '1x8', '-2', '80s', '79.', '128,', '-4', "'10", '286', '401k', '6,', '70', '25,', '27', '1984?', '19,', '5600', '103', '7', '16K', '72', '39,', '128.', '1945', '95,', '80s.', '1964,', '08,', '1959,', '57', '30.', '85', '537', '100,', '530,', '307', '162.', '1952', '.5', '1985.', '120,', '5th', '28.', '150K', '5,', '90210.', '07', '401k.', '26.', '1920,', '26', '2000', '29', '81.', '200,', '12th.', 'A18', '1969.', '687', '2?', '1200,', 'DMOS4?', 'V6', ',200,', '1927,', 'SE30', '190', '14', '486.', '83', '82,', '20s,', 'FX2', '600', '66,', '1986,', 'V6?', ',500', '-15.', '11th', '88', '1967,', '1900s,', '1913,', '91.', '51', ',001', '755', ',065,', '-22', '.357', '6s.', '70s,', 'PS1', '17,', '1972.', '630', '8088', '85.', '1957.', '48K', '38.', '86.', '20s', '55', '1130', '30s.', '23.', '22.', '-7.', '89.', '45,', '60s.', '62', '386,', '86', '12', '16.', '98,', '1987', 'PS2', '13th', '87', '98.', '90,', '2000,', '1913.', '1950s', '2010', '-800', '1988,', '1982', '48,', '50s.', '-600', '49th', '63,', '70,', ',300', '50s', '4?', '98', '1130.', '.12', '1981,', '400', '8.', '6000.', '.30,', '13.', '1970', '5', '49ers', '730', '45', '1960,', '21', '-95', '-1800s,', '.30', '250.', '86?', '-30', '30s?', '30s', '90', '40s', '500.', '99', '1865', '1989,', '70s.', '25th', '69,', '110.', '.97', '1983', '1951,', '-85', '75th', '103.', '13,', '.22.', '318', '1903.', '328', '200', '18', 'V8s.', '300.', '89,', '7,', '100', '10,', '8?', '2450', '76,', '-70.', '2001', '37', '570', '930.', '6000,', '25.', '79,', ',300,', '87.', '-1,', ',600', '.10', '280Z', '115.', '747', '58', '14,', '4th', '1988.', '72,', '9', '1840s.', '4x4', '89', '16,', '50,', '-47s,', '1923', '30?', '63', '3.', '930,', '1995', '2010,', '1985,', '1983.', '41', '3100', '100s?', '101,', '.75,', '1', 'MX3,', '1940s,', '39', '90210', '635.', '1948.', '1967.', '211', '7.', '1700s', '46th', '.287', 'LS400.', '31.', '1900?', '18,', '.30.', '48.', '67', '1200', '1984.', '.1.', '13', '15,', '.2', '289', '48K,', '30,', '102', '62,', '130.', '315.', '1045', '1963,', '1927', '1957,', '10Ks', '74', 'OS2.', 'SP1000,', '19th,', '650,', '0', '95', '15', '287', '386', '1993', '1930s', '128K.', '97.', '76', '-20', '69.', '79', '.6', '1987,', '.1', '14.', '53', ',900', '1975', '74,', '1990s', '68', '1992', '730.', '3D', '1980s.', '109.', '2020,', '-40s,', '9.', '650.', '1978.', '4K', ',500.', '100s,', '530', 'PS1,', ',000,', '45th', '17th', '280', '8,', '1950,', '6.', '26th', '87,', ',200', '.410', '-7,', '6mm', ',800', '.50', 'VH1?', '38', '1978', '2020', '11', '10th', '65,', '4s', '52.', '725.', '26,', '36,', '10?', '.25', '1940s', '125', '1960.', '286.', '20', '50s,', '-7', '78s', '240', '-6.', '486', '11,', '-17', '27.', '-35?', '10th,', '1903,', '43', '1920s', '1030', '-5,', '-1800s', '.15', '94', '80.', '23,', '75.', '33?', '60', '4th,', '.15.', '1970.', '24,', '60s', '21st.', '240SX.', 'CN1', '635', '15.', '350', '101.', '.22', '5Ks', '71,', '42,', '-60s,', '67.', '1960', '3', '1990,', '320A', '18?', '-4,', '80s,', '92', '365', '49,', ',500,', '1.', '81,', '32.', '40,', '35,', '106', '1991,', '1800', '25', '27,', '19', '10.', '40', '83,', '80,', '.98', '18th', '48?', '.29', '1190.', '302', '59.', '2', '250', '52,', '38625C', '93', '23', '10', '2020.', '-2,', '64', '75,', '-5', '1951', '007.', '51,', '1984', '76.', '18...', 'TR6', '60.', '10th.', '33.', '78.', '.99', '900', '16?', '78,', ',100', '65', '68.', '-10s,', '56', '-50s,', '-25', '1975,', '1912,', '454', '1949', '1987.', "mid-'60s,", 'V8s,', 'TI2.', 'A1', '12.', ',400', '9,', '.7', '16', '-1.', '200.', '1969,', '150.', '-3', '1st', '1977', '8', '2,', '46.', "mid-'70s,", '153', '20th', '1?', '-35', '360', '-300', '29K.', '90s.', '83T', '160', '150,', ',000.', '-11', '122', 'K9?', '-8ths', '49', '77,', '-1', '640,', '101', '-20,', 'V8s', '19...', '37.', '122,', '.75.', '90.', '74.', ',700', '55.', '1800s.', '30', '287.', '77', '102,', '88.', '.50.', '52', '305', '88s', '12s', '-80,', '37,', '33', '1700', '33,', '69', '-8,', '9th', '19.', '8086.', '20s.', ',000?', 'V6.', '-22s.', '50.', '54,', '99th', '30s,', '48', '.432', '1927.', '45.', '-3,', '20.', '1905,', '28,', '401K,', '24?', '66.', '464', '29,', '1990.', '1922.', '130', '440', '60s,', '189', '21.', '40.', '73.', '78', '66', '1972,', '110', '47', '90s,', '96', '1982,', '401', '92s.', '35', '.54', '92,', '120', '3000', '20th.', '-10', '235', '1980.', '105', '18.', '980', '24', 'SC300', '265,', '42.', '92s', '220.', '21,', '83.', '300', '4Runners,', '25?', 'V8', '73', '60,', '40s,', '29th,', '170', 'SE30.', "8's", '90s', '15th,', '.8', ',400.', '.6.', '40s.', '300,', '20,', '1980', '31', '2000.', '160.', '11.', '70.', '4Runner.', '60...', 'V8.', '180', '92.', '10x10', '64K.', '12,', '1993,', '2E', '36', '800', '9x12', '91', '1930s,', '635?', '1960s', '-60', '750', '25th,', '.99.', '84?', '-99,', 'NX2000,', '65.', '46', '84,', '95.', '1890', '6', '1960s.', '81', '.7,', '100.', '5.', '1900.', '500', '70s', '340', '-7s', '104', '17.', '.0', "V6's,", '-80', '28', '84.', '283s', '1919.', '.0.', '3,', '.5,', '102.', '17', '2001.', '34', '1973.', '29.', '.38', '54', '1,', '92s,', '.97,', ',000', '22', '4', 'PS2.', '35.', '570,', '26th.', '19th', '.75', '22,', '150', '250?', '-48s', '-20.', '1970s,', '75', '.5.', '1976,', '2.', '32,', ',200.', '24.', '1968.', '70?', '80', '560SL', '82.', '.7.', '55,', '1980,', '88,', '401K'}
    # currency = {'$150.', '$450', '$17', '$19', '$3.', '$80.', '$900', '$10?', '$35.', '$130', '$300', '$34.', '$6.', '$600', '$18', '$70', '$200', '$1', '$250', '$325.', '$315', '$7,', '$75.', '$8.', '$720.', '$86', '$100', '$200.', '$500,', '$25', '$58', '$55.', '$13', '$80', '$16,', '$7', '$300.', '$9.', '$50,', '$610', '$40', '$60,', '$26', '$35', '$3,', '$600,', '$100.', '$78', '$125', '$700.', '$80,', '$8', '$18,', '$11', '$3', '$300,', '$5,', '$50.', '$85', '$25.', '$650', '$275', '$4', '$64', '$0', '$60', '$30', '$50', '$2', '$161', '$22', '$400', '$20.', '$329.', '$6,', '$45.', '$20,', '$9', '$65', '$4.', '$55?', '$35,', '$92', '$12', '$25,', '$7.', '$34,', '$88', '$70,', '$175', '$10', '$40.', '$600.', '$2,', '$21.', '$800,', '$500', '$250.', '$32', '$40?', '$63', '$60.', '$16', '$700?', '$220.', '$140', '$5.', '$6', '$300?', '$110,', '$79', '$120', '$12.', '$170', '$40,', '$70.', '$220', '$18.', '$400,', '$750', '$200,', '$10,', '$14', '$120.', '$20', '$350', '$500.', '$15.', '$36', '$700', '$134.', '$2.', '$10.', '$299,', '$1,', '$550', '$55', '$96.', '$850', '$150', '$75', '$15,', '$100,', '$400.', '$4,', '$5', '$30.', '$63.', '$800', '$180', '$15', '$45', '$340', '$11,'}
    # percentages = {'44%.', '75%.', '70%,', '.5%,', '8%,', '33%,', '19%,', '10%,', '.25%,', '.5%.', '5%.', '4%,', '10%.', '25%.', '48%.', '11%.', '20%.', '13%,', '1%,', '18%,', '22%.', '50%,', '100%.', '2%.', '8%.', '80%.', '%', '33%.', '20%,', '4%.', '6%,', '6%.', '%?', '12%,', '50%.', '85%.', '18%.', '13%.', '5%,', '42%.'}
    # weird_i = {'ìIf', 'ìPlease', 'ìI', 'ìWhoa,', 'ìMake', 'ìNow,'}
    # weird_i2 = {'weíve', 'Así', 'wonít', 'thereís', 'itís', 'Iím', 'Whatís', 'heís', 'Donít', 'Iíll', 'youíre', 'didnít'}
    # rest = {'&T,', '&R', '&Ls', '\'4",', '&M.', '\'1".', '&T', '\'11",', '&M', '-1⁄2', 'C++', '&M,', '1⁄4,', '&L', "&M's", '&O', '1⁄2.', '&', '1⁄2', '\'3".', '&J', '8."'}

    # amount of gaps
    # 0.1 253668
    # 0.2 170750
    # 0.3 139585
    # 0.4 116261
    # 0.5 96722
    # 0.6 80282
    # 0.7 66298
    # 0.8 54713
    # 0.9 45247
    # 1.0 37555