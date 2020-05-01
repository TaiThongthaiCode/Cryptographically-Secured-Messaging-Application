import shutil
import os
import errno

def delete(src):
    """
    Deletes a specific file in a directory
    @Param: src - the path of the file to be deleted, string-format
    """
    try:
        os.remove(src)
    except OSError as e:
        print("Error: %s : %s" % (src, e.strerror))

def deletedir(src):
    """
    Deletes a specific directory
    @Param: src - the path of the directory to be deleted, string-format
    """
    try:
        os.rmdir(src)
    except OSError as e:
        print("Error: %s : %s" % (src, e.strerror))

def copy(src, dest):
    """
    Copies all contents from one directory to another directory
    @Param: src - the path of the source directory, string-format
    @Param: dest - the path of the destination directory, string-format
    """
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

def createFolder(directory):
    """
    Creates a new directory
    @Param: directory - the NAME of the new directory, string-format
    """
    # ---------- TODO: Change the parent directory to your specific directory -----------------
    parent_dir = "C:/Users/rchen/Documents/AIT Crypto/finalproject/CryptoProject-master/netsim/"
    path = os.path.join(parent_dir, directory)
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
