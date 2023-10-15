import pathlib


def get_directory_files(directory, filetype) :
    # directory = 'D:\\Robin_dataset\\fisher english'
    files = [f for f in pathlib.Path(directory).glob("**\*." + filetype)]    
    return files

# files = get_directory_files('D:\\Robin_dataset\\fisher english', 'html')
# f = files[0]
#                                                   WindowsPath(D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html)                       
# str(f)        --> string representation  (\\)     D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1\index.html
# f.as_posix()  --> string representation  (/)      D:/Robin_dataset/fisher english/training speech 2/fe_03_p2_sph1/index.html
# f.parent      --> directory                       D:\Robin_dataset\fisher english\training speech 2\fe_03_p2_sph1
# f.name        --> filename (with extention)       index.html
# f.suffix      --> only suffix                     .html
# f.stem        --> file name                       index



# transcribe audio
# 1. get all filenaes
# for each file:
# - transcibe 