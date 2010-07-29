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
    from jpeg import jpeg
except ImportError, e:
    __log__.fatal("It could not import jpeg.jpeg. Sure you have installed jpeg library. %s" % e)

PIXEL = 0
CM = 1
PERCENT = 2
CM_INCH = 2.54

def getJpegInfo (path):
    """
    @summary: Gets jpeg information.
    @return: Tuple with exif info, exif2 info and comments.
    """
    try:
        infoExif = jpeg.getExif(path)
        __log__.debug("Gets EXIF information %s" % infoExif)
    except Exception:
        __log__.warning("It could not get EXIF information from %s" % path)
        infoExif = None
    try:
        infoExif2 = jpeg.getExif2(path)
        __log__.debug("Gets EXIF2 information %s" % infoExif2)
    except Exception:
        __log__.warning("It could not get EXIF2 information from %s" % path)
        infoExif2 = None
    try:
        infoComments = jpeg.getComments(path)
        __log__.debug("Gets comments %s" % infoComments)
    except Exception:
        __log__.warning("It could not get comments information from %s" % path)
        infoComments = None
        
    return (infoExif, infoExif2, infoComments)

def setJpegInfo (path, info):
    """
    @summary: Set exif information into jpef file.
    @param path: Path where information will be set.
    @param info: Tuple with exif info, exif2 info and comments. 
    """
    
    infoExif, infoExif2, infoComments = info
    
    if (infoExif != None):
        jpeg.setExif(infoExif, path)
    else:
        __log__.warning("There is not EXIF information.")
    
    if (infoExif2 != None):
        jpeg.setExif2(infoExif2, path)
    else:
        __log__.warning("There is not EXIF2 information.")
    
    if (infoComments != None):
        jpeg.setComments(infoComments, path)
    else:
        __log__.warning("There are not comments.")


def pixelToCm (size, dpi):
    """
    @summary: Gets size in cm from pixel size.
    @param size: Tuple with width and height on pixel scale.
    @param dpi: Dots per inch.
    @return: Tuple with width and height on cm scale.  
    """
    factor = float(CM_INCH) / float(dpi)
    newSize = (size[0] * factor, size[1] * factor)
    return newSize

def cmToPixel (size, dpi):
    """
    @summary: Get size in pixel from cm size.
    @param size: Tuple with width and height on cm scale.
    @param dpi: Dots per inch.
    @return: Tuple with width and height on pixel scale.
    """
    factor = float(dpi) / float(CM_INCH)
    newSize = (round(size[0] * factor), round(size[1] * factor))
    return newSize 
