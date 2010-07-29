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

try:
    import pygtk
    if (not (sys.platform == "win32")):
        pygtk.require('2.0')
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e

import time
from datetime import datetime
import urllib
import traceback

import FactoryControls

GNOME = True
WINDOWS = True
try:
    import gnomevfs
    WINDOWS = False
    GNOME = True
    __log__.debug("Gnome platform detected.")
except ImportError:
    __log__.debug("Windows platform detected.")
    GNOME = False
    WINDOWS = True 

try:
    import gtk
except ImportError, ie:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise ie

if (WINDOWS):
    try:
        import win32api
        from win32com.shell import shell, shellcon
        from win32con import FILE_ATTRIBUTE_NORMAL
        import ctypes
        from ctypes import CDLL
        from ctypes.util import find_library
        try:
            cgtk = CDLL("libgtk-win32-2.0-0.dll")
        except Exception, ex:
            __log__.fatal("Load libgtk-win32-2.0-0.dll failed. Loading by find_library. %s", ex)
            cgtk= CDLL(find_library("libgtk-win32-2.0-0.dll"))
        try:
            cgdk = CDLL("libgdk-win32-2.0-0.dll")
        except Exception, ex:
            __log__.fatal("Load libgdk-win32-2.0-0.dll failed. Loading by find_library. %s", ex)
            cgdk = CDLL(find_library("libgdk-win32-2.0-0.dll"))
        try:
            cgdkPixbuf = CDLL("libgdk_pixbuf-2.0-0.dll")
        except Exception, ex:
            __log__.fatal("Load libgdk_pixbuf-2.0-0.dll failed. Loading by find_library. %s", ex)
            cgdkPixbuf = CDLL(find_library("libgdk_pixbuf-2.0-0.dll"))
        
    except ImportError, ie:
        __log__.error("Import errors. %s" % ie)
        WINDOWS = False
        cgtk = None
        cgdk = None
        cgdkPixbuf = None
        
