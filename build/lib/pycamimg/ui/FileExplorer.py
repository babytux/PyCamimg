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
import os, os.path
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

import threading, thread
from threading import Thread
from threading import Semaphore
import time
import urllib
from datetime import datetime

try:
    import gtk, gobject
except ImportError, ie:
    __log__.fatal("It can not import gtk, gdk modules. Sure you have installed pygtk?" )
    raise ie

import UIUtils
import FactoryControls
from MimeInfo import MimeInfo
from pycamimg.util import FactoryDirectoryMonitor
from pycamimg.util.DirectoryMonitor import DirectoryMonitor
from pycamimg.util.IOUtils import IOUtils

class FileExplorer:
    """
    @summary: This class is a handler for a TreeView for simulating a
    file explorer, like nautilus has.
    """
    
    #Index of each column
    __IMG_COLUMN__ = 0
    __NAME_COLUMN__ = 1
    __PATH_COLUMN__ = 2
    __SIZE_COLUMN__ = 3
    __SIZE_DESC_COLUMN__ = 4
    __TYPE_COLUMN__ = 5
    __TYPE_DESC_COLUMN__ = 6
    __MODIFY_DATE_COLUMN__ = 7
    __MODIFY_DATE_DESC_COLUMN__ = 8
    
    #Separator for splitting drag&drop selection
    SEP = "\n"
    #ID of data for drag&drop
    TARGET_TEXT = 80
    #Type of drag&drop
    FROM_TEXT = [("text/uri-list", 0, TARGET_TEXT)]
    
    def __init__(self, showHiddens = True):
        """
        @summary: Create a file explorer.
        @param showHiddens: True if you show hidden files. Default True
        """
        self.__monitor__ = None
        self.__currentPathLoading__ = None
        self.__currentPath__ = None
        self.__semaphore__ = Semaphore()
        self.__factoryIcons__ = MimeInfo()
        self.__ioUtils__ = IOUtils()
        
        self.__explorer__ = gtk.TreeView()
        self.__explorer__.connect("drag-data-get", self.__dragDataGetEvent__)
        self.__explorer__.connect("row-activated", self.__enterDirectory__)
        
        self.__exportControl__ = gtk.ScrolledWindow()
        self.__exportControl__.add(self.__explorer__)
        
        # Callbacks of events
        self.__cEnterDirCallback__ = None
        self.__cEndLoadCallback__ = None
        self.__cBeginLoadCallback__ = None
        
        # Store current thread
        self.__loadThread__ = None
        
        #Initialize file explorer
        self.__initializeFiles__()
        
        self.__showHiddens__ = showHiddens        
    
    def __initializeFiles__(self):
        """
        @summary: Initialize ListView of files.
        """
        self.__flModel__ = self.__getModel__()
        
        self.__explorer__.set_model(self.__flModel__)
        self.__explorer__.set_headers_visible(True)
        self.__explorer__.set_show_expanders(False)
        self.__explorer__.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        __log__.debug("Applied settings to file explorer")
        
        # Creates columns of the TreeView of Files
        column = FactoryControls.getTreeColumnTextAndPixbuf(_("Name"), self.__NAME_COLUMN__, self.__IMG_COLUMN__)
        self.__explorer__.append_column(column)
        columnSize = FactoryControls.getTreeColumnText(_("Size"), self.__SIZE_DESC_COLUMN__)
        self.__explorer__.append_column(columnSize)
        columnType = FactoryControls.getTreeColumnText(_("Type"), self.__TYPE_DESC_COLUMN__)
        self.__explorer__.append_column(columnType)
        columnModify = FactoryControls.getTreeColumnText(_("Modify Date"), self.__MODIFY_DATE_DESC_COLUMN__)
        self.__explorer__.append_column(columnModify)

        __log__.debug("Columns added")

        # Enabled as drag source
        self.__explorer__.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, 
                                                  self.FROM_TEXT, 
                                                  gtk.gdk.ACTION_COPY)

        __log__.debug("Drag & Drop enabled")

    
    def __getModel__ (self):
        """
        @summary: Gets list model of the file explorer.
        @return: gtk.ListStore with model.
        """
        list = gtk.ListStore(gtk.gdk.Pixbuf, 
                             gobject.TYPE_STRING, 
                             gobject.TYPE_STRING,
                             gobject.TYPE_LONG,
                             gobject.TYPE_STRING,
                             gobject.TYPE_STRING,
                             gobject.TYPE_STRING,
                             gobject.TYPE_LONG,
                             gobject.TYPE_STRING)
        list.set_sort_func(self.__IMG_COLUMN__, self.__sort__, self.__IMG_COLUMN__)
        list.set_sort_func(self.__NAME_COLUMN__, self.__sort__, self.__NAME_COLUMN__)
        list.set_sort_func(self.__PATH_COLUMN__, self.__sort__, self.__PATH_COLUMN__)
        list.set_sort_func(self.__SIZE_COLUMN__, self.__sort__, self.__SIZE_COLUMN__)
        list.set_sort_func(self.__SIZE_DESC_COLUMN__, self.__sort__, self.__SIZE_DESC_COLUMN__)
        list.set_sort_func(self.__TYPE_COLUMN__, self.__sort__, self.__TYPE_COLUMN__)
        list.set_sort_func(self.__TYPE_DESC_COLUMN__, self.__sort__, self.__TYPE_DESC_COLUMN__)
        list.set_sort_func(self.__MODIFY_DATE_COLUMN__, self.__sort__, self.__MODIFY_DATE_COLUMN__)
        list.set_sort_func(self.__MODIFY_DATE_DESC_COLUMN__, self.__sort__, self.__MODIFY_DATE_DESC_COLUMN__)
        
        list.set_sort_column_id(self.__PATH_COLUMN__, gtk.SORT_ASCENDING)
        
        return list
        
    
    def __handlerDirectoryMonitorEvents__(self, path, operation, type):
        """
        @summary: Handle events from directory monitors.
        @param path: Directory or file that was created, deleted or moved.
        @param operation: Type of event that occurred.
        @param type: If event occurred on a directory or a file.
        """
        if (operation == DirectoryMonitor.ADD):
            __log__.debug("Directory added. %s" % path)
            head, name = os.path.split(path)
            if (self.__checkCurrentPath__(head)):
                icon = self.__factoryIcons__.getIcon(path)
                if (icon == None):
                    icon = FactoryControls.getPixbufFromStock(gtk.STOCK_FILE)
                self.addItem(name, path, icon)
            else:
                __log__.debug("Directory Monitor Action from another monitor. %s" , head)
        elif (operation == DirectoryMonitor.DELETE):
            __log__.debug("Directory deleted. %s" % path)
            head, name = os.path.split(path)
            if (self.__checkCurrentPath__(head)):
                iter = self.getIterFromFilepath(path)
                if (iter != None):
                    self.deleteNode(iter)
            else:
                __log__.debug("Directory Monitor Action from another monitor. %s" , head)
    
    def __checkCurrentPath__(self, path):
       """
       @summary: Checks if current path is path.
       @return: True if path is current path.
       """
       bReturn = False
       self.__semaphore__.acquire()
       bReturn = (self.__currentPathLoading__ == path)
       self.__semaphore__.release()
       return bReturn
   

    def __setCurrentPath__(self, path):
       """
       @summary: Sets a path as current path.
       @param path: Path to set as current path. 
       """
       self.__semaphore__.acquire()
       self.__currentPathLoading__ = path
       self.__semaphore__.release()
    
    def __fillFiles__(self, path):
        """
        @summary: Fills ListView files with current directory files.
        @param path: Path to list.
        """

        #Create a temporal model
        if (self.__cBeginLoadCallback__ != None):
            self.__cBeginLoadCallback__()
        
        tupleSort = self.__flModel__.get_sort_column_id()
        if (tupleSort == None):
            tupleSort = (-1, gtk.SORT_ASCENDING)
        elif (tupleSort[0] == None):
            tupleSort = (-1, gtk.SORT_ASCENDING)
        
        UIUtils.setNotifyChildTreeview(self.__explorer__, False)

        if (self.__monitor__ != None):
            __log__.debug("Stopping file monitor.")
            self.__monitor__.stop()
            self.__monitor__.removeListener(self.__handlerDirectoryMonitorEvents__)
            self.__monitor__.setSeeFiles(False)
            self.__monitor__.clearFiles()
            self.__monitor__ = None

        # Get monitor of the path
        self.__monitor__ = FactoryDirectoryMonitor.getMonitor(path)
        
        #Clear every iters in TreeView
        if (self.__checkCurrentPath__(path)):
            UIUtils.clearModelTreeview(self.__flModel__, True)
            __log__.debug("Cleared previous model")
            UIUtils.setColumnOrder(self.__flModel__, -2, gtk.SORT_ASCENDING)
        else:
            UIUtils.setNotifyChildTreeview(self.__explorer__, True)
            if (self.__cEndLoadCallback__ != None):
                self.__cEndLoadCallback__()
            UIUtils.setColumnOrder(self.__flModel__, tupleSort[0], order = tupleSort[1])
            return False
        
        # Gets folders and files of current path
        folders = self.__ioUtils__.getDirectories(path, showhidden=self.__showHiddens__)
        files = self.__ioUtils__.getFiles(path, showhidden=self.__showHiddens__)
        
        
        if (folders != None):
            if (self.__checkCurrentPath__(path)):
                __log__.debug("Adding directories to new model.")
                self.__monitor__.addDirectories(folders)
                iconFolder = FactoryControls.getPixbufFromStock(gtk.STOCK_DIRECTORY)
                
                for folder in folders:
                    folderPath = os.path.join(path, folder)
                    self.addItem(folder, folderPath, iconFolder, async=True)
            else:
                UIUtils.setNotifyChildTreeview(self.__explorer__, True)
                if (self.__cEndLoadCallback__ != None):
                    self.__cEndLoadCallback__()
                    #UIUtils.clearImage(self.__loadControl__)
                UIUtils.setColumnOrder(self.__flModel__, tupleSort[0], order = tupleSort[1])
                return False
                

        if (files != None):
            if (self.__checkCurrentPath__(path)):
                __log__.debug("Adding files to new model.")
                self.__monitor__.addFiles(files)
            
                for file in files:
                    filePath = os.path.join(path, file)
                    icon = self.__factoryIcons__.getIcon(filePath)
                    if (icon == None):
                        icon = FactoryControls.getPixbufFromStock(gtk.STOCK_FILE)
                    self.addItem(file, filePath, icon, async=True)
            else:
                UIUtils.setNotifyChildTreeview(self.__explorer__, True)
                if (self.__cEndLoadCallback__ != None):
                    self.__cEndLoadCallback__()
                    #UIUtils.clearImage(self.__loadControl__)
                UIUtils.setColumnOrder(self.__flModel__, tupleSort[0], order = tupleSort[1])
                return False

        UIUtils.setNotifyChildTreeview(self.__explorer__, True)
        
        if (self.__checkCurrentPath__(path)):
            # Set and active current monitor
            if (self.__monitor__ != None):
                __log__.debug("Activating file monitor...")
                self.__monitor__.setSeeFiles(True)
                self.__monitor__.addListener(self.__handlerDirectoryMonitorEvents__)
                self.__monitor__.start()
        else:
            __log__.debug("Stopping file monitor...")
            self.__monitor__.stop()
            self.__monitor__.removeListener(self.__handlerDirectoryMonitorEvents__)
            self.__monitor__.setSeeFiles(False)
            self.__monitor__.clearFiles()
            self.__monitor__ = None
        
        if (self.__cEndLoadCallback__ != None):
            self.__cEndLoadCallback__()
            
        UIUtils.setColumnOrder(self.__flModel__, tupleSort[0], order = tupleSort[1])

        return False

    def __sort__(self, model, iter1, iter2, column):
        """
        @summary: sort compare function.
        @param model: ListStore of FileExplorer.
        @param iter1: First item to compare.
        @param iter2: Second item to compare.
        @param column: Order by column.    
        """
        path1 = model.get_value(iter1, self.__PATH_COLUMN__)
        path2 = model.get_value(iter2, self.__PATH_COLUMN__)
        
        if ((path1 == None) and (path2 != None)):
            return -1
        if ((path1 != None) and (path2 == None)):
            return 1
        if ((path1 == None) and (path2 == None)):
            return 0
        
        if (path1 == _("Loading...")):
            return -1
        elif (path2 == _("Loading...")):
            return 1
        
        if (os.path.isdir(path1) and not os.path.isdir(path2)):
            return -1
        if (os.path.isdir(path2) and not os.path.isdir(path1)):
            return 1
        
        if ((column == self.__IMG_COLUMN__) or 
            (column == self.__NAME_COLUMN__) or 
            (column == self.__PATH_COLUMN__)):
            return self.__pathComparer__(path1, path2)
        elif((column == self.__SIZE_COLUMN__) or (column == self.__SIZE_DESC_COLUMN__)):
            size1 = model.get_value(iter1, self.__SIZE_COLUMN__)
            size2 = model.get_value(iter2, self.__SIZE_COLUMN__)
            if (size1 > size2):
                return 1
            elif (size1 < size2):
                return -1
            return 0
        elif ((column == self.__TYPE_COLUMN__) or (column == self.__TYPE_DESC_COLUMN__)):
            type1 = model.get_value(iter1, self.__TYPE_DESC_COLUMN__)
            type2 = model.get_value(iter2, self.__TYPE_DESC_COLUMN__)
            if (type1 > type2):
                return 1
            elif (type1 < type2):
                return -1
            return 0
        elif ((column == self.__MODIFY_DATE_COLUMN__) or (column == self.__MODIFY_DATE_DESC_COLUMN__)):
            date1 = model.get_value(iter1, self.__MODIFY_DATE_COLUMN__)
            date2 = model.get_value(iter2, self.__MODIFY_DATE_COLUMN__)
            if (date1 > date2):
                return 1
            elif (date1 < date2):
                return -1
            return 0
        
        return 0
            

    def __pathComparer__(self, path1, path2):
        """
        @summary: Compare two paths.
        @param path1: Path to compare.
        @param path2: Path to compare.
        @return: -1 when path1 is less than path2, 
                0 when path1 is equals than path2,
                1 when path 1 is greater than path2
        """
        if (path1 == _("Loading...")):
            return -1
        elif (path2 == _("Loading...")):
            return 1
        
        if (os.path.isdir(path1) and not os.path.isdir(path2)):
            return -1
        if (os.path.isdir(path2) and not os.path.isdir(path1)):
            return 1
        
        path1cmp = path1.lower()
        path2cmp = path2.lower()
        
        if (path1cmp > path2cmp):
            return 1
        elif (path1cmp < path2cmp):
            return -1
        return 0
    
    def __enterDirectory__ (self, treeview, path, column):
        """
        @summary: Event that raises when enter in a directory.
        @param treeview: Treeview where event was occurred. 
        @param path: GtkTreePath selected.
        @param column: Column selected. 
        """
        filePath = self.getFilepathFromPath(path)
        self.applyPath(filePath)
        if (self.__cEnterDirCallback__ != None):
            self.__cEnterDirCallback__(filePath)
        
    
    def __dragDataGetEvent__ (self, treeview, context, selection, info, timestamp):
        """
        @summary: Puts selected files in the selection of drag&drop.
        @param treeview: Treeview where event was occurred. 
        @param context: Context of drag&drop.
        @param selection: Selection of drag&drop.
        @param info: Information of drag&drop.
        @param timestamp: Timestamp when drag&drop occurred.
        """
        treeselection = self.__explorer__.get_selection()
        model, paths = treeselection.get_selected_rows()
        files = []
        for path in paths:
            # Add selected files from files TreeView
            iter = model.get_iter(path)
            text = model.get_value(iter, self.__PATH_COLUMN__)
            files.append("file://%s" % urllib.pathname2url(text))

        selection.set_uris(files)
    
    #PUBLIC METHODS
    def setEnterDirectoryCallback(self, callback):
        """
        @summary: Sets callback that will be executed when it enter in a directory.
        @param callback: Callback with that format. callback(path : string) 
        """
        self.__cEnterDirCallback__ = callback
        
    def setBeginLoadCallback(self, callback):
        """
        @summary: Sets callback that will be executed when it will be loading a directory.
        @param callback: Callback with that format. callback()
        """
        self.__cBeginLoadCallback__ = callback
        
    def setEndLoadCallback(self, callback):
        """
        @summary: Sets callback that will be executed when loading of a directory ends.
        @param callback: Callback with that format. callback()
        """
        self.__cEndLoadCallback__ = callback
    
    def getControl(self):
        """
        @summary: Gets FileExplorer control.
        @return: gtk.ScrollWindow.
        """
        return self.__exportControl__
    
    def addItem (self, name, fullpath, icon, async=True):
        """
        @summary: Add an item on navigator.
        @param name: Name of the new item.
        @param fullpath: Full path of the new item
        @param icon: Icon that will be associated with item.
        @param async: True to add asynchronous. Default value is True.
        @return: New iter inserted. 
        """
        size = 0
        sizeDescription = ""
        modify = 0
        modifyDescription = ""
        mimeType = ""
        mimeTypeDescription = ""
                
        size, sizeDescription = self.__factoryIcons__.getSize(fullpath)
        __log__.debug("Gets size of %s: %d bytes" %(fullpath, size))
        mimeType, mimeTypeDescription = self.__factoryIcons__.getMime(fullpath)
        __log__.debug("Gets mime of %s: %s" %(fullpath, mimeTypeDescription))
        modify, modifyDescription = self.__factoryIcons__.getModifyDate(fullpath)
        __log__.debug("Gets modify date of %s: %s" %(fullpath, modifyDescription))
        
        return UIUtils.addIterListView(self.__flModel__, (icon, name, fullpath, 
                                                          size, sizeDescription, 
                                                          mimeType, mimeTypeDescription, 
                                                          modify, modifyDescription), doGObject=async)
    
    def deleteNode (self, iter, glock=True):
        """
        @summary: Delete an iter from treeview.
        @param iter: Iter to delete from the file explorer.
        @param glock: True to produce a gtk lock into gtk loop.  
        """
        UIUtils.deleteIter(self.__flModel__, iter, glock)
    
    def applyPath(self, path):
        """
        @summary: Apply path on file explorer.
        @param path: Path to apply. 
        """
        bThrowThread = True
        if (self.__checkCurrentPath__(path)):
            bThrowThread = False
        
        if (bThrowThread):
            self.__setCurrentPath__(path)
            
        if (bThrowThread):
            self.__loadThread__ = Thread(target=self.__fillFiles__, args=(path, ))
            self.__loadThread__.start()
        
    def getSelectedFiles(self):
        """
        @summary: Gets selected iters.
        @return: A list of paths that are selected.
        """
        treeselection = self.__explorer__.get_selection()
        model, paths = treeselection.get_selected_rows()
        files = []
        for path in paths:
            # Add selected files from files TreeView
            iter = model.get_iter(path)
            text = model.get_value(iter, self.__PATH_COLUMN__)
            files.append(text)
        
        return files
    
    def getIterFromFilepath(self, filepath):
        """
        @summary: Gets an iter from a file path.
        @param filepath: Path to search. 
        @return: An iter that match with file path. 
            If filepath does not exist, return None.
        """
        iter = self.__flModel__.get_iter_first()
        
        while (iter != None):
            value = self.__flModel__.get_value(iter, self.__PATH_COLUMN__)
            if (value == filepath):
                return iter
            iter = self.__flModel__.iter_next(iter)
        __log__.debug("Path %s has not found." % filepath)
        return None
    
    def getFilepathFromPath(self, path):
        """
        @summary: Gets a filepath from a path of a treenode.
        @param path: TreePath to search in file explorer.
        @return: string with filepath found. None if it has not found. 
        """
        iter = self.__flModel__.get_iter(path)
        sPath = None
        if (iter != None):
            sPath = self.__flModel__.get_value(iter, self.__PATH_COLUMN__)
        
        return sPath
        
        