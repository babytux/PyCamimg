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
import os
import os.path
import shutil
import sys
import logging
import string
import cPickle
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

from threading import Thread
from operations.Operations import Operation
from pycamimg.core import CamFormatOptions
from pycamimg.util.ImgMeta import ImgMeta
from pycamimg.core.Configuration import Configuration
from pycamimg.core.operations import Operations

ACTION_COPY = 0
ACTION_MOVE = 1

class CamItem:
    """
    @summary: Define an item to apply some operations.
    """
    def __init__(self, path, target=None):
        """
        @summary: Create a CamItem.
        @param path: Path of file that will be represented by CamItem.
        @param target: Path where the result of operations will store.
        @note: If target is not set, the result will store into path. 
        """
        self.__path__ = path
        self.__operations__ = {}
        self.__target__ = target
        self.__thumbnail__ = None
        self.__metaData__ = None
        self.__addPhotoAlbum__ = False
        
        # Generate thumbnail of CamItem
        self.__thThumbLoad__ = Thread(target=self.__generateThumbnail__)
        self.__thThumbLoad__.start()
        
    def __getnewargs__(self):
        """
        @summary: Gets initial arguments of instance.
        @return: Tuple with parameters.
        """
        return (self.__path__, self.__target__)
        
    def __generateThumbnail__(self):
        """
        @summary: Generate thumbnail of CamItem.
        """
        if (self.__thumbnail__ == None):
            __log__.debug("Delete previous thumbnail")
            del self.__thumbnail__
            self.__thumbnail__ = None
        
        if (self.__path__ != None):
            height = Configuration().getConfiguration().getint("TABPROJECT", "max_height_imagelist")
            self.refreshThumbnail(height)
        else:
            __log__.debug("There is not path to open image of CamItem")
            
    def __doOperations__(self, img2do):
        """
        @summary: Do a preview image.
        @img2do: Image over It will do the operations.
        @return: A PIL.Image object.
        """
        __log__.info("Doing preview on %s" % self.__path__)
        if (self.__operations__ != None):
            if (len(self.__operations__) > 0):
                # Open image to do operations over image object
                for key, op in self.__operations__.iteritems():
                    img2do = op.preview(img2do)
            else:
                __log__.debug("There are not operations for %s" % self.__path__)
        else:
            __log__.debug("There are not operations for %s" % self.__path__)
            
        return img2do
    
    def refreshThumbnail(self, height):
        """
        @summary: Refresh thumbnail.
        @param height: Max height of thumbnail 
        """
        try:
            img2do = Image.open(self.__path__)
        except IOError:
            __log__.error("An error has occurred when it was trying to open %s." % self.__path__)
            img2do = None
    
        if (img2do != None):
            resizePercent = float(height) / float(img2do.size[1])
            width = int(img2do.size[0] * resizePercent)
            img2do.thumbnail((width, height), Image.NEAREST)
            self.__thumbnail__ = img2do
            
            # Handler to extract metadata
            try:
                self.__metaData__ = ImgMeta(self.getPath(), image=self.__thumbnail__)
                __log__.debug("Extracted metada from %s" % self.getPath())
            except Exception, e:
                self.__metaData__ = None
                __log__.error("Can not extract metadata from %s. %s" % (self.getPath(), e))
    
    def waitLoadThumbnail(self, timeout = -1):
        """
        @summary: Waits until thumbnail is loaded.
        @param timeout: Time to wait. 
        """
        if (self.__thThumbLoad__ != None):
            if (timeout != -1):
                self.__thThumbLoad__.join(timeout)
            else:
                self.__thThumbLoad__.join()
    
    def getMetadata(self):
        """
        @summary: Gets metadata information of image.
        @return: pycamimg.util.ImgMeta.ImgMeta
        """
        return self.__metaData__
    
    def getThumbnail(self):
        """
        @summary: Gets thumbnail of item.
        @return: PIL.Image
        """
        return self.__thumbnail__
   
    def setAddPhotoAlbum(self, addPhotoAlbum):
        """
        @summary: Sets if result of camitem will
        add to photo album.
        @param addPhotoAlbum: True to add to photo album. 
        """
        self.__addPhotoAlbum__ = addPhotoAlbum
        
    def isAddPhotoAlbum(self):
        """
        @summary: Gets if result of camitem will
        add to photo album.
        @return: True to add to photo album.
        """
        return self.__addPhotoAlbum__
    
    def setProperty(self, key, value):
        """
        @summary: Sets value to a property
        @param key: str within property
        @param value: New value.  
        """
        if (key == "target"):
            self.__target__ = value
        elif (key == "path"):
            self.__path__ = value
        elif (key == "thumbnail"):
            self.__thumbnail__ = value
        else:
            __log__.warning("%s key is not valid." % key)
            return
        
        __log__.debug("%s key updated." % key)
                    
    
    def addOperation(self, key, operation):
        """
        @summary: Add an operation to apply to an item.
        @param key: Key of the operations. 
        @param operation: An operation instance. 
        """
        if (self.__operations__.has_key(key)):
            __log__.warning("%s just exist. It will be overwritten" % key)
        self.__operations__[key] = operation
    
    def removeOperation(self, key):
        """
        @summary: Remove an operation.
        @param key: Key of a operation.
        """
        if (self.__operations__.has_key(key)):
            del self.__operations__[key]
        else:
            __log__.warning("%s does not exist." % key)
        
    def getOperation(self, key):
        """
        @summary: Gets an operation from item operations.
        @return: An operation instance added before with key
        """
        operation = None
        if (self.__operations__.has_key(key)):
            operation = self.__operations__[key]
        else:
            __log__.info("%s does not exist" % key)
        return operation

    def getPath(self):
        """
        @summary: Gets path of file that CamItem handle.
        @return: string with the path.
        """
        return self.__path__

    def getTarget(self):
        """
        @summary: Gets target path.
        @return: string with the path.
        """
        return self.__target__

    def setTarget(self, target):
        """
        @summary: Sets target path.
        @param target: Path of the target file. 
        """
        self.__target__ = target

    def getOperations(self):
        """
        @summary: Gets operations associated with item.
        @return: Dictionary within operations.
        """
        return self.__operations__

    def getDescription(self):
        """
        @summary: Gets a string that contains a description of operations.
        @return: Description of CamItem
        """
        description = ""
        if (self.__operations__ != None):
            bFirst = True
            for key, op in self.__operations__.iteritems():
                if (not bFirst):
                    description += "\n"
                else:
                    bFirst = False
                description += "%s [%s]" %(op.getOp(), op.toString())
        if (description == ""):
            description = ""
        return description

    def doPreview(self):
        """
        @summary: Do a preview image.
        @return: A PIL.Image object. None if it is not a valid image.
        """
        self.waitLoadThumbnail()
        if (self.__thumbnail__ != None):
            return self.__doOperations__(self.__thumbnail__.copy())
        else:
            return None

    def doOperations(self, projectType, action=ACTION_COPY, tempFolder=None):
        """
        @summary: Do operations on image.
        @param projectType: Instance of IProyectType.
        @param action: Action that it will do with input file. Copy=ACTION_COPY or Move=ACTION_MOVE
        @param tempFolder: Folder where actions will do.
        @note: If tempFolder is not set, Operations will do on input file.
        @see: pycamimg.core.projectType.IProjectType    
        """
        meta = None
        __log__.info("Doing operations on %s" % self.__path__)
        fileop = self.__path__
        if (tempFolder != None):
            __log__.debug("Temporal folder is specified. %s" % tempFolder)
            head, tail = os.path.split(self.__path__)
            tempFile = os.path.join(tempFolder, tail)
            fileop = tempFile
            
            shutil.copy2(self.__path__, tempFile)
            __log__.debug("Copy file from %s to %s" % (self.__path__, tempFile))
            
            if (not projectType.PreDoItem(fileop)):
                __log__.error("An error was occurred when it was doing PreDoItem on %s" % fileop)
                os.remove(fileop)
                return None

        if (self.__operations__ != None):
            if (len(self.__operations__) > 0):
                ext = string.lower(os.path.splitext(fileop)[1])
                ext = Image.EXTENSION[ext]
                
                # Open image to do operations over image object
                img2do = None
                extraInfo = None
                try:
                    img2do, extraInfo = CamFormatOptions.openWithExtraInfo(fileop, ext)
                except Exception, ex:
                    __log__.error("An error has occurred when it was trying to open %s. Skip operation. %s" % (fileop, ex))
                    img2do = None
                    extraInfo = None
        
                if (img2do != None):
                    for key, op in self.__operations__.iteritems():
                        img2do = op.do(img2do, path=fileop)
                        
                    try:
                        CamFormatOptions.saveWithOptions(img2do, fileop, ext)
                    except IOError, ioe:
                        __log__.error("It could not save %s. Please check your permissions. %s" % (fileop, ioe))
                        raise IOError("It could not save %s. Please check your permissions. %s" % (fileop, ioe))
                    except Exception, ex:
                        __log__.error("It could not save %s. Please check your permissions. %s" % (fileop, ex))
                    finally:
                        if (img2do != None):
                            del img2do
                            img2do = None
            else:
                __log__.debug("There are not operations for %s" % self.__path__)
        else:
            __log__.debug("There are not operations for %s" % self.__path__)

        
        if (self.isAddPhotoAlbum()):
            pass
            #TODO: Add to photo album

        if (self.__target__ != None):
            head, filename = os.path.split(fileop)
            newFile = os.path.join(head, self.__target__)
            shutil.move(fileop, newFile)
            __log__.debug("Move file from %s to %s" % (fileop, newFile))
            fileop = newFile

        if (not projectType.PostDoItem(fileop)):
            __log__.error("An error was occurred when it was doing PreDoItem on %s" % fileop)
            os.remove(fileop)
                
        if (action == ACTION_MOVE):
            os.remove(self.__path__)
            __log__.debug("Delete file from %s" % self.__path__)
                
        __log__.info("Operations on %s are done." % self.__path__)
      
    def saveItem(self, fo):
        """
        @summary: Save item into a file. 
        @param fo: File where item will be saved. 
        """
        CamItem.save(self, fo)
        
    def save(item, fo):
        """
        @summary: Save item into a file.
        @param item: Item to save. 
        @param fo: File where item will be saved. 
        """
        cPickle.dump(item.getPath(), fo, PICKLE_PROTOCOL)
        cPickle.dump(item.getTarget(), fo, PICKLE_PROTOCOL)
        cPickle.dump(len(item.getOperations()), fo, PICKLE_PROTOCOL)
        
        if (len(item.getOperations()) > 0):
            for key, operation in item.getOperations().iteritems():
                cPickle.dump(key, fo, PICKLE_PROTOCOL)
                cPickle.dump(operation.getParameters(), fo, PICKLE_PROTOCOL)
            
        __log__.debug("Item %s saved." % item.getPath())
        
    save = staticmethod(save)
        
    def load(fi):
        """
        @summary: Load item from a file.
        @param fi: File where item is saved.
        @return: item loaded. 
        """
        path = cPickle.load(fi)
        target =  cPickle.load(fi)
        length =  cPickle.load(fi)
        item = CamItem(path, target)
        
        while (length > 0):
            keyOp = cPickle.load(fi)
            parameters = cPickle.load(fi)
            classname = Operations.getOperation(name)
            op = classname(keyOp, parameters)
            item.addOperation(keyOp, op)
            length -= 1
            
        __log__.debug("Item %s saved." % self.__path__)
        
        return item
        
    load = staticmethod(load)

if __name__ == "__main__":
    print "Test mode..."