SUFFIXES = {1000: ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
            1024: ["Bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]}
        
class MimeInfo:
    """
    @summary: Manager to get info of a mime.
    """
   
    def __init__( self ):
        """
        @summary: Create a new MimeInfo.
        """
        self.icons = gtk.icon_theme_get_default().list_icons()
        self.cache = {}

    def __getSizeDescription__(self, size, exactly = False):
        """
        @summary: Gets size description from size.
        @param size: Size to format.
        @return: String with size description
        @raise ValueError: When size is too long or is less than 0.  
        """
        if size < 0:
            raise ValueError('number must be non-negative')
        
        fSize = float(size)
        bPointer = False
        
        multiple = float(1024 if (exactly) else 1000)
        
        for suffix in SUFFIXES[multiple]:
            if fSize < multiple:
                if (bPointer):
                    return ("%.1f %s" % (fSize, suffix))
                else:
                    return ("%.0f %s" % (fSize, suffix))
            fSize /= multiple
            bPointer = True
    
        raise ValueError('Number too large')

    def __getWindowsInfo__(self, file):
        """
        @summary: Gets icon from windows.
        @param file: Get information from file.
        @return: Tuple with information about extension.
                (hicon, iicon, attr, display_name, type_name)
        """
    
        flags = shellcon.SHGFI_TYPENAME
        sys_encoded_file = file.encode(sys.getfilesystemencoding())
        
        retval, info = shell.SHGetFileInfo(sys_encoded_file, FILE_ATTRIBUTE_NORMAL, flags, 0)
        # non-zero on success
        if (retval != 0):
            hicon, iicon, attr, display_name, type_name = info
            if (os.path.supports_unicode_filenames):
                try:
                    return (hicon, iicon, attr, unicode(display_name.decode(sys.getfilesystemencoding())), unicode(type_name.decode(sys.getfilesystemencoding())))
                except UnicodeDecodeError, ude:
                    __log__.error("Unicode error: %s" % ude)
            else:
                return (hicon, iicon, attr, str(display_name), str(type_name))
        else:
            return (0, 0, 0, "", "")
    
    def __getIconNameWindows__(self, path):
        """
        @summary: Get icon name in windows platform.
        @param path: Path of the file to get information.
        @return: Icon name 
        """
        if (os.path.isdir(path)):
            return gtk.STOCK_DIRECTORY
        
        sys_encoded_path = path.encode(sys.getfilesystemencoding())
        sys_encoded_path = sys_encoded_path.replace('/', '\\') #SHGetFileInfo doesn't work with Unix style paths
        ret, info = shell.SHGetFileInfo(sys_encoded_path, 0, shellcon.SHGFI_ICONLOCATION, 0)
        if ret and (info[1] or info[3]):
            icon = "gtk-win32-shell-icon;%s;%d" %(info[3], info[1])
        else:
            icon = "gtk-win32-shell-icon;%s" % sys_encoded_path
        icon_theme = gtk.icon_theme_get_default()
        if not icon_theme.has_icon(icon) and not self.__create_builtin_icon(icon, sys_encoded_path):
            __log__.debug("Icon not found. %s." % path)
            return gtk.STOCK_MISSING_IMAGE
        else:
            return icon

    def __create_builtin_icon(self, iconName, filepath):
        """
        @summary: Create icon in windows platform.
        @param iconName: Icon name to create.
        @param filepath: Path of file to extract icon.  
        """
        iconFlags = [shellcon.SHGFI_SMALLICON, shellcon.SHGFI_LARGEICON]
        try:
            for flag in iconFlags:
                ret, info = shell.SHGetFileInfo(filepath, 0, shellcon.SHGFI_ICON|flag, 0)
                if ret:
                    pixbuf = cgdk.gdk_win32_icon_to_pixbuf_libgtk_only(info[0])
                    if (pixbuf):
                        cgtk.gtk_icon_theme_add_builtin_icon(iconName, cgdkPixbuf.gdk_pixbuf_get_height(pixbuf), pixbuf)
                        return True
        except Exception, e:
            __log__.error("Insert icon into theme failed. %s" % e)
            return False
        return False

    
    def __getIconMimeWindows__ (self, path):
        """
        @summary: Gets an icon name from path, matching with its mime.
        @param path: Path to extract mime.
        @return: string with mime. None if it has not found mime. 
        """
        if (os.path.isdir(path)):
            return "x-directory/normal"
        try:
            extname = os.path.splitext(path)[-1]
            hkey = win32api.RegOpenKeyEx(win32con.HKEY_CLASSES_ROOT, extname, 0, win32con.KEY_READ)
            return win32api.RegQueryValueEx(hkey, 'Content Type')[0]
        except:
            __log__.warning(("It could not get Mime of %s" % path))
            return None

    
    def __getIconNameGnome__( self, path ):
        """
        @summary: Gets an icon name from path, matching with its mime.
        @param path: Path to extract icon name.
        @return: string with icon name 
        """
        
        #Check if path exist
        if not os.path.exists(path):
            __log__.warning("Path %s does not exist." % path)
            return gtk.STOCK_DIALOG_AUTHENTICATION
 
        #get mime
        mime_type = gnomevfs.get_mime_type( path ).replace( '/', '-' )
 
        #check if mime exists in the cache
        if mime_type in self.cache:
            return self.cache[mime_type]
 
        #try to get a gnome mime
        items = mime_type.split('-')
        for aux in xrange(len(items)-1):
            icon_name = "gnome-mime-" + '-'.join(items[:len(items)-aux])
            if icon_name in self.icons:
                self.cache[mime_type] = icon_name
                return icon_name
 
        #check and try to get a folder
        if os.path.isdir(path):
            icon_name = 'folder'
            if icon_name in self.icons:
                self.cache[mime_type] = icon_name
                return icon_name
 
            icon_name = gtk.STOCK_DIRECTORY
            self.cache[mime_type] = icon_name
            return icon_name
 
        #try to get a simple mime
        for aux in xrange(len(items)-1):
            icon_name = '-'.join(items[:len(items)-aux])
            if icon_name in self.icons:
                self.cache[mime_type] = icon_name
                return icon_name
 
        #if there isn't a mime for the path, get file icon
        __log__.debug("Icon name of %s not found." % path)
        icon_name = gtk.STOCK_FILE
        self.cache[mime_type] = icon_name
        return icon_name
    
    def getSize( self, path ):
        """
        @summary: Gets a tuple with size and size description with its units (bytes, Kbytes...)
        @param path: Path to calculate size.
        @return: Tuple with size and size description  
        """
        #Check if path exist
        if not os.path.exists(path):
            __log__.warning("Path does not exist. %s" % path)
            return (0, "")        
        if (os.path.isdir(path)):
            return (0, "")
        
        try:
            size = long(os.path.getsize(path))
        except:
            size = 0
        sizeDescription = ""
 
        
        if (GNOME):
            #get mime
            mime_type = gnomevfs.get_mime_type( path )
     
            uri = "file://%s" % urllib.pathname2url(path)
            fileInfo = gnomevfs.get_file_info(uri)
            
            if ((fileInfo.valid_fields & gnomevfs.FILE_INFO_FIELDS_SIZE) != 0):
                    size = fileInfo.size
                    sizeDescription = gnomevfs.format_file_size_for_display(size)
        else:
            sizeDescription = self.__getSizeDescription__(size) 
                
        return (size, sizeDescription)

    def getModifyDate( self, path ):
        """
        @summary: Gets a tuple with modify date and modify date description.
        @param path: Path to extract modify date
        @return: Tuple with modify date in long data and string data. 
        """
        #Check if path exist
        if not os.path.exists(path):
            return (time.mktime(datetime.now().timetuple()), "")
 
        modify = long(os.path.getctime(path))
        modifyDate = datetime.fromtimestamp(modify)
                        
        return (modify, modifyDate.strftime("%c"))
    
    def getMime( self, path ):
        """
        @summary: Gets a tuple with mime type and mime description.
        @param path: Path to extract mime.
        @return: Tuple with two string, 
            the first with mime name and the second with mime description.  
        """
        #Check if path exist
        if not os.path.exists(path):
            return ("", "")
 
        mimeType = ""
        mimeDescription = ""
 
        if (GNOME):
            #get mime
            mimeType = gnomevfs.get_mime_type( path )
            mimeDescription = gnomevfs.mime_get_description(mimeType)
        elif (WINDOWS):
            info = self.__getWindowsInfo__(path)
            file, ext = os.path.splitext(path)
            mimeType = ext
            mimeDescription = info[4]
            if (mimeDescription == ""):
                mimeDescription = ("%s %s" % (_("File"), ext))
                
        return (mimeType, mimeDescription)
        
    def getIconName(self, path):
        """
        @summary: Gets an icon name from path.
        @param path: Path to get icon name.
        @return: string with icon name. None is icon does not exist. 
        """
        icon = None
        
        if (GNOME):
            icon = self.__getIconNameGnome__(path)
        elif (WINDOWS):
            icon = self.__getIconNameWindows__(path)
        
        return icon
    
    def getIcon(self, path):
        """
        @summary: Gets an icon from path, matching with its mime.
        @param path: Path to get icon.
        @return: Icon of the path. None if it is not gnome or windows platform.
        """
        if (GNOME):
            return FactoryControls.getPixbufFromStock(self.getIconName(path))
        elif (WINDOWS):
            return FactoryControls.getPixbufFromStock(self.getIconName(path))
            
        
        return None