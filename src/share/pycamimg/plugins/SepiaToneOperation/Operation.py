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
    Image._initialized = 2
    from PIL import ImageOps
except ImportError, e:
    __log__.fatal("It could not import Image.PIL. Sure you have installed PIL library. %s" % e)
    
from pycamimg.util import ImageUtils
from pycamimg.core.operations import Operations
from pycamimg.core.operations.Operations import Operation

OPERATION = "SepiaTone"

def make_linear_ramp(white):
    # putpalette expects [r,g,b,r,g,b,...]
    ramp = []
    r, g, b = white
    for i in range(255):
        ramp.extend((r * i / 255, g * i / 255, b * i / 255))
    return ramp

# make sepia ramp (tweak color as necessary)
sepia = make_linear_ramp((255, 240, 192))


class SepiaTone(Operation):
    """
    @summary: This class implements sepia toning operation.
    @see: Operation 
    """
    def __init__(self):
        """
        @summary: Create a sepia toning operation.
        """
        self.__initialize__("SepiaTone", {})

    def do(self, imgobj, path=None):
        """
        @summary: Do sepia toning on path.
        @param imgobj: Image object over it will do sepia toning operation
        @param path: Path of imgobj.
        @return: PIL.Image object as result of operation.
        @raise Exception: Raise when it can not apply sepia toning to an image. 
        """
        return self.__do__(imgobj, path=path)
        
    def __do__(self, imgobj, path=None):
        """
        @summary: Do sepia toning on path.
        @param imgobj: Image object over it will do sepia toning operation
        @param path: Path of imgobj.
        @return: PIL.Image object as result of operation.
        @raise Exception: Raise when it can not apply sepia toning to an image. 
        """        
        try:
            imgobj = ImageOps.grayscale(imgobj)
            # apply sepia palette
            im.putpalette(sepia)

            if (path != None):
                __log__.info("%s Sepia toning applied." % path)
            else:
                __log__.debug("Sepia toning applied")
        except Exception, e:
            if (path != None):
                __log__.error("An error has occurred when it was applaying sepia toning to %s. %s" % (path, e))
            else:
                __log__.error("An error has occurred when it was applaying sepia toning. %s", e)
        return imgobj
    
    def preview(self, imgobj):
        """
        @summary: Do a preview of operation
        @return: Image object
        """
        return self.__do__(imgobj)
