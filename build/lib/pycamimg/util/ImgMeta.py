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
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError, ie:
    __log__.fatal("It could not load PIL library. Check if PIL is installed. %s" % ie)
    raise ie
import StringIO
try:
    import gtk
except ImportError, ie:
    __log__.fatal("It could not load gtk library. Check if gtk is installed. %s" % ie)
    raise ie

DEFAULT_REESCALE_PERCENT = 25.0
DEFAULT_MAXHEIGHT = 32

class ImgMeta:
    """
    @summary: Class to extract information about an image file.
    """
    def __init__(self, file, image=None, doLoad=False, thumbnail=False):
        """
        @summary: Create new handler or image metadata.
        @param file: path of the file to extract its metadata.
        @param image: PIL.Image to get information.
        @param doLoad: True if do load operation after open.
        @param thumbnail: True if do operations over thumbnail.
        @raise TypeError: Raise when file is not str or unicode.  
        @raise TypeError: Raise when image is not PIL.Image.Image 
        """
        if (not isinstance(file, str) and not isinstance(file, unicode)):
            raise TypeError("file must be str or unicode")
        if (image != None):
            if (not isinstance(image, Image.Image)):
                raise TypeError("image must be Image.Image")
        
        self.__file__ = file
        self.__isThumbnail__ = False
        self.__info__ = {}
        
        if (image == None):
            # Create new info object
            self.__handler__ = Image.open(file)
        else:
            self.__handler__ = image
        
        if (thumbnail):
            self.__handler__.thumbnail(self.__handler__.size, Image.NEAREST)
            self.__isThumbnail__ = True    
        elif (doLoad):
            self.__handler__.load()
            
    def __del__(self):
        """
        @summary: Destructor of ImgMeta
        """
        del self.__handler__
        
    
    def __getPixbufFromImage__(self, image, size, thumbnail=True):
        """
        @summary: Gets pixbuf from image.
        @param image: Image to get as a pixbuf.
        @param size: Size of generated pixbuf.
        @param thumbnail: True for generates pixbuf from thumbnail.
        @return: GtkPixbuf of the image. 
        """
        file = StringIO.StringIO()
        
        img = image.copy()
        if (thumbnail):
            img.thumbnail(size, Image.NEAREST)
        else:
            img = img.resize(size, Image.NEAREST)
        img.save (file, "JPEG")
        
        __log__.debug("%s was saved into memory buffer." % self.__file__)
        contents = file.getvalue()
        file.close()
        loader = gtk.gdk.PixbufLoader("jpeg")
        loader.write (contents, len (contents))
        pixbuf = loader.get_pixbuf()
        __log__.debug("Pixbuf for %s created" % self.__file__)
        loader.close ()
        del img
        return pixbuf

    def getFormat(self):
        """
        @summary: Gets image format.
        @return: string with the format of the image.
        """
        if self.__handler__ != None:
            return self.__handler__.format
        else:
            __log__.warning("It is not initialize the handler of the image.")
        return None

    def getInfo(self):
        """
        @summary: Gets image info.
        @return: Hashtable with exif metadata.
        """
        if self.__handler__ != None:
            return self.__handler__.info
        else:
            __log__.warning("It is not initialize the handler of the image.")
        return None

    def setExifInfo(self, info):
        """
        @summary: Sets exif info. 
        """
        if ((info != None) and (self.__handler__ != None)):
            self.__handler__.info["exif"] = info

    def getExifInfoUndecoded(self):
        """
        @summary: Gets image exif info undecoded.
        @return: Hashtable with exif metadata.
        """
        if self.__handler__ != None:
            return self.__handler__._getexif()
        else:
            __log__.warning("It is not initialize the handler of the image.")
        return None

    def getExifInfo(self):
        """
        @summary: Gets image exif info.
        @return: Hashtable with exif metadata.
        """
        if (len(self.__info__) == 0):
            if self.__handler__ != None:
                infoHandler = self.__handler__._getexif()
                if (infoHandler != None):
                    # decode every tags of image
                    for tag,value in infoHandler.items():
                        decodedKey = TAGS.get(tag,tag)
                        self.__info__[decodedKey] = value
                else:
                    __log__.debug("It could not retrieve exif information from %s" % self.__file__)
            else:
                __log__.warning("It is not initialize the handler of the image.")
        return self.__info__

    def getIcon(self, rescale=DEFAULT_REESCALE_PERCENT, maxHeight=DEFAULT_MAXHEIGHT):
        """
        @summary: Gets a pixbuf.
        @param rescale: Percentaje of the rescale. Default: DEFAULT_REESCALE_PERCENT
        @param maxHeight: Maximum height of the icon. Default: DEFAULT_MAXHEIGHT
        @return: GtkPixbuf.
        @raise TypeError: Raise when rescale is not float or int. 
                        Or maxHeight is not int. 
        """
        if (not isinstance(rescale, (float, int))):
            raise TypeError("rescale must be float or int")
        if (not isinstance(maxHeight, int)):
            raise TypeError("maxHeight must be int")
        
        if self.__handler__ != None:
            size = self.getSize()
            if (size != None):
                width = int(size[0] * (float(rescale) / 100))
                height = int(size[1] * (float(rescale) / 100))
                
                if (height > maxHeight):
                    rel = float(maxHeight) / size[1]
                    width = int(size[0] * rel)
                    height = int(maxHeight)
                
                return self. __getPixbufFromImage__(self.__handler__, (width, height), thumbnail=(not self.__isThumbnail__))
            else:
                __log__.warning("Could not get size of image %s." % self.__file__)
        else:
            __log__.warning("It is not initialize the handler of the image. %s" % self.__file__)
        return None

    def getSize(self):
        """
        @summary: Gets image information.
        @return: Tuple with the size (width, height).
        """
        if self.__handler__ != None:
            return self.__handler__.size
        else:
            __log__.warning("It is not initialize the handler of the image.")
        return None

    def getDateTimeDigitized(self):
        """
        @summary: Gets DateTime Digitized.
        @return: String with Date and Time when image was taken.
        """
        info = self.getExifInfo()
        if info.has_key("DateTimeDigitized"):
            return info["DateTimeDigitized"]
        return ""

    def close(self):
        """
        @summary: Closes file.
        """
        if self.__handler__ != None:
            del self.__handler__
            self.__handler__ = None
        else:
            __log__.warning("It is not initialize the handler of the image.")

    def save(self):
        """
        @summary: Save file.
        """
        if self.__handler__ != None:
            self.__handler__.save(self.__file__)
        else:
            __log__.warning("It is not initialize the handler of the image.")

    def show(self):
        """
        @summary: Show image in system viewer.
        """
        if self.__handler__ != None:
            self.__handler__.show()
        else:
            __log__.warning("It is not initialize the handler of the image.")