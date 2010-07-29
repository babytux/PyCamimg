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
import logging
import os.path
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")

import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

try:
    from PIL import Image
    from PIL import JpegImagePlugin
    Image._initialized=2
except ImportError, e:
    __log__.fatal("It could not import Image.PIL. Sure you have installed PIL library. %s" % e)
    
from pycamimg.util import ImageUtils
from pycamimg.core.operations import Operations
from pycamimg.core.operations.Operations import Operation

OPERATION = "Resize"
DEFAULT_DPI = 300


class Resize(Operation):
    """
    @summary: This class implements a operation of a resizing.
    @see: Operation 
    """
    
    def __init__(self, size = (100, 100), scale = ImageUtils.PERCENT):
        """
        @summary: Create a resize operation.
        @param size: Tuple with Width x Height that input file will resize. Default = (100,100)
        @param scale: Scale units. Default ImageUtils.PERCENT 
        """
        self.__initialize__(OPERATION, {"width": size[0], "height": size[1], "scale": scale, "filter": Image.ANTIALIAS})

    def preview(self, imgobj):
        """
        @summary: Do a preview over image
        @param imgobj: Image object over it will do the preview 
        """
        return imgobj
        
    def do(self, imgobj, path=None):
        """
        @summary: Do a resizing.
        @param imgobj: File on path will be used as input file.
        @param path: Path of imgobj.
        @return: PIL.Image object as result of operation.
        @raise Exception: Raise when it can not resize image. 
        """            
        scale = self.__args__["scale"]
        __log__.debug("Get scale: %d" % scale)
        
        if (scale == ImageUtils.CM):
            size = ImageUtils.cmToPixel((self.__args__["width"], 
                                         self.__args__["height"]), DEFAULT_DPI)
        elif (scale == ImageUtils.PIXEL):
            size = (int(self.__args__["width"]), int(self.__args__["height"]))
        elif (scale == ImageUtils.PERCENT):
            srcSize = imgobj.size
            size = (int(srcSize[0] * (float(self.__args__["width"]) / 100)),
                    int(srcSize[1] * (float(self.__args__["height"]) /100)))
        else:
            __log__.error("Scale has non-valid value. %d" % scale)
            raise ValueError("Scale has non-valid value. %d" % scale)

        __log__.debug("Get new size: %d x %d" % size)

        try:
            imgobj = imgobj.resize(size, self.__args__["filter"])
            if (path != None):
                __log__.info("%s Resized." % path)
            else:
                __log__.debug("Resized")
        except Exception, e:
            if (path != None):
                __log__.error("An error has occurred when it was resizing %s. %s" % (path, e))
            else:
                __log__.error("An error has occurred when it was resizing. %s", e)
        return imgobj