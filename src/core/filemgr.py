# TODO Update this openFile method to be aware of .p3d files, and make all file openings use it
def openFile(filename, args):
    return open("Galaxis_savedata/"+filename, args)