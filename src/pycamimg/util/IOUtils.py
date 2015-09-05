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
import os.path
import pycamimg
import logging
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

import os, string
import os.path

if os.name == "nt":
    try:
        import win32api, win32con
    except ImportError, ie:
        __log__.fatal("It could not load win32api or win32con. Check if you have installed this modules. %s" % ie)
        raise ie
    isWin = 1
else:
    isWin = 0

    
class IOUtils:
    """
    @summary: Contains some common functions for IO operations.
    """
    def __init__(self):
        """
        @summary: Create new IOUtils.
        """
        self.__unicode__ = os.path.supports_unicode_filenames
        __log__.debug("Unicode enabled: %s" % self.__unicode__)

        if isWin:
            drives = win32api.GetLogicalDriveStrings()
            if (self.__unicode__):
                drives = unicode(drives)
            split = "\000"
            if (self.__unicode__):
                split = u"\x00"
            self.__drives__ = drives.split(split)
        else:
            root = None
            if (self.__unicode__):
                root = u"/"
            else:
                root = "/"
            self.__drives__ = [root, ]

        if self.__drives__ == None:
            self.__drives__ = []

    def __getListDirectory__(self, path):
        """
        @summary: Gets a list of a path.
        @param path: Path where list its directories.
        @return: Gets list with directories that are in path.
        @raise IOError: raise when path does not exist.   
        """
        if os.path.exists(path):
            ldir = os.listdir(path)
        else:
            __log__.error("%s does not exist." % path)
            raise IOError("%s does not exist." % path)
        return ldir

    def __isHidden__(self, path):
        """
        @summary: Check if path is hidden or not.
        @param path: Path to check.
        @return: True if path is hidden. 
        """        
        if isWin:
            res = None
            if (os.path.isdir(path)):
                return False
            try:
                flags = win32api.GetFileAttributes(path)
            except Exception, ex:
                __log__.error("An error has occurred when it was trying to get its file attributes [%s]. %s" % (path, ex))
                flags = None
            if flags:
                res = flags & win32con.FILE_ATTRIBUTE_HIDDEN
            if res:
                return True
        else:
            head, filename = os.path.split(path)
            pattern = "."
            if (self.__unicode__):
                pattern = u"."
            if filename.startswith(pattern):
                return True
        return False

    def getExtension(self, filename):
        """
        @summary: Gets extension of a filename.
        @param filename: Path to extract its extension.
        @return: string with the extension.
        @raise TypeError: raise when filename is not str or unicode.
        """
        if (not isinstance(filename, str) and not isinstance(filename, unicode)):
            raise TypeError("filename must be str or unicode")
        
        root, ext = os.path.splitext(filename)
        return ext

    def getDrives(self):
        """
        @summary: Gets available drives in current system.
        @return: List with all drives.
        """
        return self.__drives__
    
    def getDirectories(self, path, showhidden=True, insensitive=True, getFullpath=False):
        """
        @summary: Gets directories from a path.
        @param path: Path to get its directory.
        @param showhidden: True to get its hidden directory too. Default True
        @param insensitive: True to sort list insensitive.
        @param getFullPath: True to get a list with fullpath.
        @return: List with the directory.    
        @raise TypeError: raise when path is not str or unicode.
        @raise TypeError: raise when showhidden is not boolean.
        @raise TypeError: raise when insensitive is not boolean.
        """
        if (not isinstance(path, str) and not isinstance(path, unicode)):
            raise TypeError("path must be str or unicode")
        if (not isinstance(showhidden, bool)):
            raise TypeError("showhidden must be bool")
        if (not isinstance(insensitive, bool)):
            raise TypeError("insensitive must be bool")
        
        result = []

        if (self.__unicode__):
            if (type(path) != unicode):
                path = unicode(path)

        try:
            ldir = self.__getListDirectory__(path)
        except Exception, ex:
            __log__.error("An error has occurred when it was trying to get its directories [%s]. %s" % (path, ex))
            ldir = None

        if ldir != None:
            for item in ldir:
                fullpath = os.path.join(path, item)
                if os.path.isdir(fullpath):
                    if (self.__isHidden__(fullpath)):
                        continue
                    if (getFullpath):
                        result.append(fullpath)
                    else:
                        result.append(item)
            if (insensitive):
                if (self.__unicode__):
                    result.sort(key=unicode.lower)
                else:
                    result.sort(key=str.lower)
            else:
                result.sort()
        
        return result

    def getFiles(self, path, showhidden=True, insensitive=True, getFullpath=False):
        """
        @summary: Gets files from a path.
        @param path: Path to get its files.
        @param showhidden: True to get its hidden files too. Default True
        @param insensitive: True to sort list insensitive.
        @param getFullPath: True to get a list with fullpath.
        @return: List with the files.
        @raise TypeError: raise when path is not str or unicode.
        @raise TypeError: raise when showhidden is not boolean.
        @raise TypeError: raise when insensitive is not boolean.   
        """
        if (not isinstance(path, str) and not isinstance(path, unicode)):
            raise TypeError("path must be str or unicode")
        if (not isinstance(showhidden, bool)):
            raise TypeError("showhidden must be bool")
        if (not isinstance(insensitive, bool)):
            raise TypeError("insensitive must be bool")
        
        if (self.__unicode__):
            if (type(path) != unicode):
                path = unicode(path)
        
        result = []

        try:
            ldir = self.__getListDirectory__(path)
        except Exception, ex:
            __log__.error("An error has occurred when it was trying to get its files [%s]. %s" % (path, ex))
            ldir = None

        if ldir != None:
            for item in ldir:
                fullpath = os.path.join(path, item)
                if os.path.isfile(fullpath):
                    if (self.__isHidden__(fullpath)):
                        continue
                    if (getFullpath):
                        result.append(fullpath)
                    else:
                        result.append(item)
            if (insensitive):
                if (self.__unicode__):
                    result.sort(key=unicode.lower)
                else:
                    result.sort(key=str.lower)
            else:
                result.sort()

        return result
