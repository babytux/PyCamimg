#! python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import pycamimg

DESKTOP_FOLDER = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
NAME = 'pycamimg.lnk'

if sys.argv[1] == '-install':
    create_shortcut(
        os.path.join(sys.prefix, 'pythonw.exe'),  # program
        'PyCamimig',  # description
        NAME,  # filename
        os.path.join(sys.prefix, 'scripts', 'camimg.py'),  # parameters
        '',  # workdir
        os.path.join(sys.prefix, 'share', 'pycamimg', 'icons', 'pycamimg.ico'),  # iconpath
    )
    # move shortcut from current directory to DESKTOP_FOLDER
    shutil.move(os.path.join(os.getcwd(), NAME),
                os.path.join(DESKTOP_FOLDER, NAME))
    # tell windows installer that we created another 
    # file which should be deleted on uninstallation
    file_created(os.path.join(DESKTOP_FOLDER, NAME))

if sys.argv[1] == '-remove':
    pass
    # This will be run on uninstallation. Nothing to do.
