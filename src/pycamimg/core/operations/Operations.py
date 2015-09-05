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

import string
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
    from PIL import JpegImagePlugin
    Image._initialized = 2
except ImportError, e:
    __log__.fatal("It could not import Image.PIL. Sure you have installed PIL library. %s" % e)
    
from pycamimg.util import ImageUtils
from pycamimg.core import CamFormatOptions

class Operation:
    """
    @summary: Defines a generic operation to do on camimg item
    """
    
    def __init__(self):
        """
        @summary: Create a generic operation.
        """
        self.__initialize__(input, "", {})

    def __initialize__(self, op, args):
        """
        @summary: Initialize a generic operation.
        @param op: Operation name. 
        @param args: Dictionary with name of arguments (key) and its value..  
        """
        __log__.debug("Initializing operation %s..." % op)
        self.__op__ = op
        self.__args__ = args

    def getOp(self):
        """
        @summary: Gets operation name.
        @return: Name of operation.
        """
        return self.__op__

    def getParameterKeys(self):
        """
        @summary: Gets a list with key of each parameter.
        @return: A list with all keys.
        """
        if (self.__args__ != None):
            return self.__args__.keys()
        else:
            return []

    def getParameter(self, name):
        """
        @summary: Gets value of a parameter.
        @param name: Name of a parameter.
        @return: Parameter value.
        @raise KeyError: Raise when parameter does not exist.  
        """
        if (self.__args__ != None):
            if (self.__args__.has_key(name)):
                return self.__args__[name]
            else:
                __log__.warning("Unknown key in parameters dictionary [%s]. Raising KeyError" % name)
                raise KeyError("%s does not exist." % name)
        else:
            __log__.warning("There are not parameters defined. Raising ValueError")
            raise ValueError("There are not parameters")

    def setParameter(self, name, value):
        """
        @summary: Sets value of a parameter.
        @param name: Name of a parameter that will be set.
        @param value: New value for the parameter.
        """
        if (self.__args__ == None):
            self.__args__ = {}
        self.__args__[name] = value
        
    def getParameters(self):
        """
        @summary: Gets dictionary within parameters
        @return: Dictionary within parameters
        """
        return self.__args__
    
    def setParameters(self, params):
        """
        @summary: Sets dictionary within parameters of a operation.
        @param params: Dictionary within parameters. 
        """
        self.__args__ = params

    def toString(self):
        """
        @summary: Gets a string with a description about the operation.
        @return: Description of the operation.
        """
        desc = ""
        if (self.__args__ != None):
            bFirst = True
            for key, value in self.__args__.iteritems():
                if (not bFirst):
                    desc += ";"
                else:
                    bFirst = False
                desc += "%s: %s" % (key, value)
        return desc

    def doOnPath(self, path):
        """
        @summary: Do operation on path.
        @param path: File on path will be used as input file.
        @note: Generic operation will always do nothing. 
               Its child classes should overwrite this method.  
        """
        
        
        # Open image to do operations over image object
        try:
            img2do = Image.open(path)
        except IOError:
            __log__.error("An error has occurred when it was trying to open %s. Skip operation." % path)
            img2do = None

        if (img2do != None):
            # HACKME: Try to remove dependency with jpeg
            infoExif = None
            infoExif2 = None
            infoComments = None
            
            infoExif, infoExif2, infoComments = ImageUtils.getJpegInfo(path)
            
            self.do(img2do)
            
            try:
                ext = string.lower(os.path.splitext(path)[1])
                ext = Image.EXTENSION[ext]
                CamFormatOptions.saveWithOptions(img2do, path, ext)
                
                if (ext == "JPEG"):
                    __log__.debug("It is a JPEG image. It will set EXIF information...")
                    ImageUtils.setJpegInfo(path, (infoExif, infoExif2, infoComments))
            except IOError, ioe:
                __log__.error("It could not save %s. Please check your permissions. %s" % (path, ioe))
                raise IOError("It could not save %s. Please check your permissions. %s" % (path, ioe))
            finally:
                del img2do
                img2do = None
        

    def do(self, imgobj, path=None):
        """
        @summary: Do operation on input file.
        @param imgobj: Image object
        @param path: Path of imgobj. 
        @return: PIL.Image object as result of operation.
        """
        return imgobj
        
    def preview(self, imgobj):
        """
        @summary: Do a preview of operation
        @return: Image object
        """
        return self.do(imgobj)

__aOperations__ = {}

def addOperation (key, operationClass):
    """
    @summary: Add an operation class to operation dictionary.
    @param key: Key that represents to operation.
    @param operationClass: Class reference.  
    @return: True if operation class was added.
    """
    if (__aOperations__.has_key(key)):
        return False
    else:
        __aOperations__[key] = operationClass
        return True

def getOperation(key):
    """
    @summary: Gets an operation class from a key.
    @param key: Key of the operation to look up. 
    @return: An operation class. None if it has not found.
    """
    if (__aOperations__.has_key(key)):
        return __aOperations__[key]
    else:
        return None


if __name__ == "__main__":
    print "Module"
