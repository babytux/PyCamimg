#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2008, 2009, 2010 Hugo Párraga Martín

This file is part of PyCamimg.

PyCamimg is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyCamimg is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCamimg.  If not, see <http://www.gnu.org/licenses/>.

"""
import sys

from ez_setup import use_setuptools
use_setuptools()

from distutils.core import setup, Distribution, Command
# from distutils.core import setup, find_packages
import glob
import os
import os.path as path
import sys
import pkg_resources
import ConfigParser

try:
    import py2exe
    buildExe = py2exe.build_exe.py2exe
    Distribution = py2exe.Distribution
except:
    py2exe = None
    buildExe = Command
    
try:
    import py2app
except ImportError:
    py2app = None
    

iconsTheme = "gnome"
gtkTheme = "Industrial"
    
try:
   # if this doesn't work, try import modulefinder
  import py2exe.mf as modulefinder
  import win32com
  for p in win32com.__path__[1:]:
      modulefinder.AddPackagePath("win32com", p)
  for extra in ["win32com.shell"]:  # ,"win32com.mapi"
      __import__(extra)
      m = sys.modules[extra]
      for p in m.__path__[1:]:
          modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    print("Error")
    pass


updateConfigAtEnd = False
exePath, setupFile = path.split(__file__)

versionFile = path.join(exePath, "src", "share", "pycamimg", "config", "version.cfg")
languagesFile = path.join(exePath, "src", "share", "pycamimg", "locale", "availables.cfg")

version = ConfigParser.ConfigParser()
failLoad = False
try: 
    # Try to read the version file
    version.read([versionFile])
except:
    failLoad = True
    
if (failLoad):
    raise Exception("Can't not open version file: %s" % versionFile)

languages = ConfigParser.ConfigParser()
listLanguages = []
failLanguages = False
try:
    languages.read([languagesFile])
    listLanguages = languages.sections()
except:
    failLanguages = True

__description__ = version.get("pycamimg", "short_description")
__name__ = version.get("pycamimg", "name_program")
__version__ = version.get("pycamimg", "version")
__author__ = version.get("pycamimg", "authors")
__email__ = version.get("pycamimg", "email")
__license__ = version.get("pycamimg", "alt_license")
__url__ = version.get("pycamimg", "website")
__copyright__ = version.get("pycamimg", "copyright")
__filename__ = version.get("pycamimg", "filename")
__exefilename__ = version.get("pycamimg", "exefilename")

__dependencies__ = ["gtk",
                    "gtk.glade",
                    "pygtk",
                    "gobject",
                    "PIL",
                    "PIL.ImageOps",
                    "jpeg",
                    "gettext",
                    "pkg_resources",
                    "pango",
                    "gdata",
                    "elementtree"]

if (sys.platform == "win32"):
    __dependencies__.append("ctypes")
    __dependencies__.append("win32api")
    __dependencies__.append("win32com")
    __dependencies__.append("win32con")
    __dependencies__.append("win32com.shell")
    # __dependencies__.append("win32com.shellcon")

__package_data__ = {
    }

__data_files__ = [
    (path.join("share", "pycamimg"), [
               path.join("src", "share", "pycamimg", "COPYING")
            ]),
    (path.join("share", "pycamimg", "config"), [
            path.join("src", "share", "pycamimg", "config", "config.cfg"),
            path.join("src", "share", "pycamimg", "config", "version.cfg")
            ]),
    (path.join("share", "pycamimg", "locale"), [
            path.join("src", "share", "pycamimg", "locale", "pycamimg.pot"),
            path.join("src", "share", "pycamimg", "locale", "files_gettext.list"),
            path.join("src", "share", "pycamimg", "locale", "availables.cfg"),
            path.join("src", "share", "pycamimg", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "locale", "es.po"),
            path.join("src", "share", "pycamimg", "locale", "pycamimg.pot")
            ]),
    (path.join("share", "pycamimg", "locale", "en", "LC_MESSAGES"), [
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "FacebookPlugin.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "LocalProjectPlugin.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "pycamimg.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "RenameOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "ResizeOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "RotateOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "GrayScaleOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "SepiaToneOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "en", "LC_MESSAGES", "FlipOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "fbcore.mo")                             
            ]),
    (path.join("share", "pycamimg", "locale", "es", "LC_MESSAGES"), [
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "FacebookPlugin.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "LocalProjectPlugin.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "pycamimg.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "RenameOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "ResizeOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "RotateOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "GrayScaleOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "SepiaToneOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "FlipOperation.mo"),
            path.join("src", "share", "pycamimg", "locale", "es", "LC_MESSAGES", "fbcore.mo")
            ]),
    (path.join("share", "pycamimg", "icons"), [
            path.join("src", "share", "pycamimg", "icons", "pycamimg.bmp"),
            path.join("src", "share", "pycamimg", "icons", "pycamimg.png"),
            path.join("src", "share", "pycamimg", "icons", "pycamimg.ico"),
            path.join("src", "share", "pycamimg", "icons", "facebook.png"),
            path.join("src", "share", "pycamimg", "icons", "pycamimg.png"),
            path.join("src", "share", "pycamimg", "icons", "loading.gif"),
            path.join("src", "share", "pycamimg", "icons", "rename.gif"),
            path.join("src", "share", "pycamimg", "icons", "resize.png"),
            path.join("src", "share", "pycamimg", "icons", "rotate.png"),
            path.join("src", "share", "pycamimg", "icons", "rotateLeft.gif"),
            path.join("src", "share", "pycamimg", "icons", "rotateRight.gif"),
            path.join("src", "share", "pycamimg", "icons", "lock.png"),
            path.join("src", "share", "pycamimg", "icons", "grayscale.png"),
            path.join("src", "share", "pycamimg", "icons", "sepiatone.png"),
            path.join("src", "share", "pycamimg", "icons", "mirror.png"),
            path.join("src", "share", "pycamimg", "icons", "flip.png"),
            path.join("src", "share", "pycamimg", "icons", "fb-connect.png")
            ]),
    (path.join("share", "pycamimg", "plugins"), [
            path.join("src", "share", "pycamimg", "plugins", "__init__.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "localproject"), [
            path.join("src", "share", "pycamimg", "plugins", "localproject", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "localproject", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "localproject", "LocalProject.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "localproject", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "localproject", "locale", "LocalProjectPlugin.pot"),
            path.join("src", "share", "pycamimg", "plugins", "localproject", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "localproject", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "facebookproject"), [
            path.join("src", "share", "pycamimg", "plugins", "facebookproject", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "facebookproject", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "facebookproject", "FacebookProj.py"),
            path.join("src", "share", "pycamimg", "plugins", "facebookproject", "AlbumSelection.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "facebookproject", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "facebookproject", "locale", "FacebookPlugin.pot"),
            path.join("src", "share", "pycamimg", "plugins", "facebookproject", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "facebookproject", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "fbcore"), [
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "AuthDialog.py"),
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "SessionFB.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "fbcore", "lib"), [
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "lib", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "lib", "facelib.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "fbcore", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "locale", "fbcore.pot"),
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "fbcore", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "RenameOperation"), [
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "Operation.py"),
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "RenameDialog.py"),
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "RenamePlugin.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "RenameOperation", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "locale", "RenameOperation.pot"),
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "RenameOperation", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "ResizeOperation"), [
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "Operation.py"),
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "ResizeDialog.py"),
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "ResizePlugin.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "ResizeOperation", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "locale", "ResizeOperation.pot"),
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "ResizeOperation", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "RotateOperation"), [
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "Operation.py"),
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "RotateDialog.py"),
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "RotatePlugin.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "RotateOperation", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "locale", "RotateOperation.pot"),
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "RotateOperation", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "GrayScaleOperation"), [
            path.join("src", "share", "pycamimg", "plugins", "GrayScaleOperation", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "GrayScaleOperation", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "GrayScaleOperation", "Operation.py"),
            path.join("src", "share", "pycamimg", "plugins", "GrayScaleOperation", "GrayScalePlugin.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "GrayScaleOperation", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "GrayScaleOperation", "locale", "GrayScaleOperation.pot"),
            path.join("src", "share", "pycamimg", "plugins", "GrayScaleOperation", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "GrayScaleOperation", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "SepiaToneOperation"), [
            path.join("src", "share", "pycamimg", "plugins", "SepiaToneOperation", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "SepiaToneOperation", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "SepiaToneOperation", "Operation.py"),
            path.join("src", "share", "pycamimg", "plugins", "SepiaToneOperation", "SepiaTonePlugin.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "SepiaToneOperation", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "SepiaToneOperation", "locale", "SepiaToneOperation.pot"),
            path.join("src", "share", "pycamimg", "plugins", "SepiaToneOperation", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "SepiaToneOperation", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "FlipOperation"), [
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "Operation.py"),
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "FlipPlugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "FlipDialog.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "FlipOperation", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "locale", "FlipOperation.pot"),
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "FlipOperation", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "picasaproject"), [
            path.join("src", "share", "pycamimg", "plugins", "picasaproject", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "picasaproject", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "picasaproject", "PicasaProj.py"),
            path.join("src", "share", "pycamimg", "plugins", "picasaproject", "AlbumSelection.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "picasaproject", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "picasaproject", "locale", "PicasaPlugin.pot"),
            path.join("src", "share", "pycamimg", "plugins", "picasaproject", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "picasaproject", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "plugins", "gdatacore"), [
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "__init__.py"),
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "camimgplugin.py"),
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "AuthDialog.py"),
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "Session.py"),
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "LoginDialog.py")
            ]),
    (path.join("share", "pycamimg", "plugins", "gdatacore", "locale"), [
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "locale", "gdatacore.pot"),
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "locale", "en.po"),
            path.join("src", "share", "pycamimg", "plugins", "gdatacore", "locale", "es.po")
            ]),
    (path.join("share", "pycamimg", "scripts"), [
            path.join("src", "share", "pycamimg", "scripts", "db_scheme.sql"),
            ]),
    (path.join("share", "pycamimg", "xml"), [
            path.join("src", "share", "pycamimg", "xml", "MainMenu.xml"),
            path.join("src", "share", "pycamimg", "xml", "execute.xml"),
            path.join("src", "share", "pycamimg", "xml", "Explorer.xml"),
            path.join("src", "share", "pycamimg", "xml", "facebookproject.xml"),
            path.join("src", "share", "pycamimg", "xml", "flipoperation.xml"),
            path.join("src", "share", "pycamimg", "xml", "grayscaleoperation.xml"),
            path.join("src", "share", "pycamimg", "xml", "localproject.xml"),
            path.join("src", "share", "pycamimg", "xml", "renameoperation.xml"),
            path.join("src", "share", "pycamimg", "xml", "resizeoperation.xml"),
            path.join("src", "share", "pycamimg", "xml", "rotateoperation.xml"),
            path.join("src", "share", "pycamimg", "xml", "sepiatoneoperation.xml")
            ]),
    ]
__script__ = path.join("src", "camimg.py")


__packages__ = ["pycamimg",
               "pycamimg.core",
               "pycamimg.core.db",
               "pycamimg.core.operations",
               "pycamimg.core.photoalbum",
               "pycamimg.core.plugins",
               "pycamimg.ui",
               "pycamimg.util",
               ]


# Some of these depend on some files to be built externally before running
# setup.py, like the .xml and .desktop files
options = {}



def get_innosetup_compile():
    try:
        import _winreg
        compile_key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, "innosetupscriptfile\\shell\\compile\\command")
        compilecommand = _winreg.QueryValue(compile_key, "")
        compile_key.Close()

    except:
        compilecommand = "compil32.exe"
    return compilecommand


def chop(dist_dir, pathname):
    """returns the path relative to dist_dir"""
    assert pathname.startswith(dist_dir)
    return pathname[len(dist_dir):]


def create_inno_script(name, _lib_dir, dist_dir, exe_files, other_files, version="1.0"):
    if not dist_dir.endswith(os.sep):
        dist_dir += os.sep
    exe_files = [chop(dist_dir, p) for p in exe_files]
    other_files = [chop(dist_dir, p) for p in other_files]
    pathname = path.join(dist_dir, name + os.extsep + "iss")

# See http://www.jrsoftware.org/isfaq.php for more InnoSetup config options.
    ofi = open(pathname, "w")
    print >> ofi, r'''; WARNING: This script has been created by py2exe. Changes to this script
; will be overwritten the next time py2exe is run!

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Setup]
AppName=%(name)s
AppVerName=%(name)s %(version)s
AppPublisher=Hugo Párraga Martín
AppPublisherURL=http://babytuxexperience.blogspot.com
AppSupportURL=http://babytuxexperience.blogspot.com
AppUpdatesURL=http://babytuxexperience.blogspot.com
;AppComments=
AppCopyright=Copyright (C) 2008-2010 Hugo Párraga Martín
DefaultDirName={pf}\%(name)s
DefaultGroupName=%(name)s
LicenseFile=%(license)s
OutputDir=%(output)s
OutputBaseFilename=%(name)s-%(version)s-setup
ChangesAssociations=yes
SetupIconFile=%(icon_path)s
;WizardSmallImageFile=compiler:images\WizModernSmallImage13.bmp
WizardImageFile=%(wizard_image)s
Compression=lzma
SolidCompression=yes

[Files]''' % {
    'name': __name__,
    'version': __version__,
    'icon_path': path.join(path.abspath("src"), "share", "pycamimg", "icons", "pycamimg.ico"),
    'wizard_image': path.join(path.abspath("src"), "share", "pycamimg", "icons", "pycamimg.bmp"),
    'license': path.join(path.abspath("src"), "share", "pycamimg", "COPYING"),
    'output': path.abspath("dist")
}
    for fpath in exe_files + other_files:
        print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (fpath, os.path.dirname(fpath))
        
    print >> ofi, r'''
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Icons]
Name: "{group}\%(name)s"; Filename: "{app}\%(exefilename)s.exe";
Name: "{group}\Uninstall %(name)s"; Filename: "{uninstallexe}";
Name: "{commondesktop}\%(name)s"; Filename: "{app}\%(exefilename)s.exe"; Tasks: desktopicon''' % {'name': __name__, 'exefilename': __exefilename__}

    # Show a "Launch Virtaal" checkbox on the last installer screen
    print >> ofi, r'''
[Run]
Filename: "{app}\%(exefilename)s.exe"; Description: "{cm:LaunchProgram,%(name)s}"; Flags: nowait postinstall skipifsilent''' % {'name': __name__, 'exefilename': __exefilename__}
    print >> ofi
    ofi.close()
    return pathname


def compile_inno_script(script_path):
    """compiles the script using InnoSetup"""
    shell_compile_command = get_innosetup_compile()
    compile_command = shell_compile_command.replace('"%1"', script_path)
    result = os.system(compile_command)
    if result:
        print("Error compiling iss file")
        print("Opening iss file, use InnoSetup GUI to compile manually")
        os.startfile(script_path)
        
class BuildWin32Installer(buildExe):
    """distutils class that first builds the exe file(s), then creates a Windows installer using InnoSetup"""
    description = "create an executable installer for MS Windows using InnoSetup and py2exe"
    user_options = getattr(buildExe, 'user_options', []) + \
        [('install-script=', None,
          "basename of installation script to be run after installation or before deinstallation")]

    def initialize_options(self):
        buildExe.initialize_options(self)

    def run(self):
        # First, let py2exe do it's work.
        buildExe.run(self)
        # create the Installer, using the files py2exe has created.
        exe_files = self.windows_exe_files + self.console_exe_files
        print("*** creating the inno setup script***")
        script_path = create_inno_script(__name__, self.lib_dir, self.dist_dir, exe_files, self.lib_files,
                                         version=self.distribution.metadata.version)
        print("*** compiling the inno setup script***")
        compile_inno_script(script_path)
        # Note: By default the final setup.exe will be in an Output subdirectory.




def find_gtk_bin_directory():
    GTK_NAME = "libgtk"
    # Look for GTK in the user's Path as well as in some familiar locations
    paths = [r'C:\GTK\bin', r'C:\GTK\lib', r'C:\Program Files\GTK\bin' r'C:\Program Files\GTK2-Runtime'] + os.environ['Path'].split(';') 
    for p in paths:
        if not path.exists(p):
            continue
        files = [path.join(p, f) for f in os.listdir(p) if path.isfile(path.join(p, f)) and f.startswith(GTK_NAME)]
        if len(files) > 0:
            return p
    raise Exception("""Could not find the GTK runtime.
