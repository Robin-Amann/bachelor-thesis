text = "PS C:UsersrobinDesktopBachelorarbeitbachelor-thesis> & C:/Users/robin/AppData/Local/Programs/Python/Python311/python.exe c:/Users/robin/Desktop/Bachelorarbeit/bachelor-thesis/ctc_alignment/tests.py"
chars = set(text)
unwanted = set("/,.")
print(chars - unwanted)