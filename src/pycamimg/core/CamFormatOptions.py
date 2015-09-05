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
import os.path
import sys
import logging
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")

import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

try:
    from PIL import Image
except ImportError, e:
    __log__.fatal("It could not import Image.PIL. Sure you have installed PIL library. %s" % e)
    
try:
    from PIL import Image
    from PIL import JpegImagePlugin
    Image._initialized = 2
except ImportError, e:
    __log__.fatal("It could not import Image.PIL. Sure you have installed PIL library. %s" % e)
    
from pycamimg.util import ImageUtils
    
jpegOptions = {"quality" : 95}

def openWithExtraInfo(path, extension):
    """
    @summary: Gets a pointer and extra info from path.
    @param path: Path of image.
    @param extension: Extension of image.
    @return: Tuple within (handler of image, extraInfo)  
    """
    extraInfo = None
    try:
        img2do = Image.open(path)
    except IOError:
        __log__.error("An error has occurred when it was trying to open %s. Skip operation." % fileop)
        img2do = None
        
    if (extension == "JPEG"):
        extraInfo = ImageUtils.getJpegInfo(path)
        
    return (img2do, extraInfo)

def saveWithOptions(img, output, extension, extraInfo=None):
    """
    @summary: Gets a dictionary with options for extension.
    @param img: PIL.Image to save.
    @param output: outfile where store img
    @param extension: Extension of the output file.   
    """
    try:
        if (extension == "JPEG"):
            img.save(output, extension,
                     quality=jpegOptions["quality"])
            if (extraInfo != None):
                __log__.debug("It is a JPEG image. It will set EXIF information...")
                ImageUtils.setJpegInfo(output, extraInfo)
        else:
            img.save(output, extension)
    except Exception, e:
        __log__.error("It could not save %s. %s" (output, e))