Please place bin directory of your GTK installation in the program path.""")

def find_gtk_files():
    def parent(dir_path):
        return path.abspath(path.join(path.abspath(dir_path), '..'))

    def strip_leading_path(leadingPath, p):
        return p[len(leadingPath) + 1:]

    data_files = []
    gtk_path = parent(find_gtk_bin_directory())
    for dir_path in [path.join(gtk_path, p) for p in ('etc', 'lib')]:
        for dir_name, _, files in os.walk(dir_path):
            files = [path.abspath(path.join(dir_name, f)) for f in files]
            if len(files) > 0:
                data_files.append((strip_leading_path(gtk_path, dir_name), files))
    
    validPathList = [
             path.join(gtk_path, 'share', 'aclocal'),
             path.join(gtk_path, 'share', 'icons', iconsTheme),
             path.join(gtk_path, 'share', 'themes', gtkTheme),
             path.join(gtk_path, 'share', 'xml')]
    if (not failLanguages):
        for l in listLanguages:
            validPathList.append(path.join(gtk_path, 'share', 'locale', l))         
    else:
        validPathList.append(path.join(gtk_path, 'share', 'locale'))
                     
    
    for dir_name, _, files in os.walk(path.join(gtk_path, 'share')):
        found = False
        for v in validPathList:
            if (dir_name.startswith(v)):
                found = True
                break  
        if (found):  
            files = [path.abspath(path.join(dir_name, f)) for f in files]
            if len(files) > 0:
                data_files.append((strip_leading_path(gtk_path, dir_name), files))
    files_bin = []
    for dir_name, _, files in os.walk(path.join(gtk_path, 'bin')):
        for file in files:
            if (file.endswith(".dll")):
                files_bin += [path.abspath(path.join(gtk_path, 'bin', file))]
        if (len(files_bin) > 0):
            data_files.append((strip_leading_path(gtk_path, path.join(gtk_path, 'bin')), files_bin))
    return data_files

def update_configuration(withReturn=False, withPath=False):
    def parent(dir_path):
        return path.abspath(path.join(path.abspath(dir_path), '..'))

    def strip_leading_path(leadingPath, p):
        return p[len(leadingPath) + 1:]
    
    updateConfigAtEnd = withPath
    xmlFiles = []
    xmlFolder = path.join("share", "pycamimg", "xml")
    dirXml = path.join ("src", xmlFolder)

    files = os.listdir(dirXml)
    for file in files:
        if (path.isfile(path.join(dirXml, file))):
            xmlFiles.append(path.abspath(path.join(dirXml, file)))
    
    configFile = path.join("src", "share", "pycamimg", "config", "config.cfg")
    config = ConfigParser.ConfigParser()
    configMade = True
    try: 
        # Try to read the config file
        config .read([configFile])
    except:
        configMade = False

    if ((configMade) and
        (len(config .sections()) <= 0)):
        configMade = False

    if (configMade):
        config.set("UI_CORE", "ui_files_as_resources", not withPath)
        if (withPath):
            config.set("UI_CORE", "xmlui_path", xmlFolder)
            config.set("LOG", "level", 30)
        else:
            config.set("UI_CORE", "xmlui_path", "")
            config.set("LOG", "level", 20)        
        
    try:
        f = open(configFile, "w")
        config.write(f)
    except:
        print("An error was ocurred when the configuration was saving")
    finally:
        # Checks the file status and closes it.
        if (f != None):
            f.close()
    if (withReturn):
        return [(xmlFolder, xmlFiles)]
    else:
        return None

def add_win32_options(options):
    """This function is responsible for finding data files and setting options necessary
    to build executables and installers under Windows.

    @return: A 2-tuple (data_files, options), where data_files is a list of Windows
             specific data files (this would include the GTK binaries) and where
             options are the options required by py2exe."""
    if ((py2exe != None) and 
        ('py2exe' in sys.argv or 
         'innosetup' in sys.argv or
         'py2exe_nogtk' in sys.argv or
         'innosetup_nogtk' in sys.argv)):
        if (not (('py2exe_nogtk' in sys.argv) or ('innosetup_nogtk' in sys.argv))):
            options['data_files'].extend(find_gtk_files())
        uiData = update_configuration(withReturn=True, withPath=True)
        if (uiData != None):
            options['data_files'].extend(uiData)
        

        py2exe_options = {
            "packages":   ["encodings", "pycamimg"],
            "compressed": True,
            "excludes":   ["PyLucene", "Tkconstants", "Tkinter", "tcl", "translate.misc._csv"],
            "dist_dir": path.join("dist", "win32"),
            "includes" : ["cairo", "pango", "pangocairo", "atk", "gobject", "jpeg", "PIL", "PIL.ImageOps"],
            "optimize":   2,
            # "bundle_files": 1, 
        }
        py2exe_options['includes'] += ["zipfile"]  # Dependencies for the migration and auto-correction plug-ins, respectively.
        innosetup_options = py2exe_options.copy()
        options.update({
            "windows": [
                {
                    'script': __script__,
                    'icon_resources' : [(1, path.join("src", "share", "pycamimg", "icons", "pycamimg.ico"))]
                }
            ],
            "zipfile":  "pycamimg.zip",
            "options": {
                "py2exe":    py2exe_options,
                "innosetup": innosetup_options
            },
            'cmdclass':  {
                "py2exe":    buildExe,
                "py2exe_nogtk": buildExe,
                "innosetup": BuildWin32Installer,
                "innosetup": BuildWin32Installer
            }
        })
    
    options['scripts'].append("postinstall_win.py")
        
    return options


def add_mac_options(options):
    # http://svn.pythonmac.org/py2app/py2app/trunk/doc/index.html#tweaking-your-info-plist
    # http://developer.apple.com/documentation/MacOSX/Conceptual/BPRuntimeConfig/Articles/PListKeys.html
    if py2app is None:
        return options
    from translate.storage import factory
    options.update({
        "app": [__script__],
        "options": {
            "py2app": {
                # "semi_standalone": True,
                "compressed": True,
                "argv_emulation": True,
                "plist":  {
                    "CFBundleGetInfoString": __description__,
                    "CFBundleGetInfoString": __name__,
                    "CFBundleIconFile": "%s.icns" % __filename__,
                    "CFBundleShortVersionString": __version__,
                    # "LSHasLocalizedDisplayName": "1",
                    # "LSMinimumSystemVersion": ???,
                    "NSHumanReadableCopyright": __copyright__,
                    "CFBundleDocumentTypes": [{
                        "CFBundleTypeExtensions": [extention.lstrip("*.") for extention in extentions],
                        "CFBundleTypeIconFile": "%s.icns" % __filename__,
                        "CFBundleTypeMIMETypes": mimetypes,
                        "CFBundleTypeName": description,  # ????
                        } for description, extentions, mimetypes in factory.supported_files()]
                    }
                }
            }})
    return options

def add_freedesktop_options(options):
    return options

def add_platform_specific_options(options):
    options = {
        "scripts": [__script__],
        "package_dir": {'':'src'},
        "packages": __packages__,
        "package_data": __package_data__,
        "install_requires": __dependencies__,
        "zip_safe": True,
        "data_files": __data_files__
    }
    options.update({
                    "bdist":{
                             "formats" : "wininst,bztar,zip,egg",
                             "dist_dir": path.join("dist", "binary")
                         },
                    "sdist":{
                             "formats": "zip,bztar,gztar",
                             "dist_dir": path.join("dist", "sources")
                         },
                    "install":{
                               "optimize" : 2,
                               "compile" : True
                        }
                    
                    }
                )
    
    if sys.platform == 'win32':
        return add_win32_options(options)
    if sys.platform == 'darwin':
        return add_mac_options(options)
    else:
        return add_freedesktop_options(options)


def doSetup(options):
    options = add_platform_specific_options(options)
    setup(name=__name__,
          version=__version__,
          description=__description__,
          author=__author__,
          author_email=__email__,
          maintainer=__author__,
          maintainer_email=__email__,
          url=__url__,
          license=__license__,
          platforms=["any"],
          **options)

# if __name__ == "__main__":
try:
    doSetup(options)
finally:
    if (updateConfigAtEnd):
        update_configuration()
