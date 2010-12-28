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
import cPickle
import sys

import logging
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

import threading, thread
from threading import Thread
from threading import Semaphore
import time

import CamItem

import pycamimg.core.plugins.IProjectType
from pycamimg.core.plugins.IProjectType import Project

STATE_IDLE = 0
STATE_EXEC = 1
STATE_FINISHED = 2

PICKLE_PROTOCOL = 2

class CamCore: 
    """
    @summary: Defines a core that process some items
    """
    
    def __init__(self, temp=None, isCopy=True, projectType=None):
        """
        @summary: Creates new CamCore.
        @param temp: Temporal folder.
        @param isCopy: True to make a copy of source files of the project.
        @param projectType: Type of project that core is. 
        """
        self.__finished__ = False
        self.__currentItem__ = None
        self.__name__ = ""
        self.__currentKey__ = ""
        self.__items__ = {}
        self.__orderItemsProcess__ = []
        self.__temp__ = temp
        self.__isCopy__ = isCopy
        self.__callbackEndProcess__ = None
        self.__callbackBeginItem__ = None
        self.__callbackEndItem__ = None
        self.__isSaved__ = False
        self.__filename__ = None
        self.__mainWindow__ = None
        self.__state__ = STATE_IDLE
        self.__threadExec__ = None
        self.__semaphore__ = Semaphore()
        self.__cancel__ = False
        self.__addPhotoAlbum__ = False
        
        if (projectType != None):
            self.__projectType__ = projectType()
            self.__projectTypeReference__ = projectType
            __log__.debug("Created project type specified before. %s" % self.__projectType__)
        else:
            self.__projectType__ = Project()
            self.__projectTypeReference__ = Project
            __log__.debug("ProjectType is not specified. It has created LocalProject. %s" % self.__projectType__)
    
    def __process__(self):
        """
        @summary: Process all items of the core.
        """
        __log__.info("Begin process of core %s" % self)
        
        if ((self.__items__ != None) and (not self.__finished__)):
        
            actionop = CamItem.ACTION_COPY
            if (not self.__isCopy__):
                __log__.debug("Core will not copy source files. Beware with this action.")
                actionop = CamItem.ACTION_MOVE
                
            if (self.__orderItemProcess__ == None):
                self.__orderItemProcess__ = self.__items__.keys().sort()
            elif (len(self.__orderItemProcess__) == 0):
                self.__orderItemProcess__ = self.__items__.keys().sort()    

            # Do each item.
            for key in self.__orderItemProcess__:
                #for key, item in self.__items__.iteritems():
                self.__semaphore__.acquire()
                if (self.__cancel__ == True):
                    thread.exit()
                self.__semaphore__.release()
                
                __log__.debug("Processing %s item..." % key)
                item  = self.__items__[key]
                if (item != None):
                    item.setAddPhotoAlbum(self.isAddPhotoAlbum())
                    if (self.__callbackBeginItem__ != None):
                        __log__.debug("There is begin item callback. It is going to do it. %s" % self.__callbackBeginItem__)
                        self.__callbackBeginItem__(item)
                    
                    self.__currentKey__ = key
                    self.__currentItem__ = item
                    
                    try:
                        item.doOperations(self.__projectType__, action=actionop, tempFolder=self.__temp__)
                    except Exception, e:
                        __log__.error("An error has occurred when it was processing %s item. %s" % (key, e))

                    if (self.__callbackEndItem__ != None):
                        __log__.debug("There is end item callback. It is going to do it. %s" % self.__callbackEndItem__)
                        self.__callbackEndItem__(item)

                else:
                    __log__.warning("%s item is None." % key)
                    
                __log__.info("%s item processed." % key)
        else:
            if (self.__items__ == None):
                __log__.info("Process Aborted. There are not item in core %s." % self)
            elif (self.__finished__):
                __log__.info("Process Aborted. Core status is finished.")

        self.__currentKey__ = ""
        self.__currentItem__ = None

        if (self.__projectType__ != None):
            if (not self.__projectType__.PostDoProject(self, self.getMainWindow())):
                __log__.info("It could not execute post project actions.")

        if (self.__callbackEndProcess__ != None):
            __log__.debug("There is end process callback. It is going to do it. %s" % self.__callbackEndProcess__);
            self.__callbackEndProcess__()
            
        self.__finished__ = True
        self.__state__ = STATE_FINISHED
    
    def isCopy(self):
        """
        @summary: Gets if items will be copied.
        @return: True if items will be copied.
        """
        return self.__isCopy__
    
    def setTranslator(self, translationFunction):
        """
        @summary: Sets translator function.
        @param translationFunction: callback 
        """
        self._ = translationFunction
        if (self.__projectType__ != None):
            self.__projectType__.setTranslator(translationFunction)
       
    def setName (self, name):
        """
        @summary: Sets project name
        @param name: New name for the project 
        """
        self.__name__ = name
    
    def getName (self):
        """
        @summary: Gets project name.
        @return: string with project name.
        """
        return self.__name__ 
    
    def setMainWindow(self, window):
        """
        @summary: Sets main window
        @param window: GtkWindow to set. 
        """
        self.__mainWindow__ = window
    
    def getMainWindow(self):
        """
        @summary: Gets main window
        @return: GtkWindow to set. 
        """
        return self.__mainWindow__
    
    def setAddPhotoAlbum(self, addPhotoAlbum):
        """
        @summary: Sets if result of each camitem will
        add to photo album.
        @param addPhotoAlbum: True to add to photo album. 
        """
        self.__addPhotoAlbum__ = addPhotoAlbum
        
    def isAddPhotoAlbum(self):
        """
        @summary: Gets if result of each camitem will
        add to photo album.
        @return: True to add to photo album.
        """
        return self.__addPhotoAlbum__

    def getProjectType (self):
        """
        @summary: Gets IProjectType associated with the core.
        @return: A pycamimg.core.projectType.IProjectType object.
        """
        return self.__projectType__
    
    def getProjectTypeReference (self):
        """
        @summary: Gets IProjectType reference associated with the core.
        @return: A pycamimg.core.projectType.IProjectType reference.
        """
        return self.__projectTypeReference__
        
    def getState(self):
        """
        @summary: Gets state of the execution
        @return: STATE_IDLE, STATE_EXEC or STATE_FINISHED
        """
        return self.__state__
        
    def isSaved (self):
        """
        @summary: Gets if core is saved.
        @return: True when core is just saved.
        """
        return self.__isSaved__
        
    def getFilename (self):
        """
        @summary: Gets filename where project is saved.
        @return: A string with path of file.
        """
        return self.__filename__

    def getTempFolder(self):
        """
        @summary: Gets temporal folder path.
        @return: A string with the temporal folder path.
        """
        return self.__temp__

    def setTempFolder(self, folder):
        """
        @summary: Sets temporal folder path.
        @param folder: Path of the temporal folder. 
        """
        self.__temp__ = folder
    
    def setOrderItemProcess(self, listOrder):
        """
        @summary: Sets list that contains order of processing items.
        @param listOrder: List of strings. 
        """
        self.__orderItemProcess__ = listOrder
        
    def getOrderItemProcess(self):
        """
        @summary: Gets list that contains order of processing items.
        @return: List of strings.
        """
        return self.__orderItemProcess__
    
    def setCallbackEndProcess (self, callback):
        """
        @summary: Sets callback that will be executed when the process ends.
        @param callback: Reference to callback.
        @note: callback must not have any parameter.
        """
        self.__callbackEndProcess__ = callback

    def getCallbackEndProcess (self):
        """
        @summary: Gets callback that will be executed when the process ends.
        @return: Reference to callback. 
        """
        return self.__callbackEndProcess__

    def setCallbackBeginItem (self, callback):
        """
        @summary: Sets callback that will be executed when an item begins to process.
        @param callback: Reference to callback.
        @note: callback must have one parameter that is a CamItem.
        """
        self.__callbackBeginItem__ = callback

    def getCallbackBeginItem (self):
        """
        @summary: Gets callback that will be executed when an item begins to process.
        @return: Reference to callback.
        """
        return self.__callbackBeginItem__

    def setCallbackEndItem (self, callback):
        """
        @summary: Sets callback that will be executed when an item  ends to process.
        @param callback: Reference to callback.
        @note: callback must have one parameter that is a CamItem.
        """
        self.__callbackEndItem__ = callback

    def getCallbackEndItem (self):
        """
        @summary: Gets callback that will be executed when an item ends to process.
        @return: Reference to callback.
        """
        return self.__callbackEndItem__

    def getCurrent(self):
        """
        @summary: Gets current item that core is processing.
        @return: Current CamItem.
        """
        return self.__currentItem__

    def isFinished(self):
        """
        @summary: Gets if core has finished processing items.
        @return: True when process is finished.
        """
        return self.__finished__
        
    def addItem(self, key, item):
        """
        @summary: Add an item in item collection.
        @param key: Key that represents a CamItem.
        @param item: A CamItem object to add.  
        """
        if (self.__items__.has_key(key)):
            __log__.info("It just exists an item with key %s. It will be overwrited" % key)
        self.__items__[key] = item

    def getItems(self):
        """
        @summary: Gets items that core has.
        @return: Dictionary with all item of the core.
        """
        return self.__items__

    def getItem(self, key):
        """
        @summary: Gets an item from a key.
        @return: CamItem object when it can recover item with key. Otherwise return None.
        """
        item = None
        if (self.__items__.has_key(key)):
            item = self.__items__[key]
        else:
            __log__.warning("Key %s does not exist." % key)
        return item

    def removeItem(self, key):
        """
        @summary: Remove an item from dictionary.
        @param key: Key of the item that will remove. 
        """
        if (self.__items__.has_key(key)):
            del self.__items__[key]
        else:
            __log__.warning("Key %s does not exist" % key)

    def getKeys(self):
        """
        @summary: Gets keys of dictionary.
        @return: A list with current keys.
        """
        return self.__items__.keys()

    def reset(self):
        """
        @summary: Reset core process.
        """
        self.__currentKey__ = None
        self.__currentItem__ = None
        self.__finished__ = False
        self.__cancel__ = False

    def process(self):
        """
        @summary: Process all items of the core.
        @return: True if process ran.
        """
        bStart = True
        
        if (self.__threadExec__ != None):
            if (self.__threadExec__.isAlive()):
                __log__.info("Execution thread is just on execution")
                bStart = False
            else:
                del self.__threadExec__
                self.__threadExec__ = None
        if (bStart):
            self.__state__ = STATE_EXEC
            self.__finished__ = False
                
            self.__threadExec__ = Thread(target=self.__process__)
            __log__.debug("Thread of execution project created. %s", self.__threadExec__)
        
            if (self.__projectType__ != None):
                bStart = self.__projectType__.PreDoProject(self, self.getMainWindow())        
            if (bStart):        
                try:
                    self.__threadExec__.start()
                    __log__.debug("Execution thread started. %s", self.__threadExec__)
                except RuntimeException, re:
                    __log__.error("An error occurred when it was starting the thread. %s", re)
                    del self.__threadExec__
                    self.__threadExec__ = None
                    bStart = False
                    self.__finished__ = True
                    self.__state__ = STATE_IDLE
            else:
                self.__finished__ = True
                self.__state__ = STATE_IDLE
                del self.__threadExec__
                self.__threadExec__ = None
                
        return bStart
    
    def cancel(self):
        """
        @summary: Cancel execution of core.
        """ 
        if (self.__threadExec__ != None):
            if (self.__threadExec__.isAlive()):
                try:
                    self.__semaphore__.acquire()
                    self.__cancel__ = True
                    self.__semaphore__.release()
                    __log__.info("Cancel thread signaled.")
                except Exception, e:
                    __log__.error("Thread was not cancel. %s" % e)
                del self.__threadExec__
                self.__threadExec__ = None
                self.__finished__ = False
                self.__state__ = STATE_IDLE
            else:
                __log__.debug("Execution is just finished")
        else:
            __log__.debug("There is not thread")
    
    def save(self, path=None):
        """
        @summary: Saves core in a file.
        @param path: Path where core will store.
        @return: True if everything was be right
        @note: If it is the first time that it saves the core, path must be specified.
               If it is not the firt time and path is not specified, it will save on previous specified path.
        """
        if (CamCore.saveCore(self, path)):
            self.__isSaved__ = True
            self.__filename__ = path
            return True
        
        return False
        
    
    def saveCore(core, path=None):
        """
        @summary: Saves core in a file.
        @param core: Core that will be saved. 
        @param path: Path where core will store.
        @return: True if everything was be right
        @note: If it is the first time that it saves the core, path must be specified.
               If it is not the first time and path is not specified, it will save on previous specified path. 
        """
        bReturn = True
        
        if (path == None):
            __log__.debug("Path is not specified. Get previous path specified.")
            path = core.getFilename()
            if (path == None):
                __log__.debug("Path empty. It can not be possible save core.")
                return False
        
        fo = None
        try:
            fo = open(path, "wb")
        except IOError, e:
            __log__.error("An error has occurred when it was trying to open file %s in write mode. %s" % (path, e))
            fo = None
        
        """
        Do not save temporal folder, because temporal folder path may change.
        currentItem and currentKey do not save, they are temporal variables.
        """    
        if (fo != None):
            try:
                cPickle.dump(core.getName(), fo, PICKLE_PROTOCOL)
                __log__.debug("Name saved. %s" % core.getName())
                
                cPickle.dump(core.isCopy(), fo, PICKLE_PROTOCOL)
                __log__.debug("Copy flag saved. %s" % core.isCopy())
            
                cPickle.dump(core.getProjectTypeReference(), fo, PICKLE_PROTOCOL)
                __log__.debug("ProjectType saved. %s" % core.getProjectTypeReference())
                
                cPickle.dump(len(core.getItems()), fo, PICKLE_PROTOCOL)
                if (len(core.getItems()) > 0):
                    for key, item in core.getItems().iteritems():
                        item.saveItem(fo)
                __log__.debug("Items saved. %s" % core.getItems())
            except IOError, ioe:
                __log__.error("An error has occurred when it was writting the core. %s" % ioe)
                bReturn = False
            except Exception, ex:
                __log__.error("An error has occurred when it was writting the core. %s" % ex)
                bReturn = False
            finally:
                fo.close()
                __log__.debug("Close file %s" % path)
        else:
            bReturn = False
        
        return bReturn

    saveCore = staticmethod(saveCore)

    def load(path, tempFolder=None):
        """
        @summary: Loads core from a file.
        @param path: Path where core are stored.
        @param tempFolder: Temporal foldet that will assign to core.
        @return: CamCore loaded if load process is ok. Otherwise None.  
        """
        fi = None
        try:
            fi = open(path, "rb")
        except IOError, e:
            __log__.error("An error has occurred when it was trying to open file %s in read mode. %s" % (path, e))
            fi = None

        if (fi != None):
            build = True
            try:
                name = cPickle.load(fi)
                __log__.debug("Name loaded. %s" % name)
                isCopy = cPickle.load(fi)
                __log__.debug("Copy flag loaded. %s" % isCopy)
                
                projectType = cPickle.load(fi)
                __log__.debug("ProjectType loaded. %s" % projectType)
                
                items = {}
                nItems = cPickle.load(fi)
                while (nItems > 0):
                    item = CamItem.load(fi)
                    items[item.getPath()] = item
                    nItems -= 1
                
                __log__.debug("Items loaded. %s" % items)
            except Exception, e:
                print e
                build = False
            finally:
                fi.close()
                __log__.debug("Close file %s" % path)
            
            if(build):
                core = CamCore(temp=tempFolder, isCopy=isCopy, projectType=projectType)
                core.setName(name)
                core.__items__ = items
                core.__filename__ = path
                core.__isSaved__ = True
                
                __log__.info("Core created. %s" % core)
                
                return core
            else:
                __log__.info("There were errors on load process")
            
        return None
    
    load = staticmethod(load)
            
if __name__ == "__main__":
    print "Testing module..."
