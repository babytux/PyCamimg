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

import threading, thread
from threading import Thread
from threading import Semaphore
import os.path
import time 

import IOUtils

class DirectoryMonitor:
    """
    @summary: Class that is watching in a directory to see any change.
    """

    WAIT_TIME = 3000
    # Types
    DIRECTORY = 0
    FILE = 1
    # Operations
    ADD = 0
    DELETE = 1
    
    def __init__(self, directory):
        """
        @summary: Create new DirectoryMonitor.
        @param directory: Directory to watch. 
        """
        self.__directory__ = directory
        self.__utils__ = IOUtils.IOUtils()
        self.__seeFiles__ = False
        self.__seeHiddens__ = True
        self.__signalStop__ = False
        self.__semaphore__ = Semaphore()
        self.__directories__ = []
        self.__files__ = []
        self.__listeners__ = []
        self.__thread__ = None
        
        __log__.debug("DirectoryMonitor created to %s" % directory)
        
    def __raiseEvent__(self, path, operation, type):
        """
        @summary: Raise event, when it detects new file or directory.
        @param path: Path of the event.
        @param operation: Operation that occurs.
        @param type: Type of path. Directory or File.   
        """
        for listener in self.__listeners__:
            listener(path, operation, type)

    def __doLoop__(self):
        """
        @summary: Do the loop of monitor.
        """
        while (True):
            bContinue = True
            # Wait time 
            time.sleep(self.WAIT_TIME / 1000)
            
            # Checks if signal stop is set
            self.__semaphore__.acquire()
            if (self.__signalStop__):
                bContinue = False
            self.__semaphore__.release()
            
            if (bContinue):
                # Checks new directories
                directories = self.__utils__.getDirectories(self.__directory__,
                                                            showhidden=self.__seeHiddens__)
                if (len(self.__directories__) == 0):
                    self.__directories__ = directories
                    if (directories != None):
                        for direc in directories:
                            self.__raiseEvent__(os.path.join(self.__directory__, direc),
                                                self.ADD,
                                                self.DIRECTORY)
                else:
                    if (directories != None):
                        for direc in self.__directories__:
                            if (directories.count(direc) == 0):
                                # If a directory isn't in new directory list, then the directory
                                # is deleted
                                self.__directories__.remove(direc)
                                self.__raiseEvent__(os.path.join(self.__directory__, direc),
                                                    self.DELETE,
                                                    self.DIRECTORY)
                                
                        for direc in directories:
                            if (self.__directories__.count(direc) == 0):
                                self.__directories__.append(direc)
                                self.__raiseEvent__(os.path.join(self.__directory__, direc),
                                                    self.ADD,
                                                    self.DIRECTORY)
                    else:
                        for direc in self.__directories__:
                            self.__directories__.remove(direc)
                            self.__raiseEvent__(os.path.join(self.__directory__, direc),
                                                self.DELETE,
                                                self.DIRECTORY)
                            
                if (self.__seeFiles__):
                    files = self.__utils__.getFiles(self.__directory__,
                                                    showhidden=self.__seeHiddens__)
                    if (len(self.__files__) == 0):
                        self.__files__ = files
                        
                        if (files != None):
                            for file in files:
                                self.__raiseEvent__(os.path.join(self.__directory__, file),
                                                    self.ADD,
                                                    self.FILE)
                    else:
                        if (files != None):
                            for file in self.__files__:
                                if (files.count(file) == 0):
                                    self.__files__.remove(file)
                                    self.__raiseEvent__(os.path.join(self.__directory__, file),
                                                        self.DELETE,
                                                        self.FILE)
                            for file in files:
                                if (self.__files__.count(file) == 0):
                                    self.__files__.append(file)
                                    self.__raiseEvent__(os.path.join(self.__directory__, file),
                                                        self.ADD,
                                                        self.FILE)
                        else:
                            for file in self.__files__:
                                self.__files__.remove(file)
                                self.__raiseEvent__(os.path.join(self.__directory__, file),
                                                    self.DELETE,
                                                    self.FILE)
                
            else:
                self.__signalStop__ = False
                break
        
    def addListener(self, callback):
        """
        @summary: Add a listener. 
        @param callback:  callback that must have as parameters, path , type.
        """
        if (self.__listeners__.count(callback) == 0):
            self.__listeners__.append(callback)
            
    def removeListener(self, callback):
        """
        @summary: Remove a listener from the list.
        @param callback:  callback to remove.
        """
        if (self.__listeners__.count(callback) != 0):
            self.__listeners__.remove(callback)
            
    def addDirectories(self, directories):
        """
        @summary: Add directories to monitor.
        @param directories: List with directories to add to its list. 
        """
        for directory in directories:
            if (self.__directories__.count(directory) == 0):
                self.__directories__.append(directory)
    
    def addFiles(self, files):
        """
        @summary: Add files to monitor.
        @param files: List with files to add to its list.
        """
        for file in files:
            if (self.__files__.count(file) == 0):
                self.__files__.append(file)
    
    def clearFiles(self):
        """
        @summary: Remove all files from cache.
        """
        while (len(self.__files__) > 0):
            self.__files__.pop()
    
    def setHiddensVisibility(self, seeHiddens):
        """
        @summary: Sets if hiddens are visible.
        @param seeHiddens: True to check hidden files and directories. 
        """
        self.__seeHiddens__ = seeHiddens
    
    def getHiddensVisibility(self):
        """
        @summary: Gets if hiddens are visible.
        @return: True if it is checking hidden files and directories.
        """
        return self.__seeHiddens__
    
    def setSeeFiles(self, seeFiles):
        """
        @summary: Sets if the monitor must watch file changes.
        @param seeFile: True to check files too. 
        """ 
        self.__seeFiles__ = seeFiles
        
    def getSeeFiles(self):
        """
        @summary: Gets if the monitor must watch files changes.
        @return: True if monitor is watching files too.
        """
        return self.__seeFiles__
        
    def start(self):
        """
        @summary: Starts monitoring.
        """
        if (self.__thread__ == None):
            self.__thread__ = Thread(target=self.__doLoop__, args=())
            self.__thread__.start()
    
    def stop(self, timeout=0, checkListeners=True):
        """
        @summary: Stops monitoring.
        @param timeout: time to wait the end of the monitor. Default 0.
        @param checkListeners: True to check if there is other listeners. Default True.   
        """
        if (checkListeners and (len(self.__listeners__) > 1)):
            return None
        
        self.__semaphore__.acquire()
        self.__signalStop__ = True
        self.__semaphore__.release()
        
        if (self.__thread__ != None):
            self.__thread__.join(timeout)
            
        self.__thread__ = None
