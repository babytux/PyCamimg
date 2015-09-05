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

import os, os.path

try:
    import pygtk
    if (not (sys.platform == "win32")):
        pygtk.require('2.0')
    import gtk, gobject
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

import threading, thread
from threading import Thread
import time

import UIUtils
import FactoryControls
from pycamimg.util import FactoryDirectoryMonitor
from pycamimg.util.DirectoryMonitor import DirectoryMonitor
from pycamimg.util.IOUtils import IOUtils

class TreeExplorer:
    """
    @summary: This class is a handler for a TreeView, for
        simulating a tree explorer, like nautilus has.
    """
    
    __selectCallback__ = None
    __showHiddens__ = True

    __TEMP_NODE__ = " !TempCamimg"    
    
    # Index of each column
    __IMG_COLUMN__ = 0
    __NAME_COLUMN__ = 1
    __PATH_COLUMN__ = 2
    
    def __init__(self, selectCallback=None, showHiddens=True):
        """
        @summary: Create new TreeExplorer.
        @param selectCallback: Callback that will call when an item will be selected.
        @param showHiddens: True to show hidden folders.
        @note: selectCallback must be a funtion reference, like function(path : str)
        """
        self.__selectedPath__ = ""
        self.__ioUtils__ = IOUtils()

        # Define Treeview explorer
        self.__explorer__ = gtk.TreeView()
        self.__explorer__.connect("cursor-changed", self.__selectRowTvOneClickSignal__)
        self.__explorer__.connect("row-collapsed", self.__collapsedRowTVSignal__)
        self.__explorer__.connect("row-expanded", self.__expandRowTVSignal__)
        
        self.__exportControl__ = gtk.ScrolledWindow()
        self.__exportControl__.add(self.__explorer__)
        
        self.__HOME_NODE__ = _("home")
        
        # Initialize TreeView explorer
        self.__initializeExplorer__()
        
        self.__selectCallback__ = selectCallback
        self.__showHiddens__ = showHiddens
    
    def __initializeExplorer__(self):
        """
        @summary: Initialize TreeView explorer. Add drives of OS.
        """
        # Make a model for TreeView explorer
        self.__model__ = gtk.TreeStore(gtk.gdk.Pixbuf,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_STRING)
        
        __log__.debug("Created model for TreeExplorer.")
        # Gets home icon
        iconHome = FactoryControls.getPixbufFromStock(gtk.STOCK_HOME)
        
        # Gets drive icon
        icon = FactoryControls.getPixbufFromStock(gtk.STOCK_HARDDISK)
    
        self.__explorer__.set_model(None)
    
        # Apply look to TreeView
        self.__explorer__.set_headers_visible(False)
        self.__explorer__.set_show_expanders(True)
        self.__explorer__.get_selection().set_mode(gtk.SELECTION_SINGLE)
    
        column = FactoryControls.getTreeColumnTextAndPixbuf(_("Explorer"),
                                                            self.__NAME_COLUMN__,
                                                            self.__IMG_COLUMN__)
        self.__explorer__.append_column(column)
    
        __log__.debug("Added columns to TreeExplorer")
        
        # Add home node
        self.addDirectory(self.__HOME_NODE__, os.path.expanduser("~"), iconHome, glock=False)
        
        # Gets drives from the OS
        for sDrive in self.__ioUtils__.getDrives():
            if (sDrive != None) and (sDrive != ""):
                self.addDirectory (sDrive, sDrive, icon, glock=False)
        
        __log__.debug("Drives added.")
        
        # Set model to explorer TreeView
        self.__explorer__.set_model(self.__model__)
     
    def __fillDirectory__(self, path):
        """
        @summary: Fills a node with sub-directories.
        @param path: Folder path to fill. 
        """
        newExpand = False
        # Gets current path
        iter = self.__model__.get_iter(path)
        sPath = self.__model__.get_value(iter, self.__PATH_COLUMN__)
        
        monitor = FactoryDirectoryMonitor.getMonitor(sPath)
        
        # Checks if first child y a temporal node. If it is, it must be removed
        itFirstChild = self.__model__.iter_children(iter)
        if (itFirstChild != None):
            if (self.__model__.get_value(itFirstChild, self.__PATH_COLUMN__) == self.__TEMP_NODE__):
                # Gets number of nodes. If nNodes > 1, 
                # there is another thread that is loading the directory 
                nNodes = self.__model__.iter_n_children(iter)
                if (nNodes > 1):
                    return
                newExpand = True
        else:
            __log__.warning("It can not get first child of %s" % sPath)
    
        # Gets directories of the path
        lDirectories = self.__ioUtils__.getDirectories(sPath,
                                                       showhidden=self.__showHiddens__)
    
        if (lDirectories != None):
            icon = FactoryControls.getPixbufFromStock(gtk.STOCK_DIRECTORY)
                
            if (not newExpand):
                __log__.debug("It is not a new expand. Checking directories...")
                
                iterStep = self.__model__.iter_children(iter)
                # Find deleted iters
                while (iterStep != None):
                    doStep = True
                    sDirFind = self.__model__.get_value(iterStep, self.__NAME_COLUMN__)
                    if (sDirFind != None):
                        try:
                            index = lDirectories.index(sDirFind)
                        except ValueError, ve:
                            __log__.debug("It can not get index of %s. %s" % (sDirFind, ve))
                            index = -1
                        if (index == -1):
                            # In case of directory does not exist, it will remove from treeview
                            iterDelete = iterStep
                            iterStep = self.__model__.iter_next(iterStep)
                            self.deleteNode(iterDelete)
                            __log__.debug("Delete node %s" % sDirFind)
                            
                            doStep = False
                        else:
                            # In case of directory just exists, it will remove from list
                            lDirectories.remove(sDirFind)
                            __log__.debug("%s skipped" % sDirFind)
        
                    if (doStep):
                        iterStep = self.__model__.iter_next(iterStep)
                
                # Check directories in the list 
                for sDir in lDirectories:
                    sFullPath = os.path.join(sPath, sDir)
                    checkIter = self.__findDirectoryOnParent__(iter, sDir)
                    if (checkIter == None):
                        self.addDirectory(sDir, sFullPath, icon, iter)
                        __log__.debug("Add %s" % sFullPath)
            
            # Insert directories
            for sDir in lDirectories:
                sFullPath = os.path.join(sPath, sDir)
                self.addDirectory(sDir, sFullPath, icon, iter)
                __log__.debug("Add %s" % sFullPath)
                    
            if ((itFirstChild != None) and newExpand):
                __log__.debug("Remove temporal node.")
                self.deleteNode(itFirstChild)
                
            monitor.addDirectories(lDirectories)
            monitor.addListener(self.__handlerDirectoryMonitorEvents__)
            
        else:  # When there isn't any directory
            iterStep = self.__model__.iter_children(iter)
            # Find delete all child 
            while (iterStep != None):
                self.deleteNode(iterStep)
        
        monitor.start()
    
    def __findDirectoryOnParent__ (self, iterParent, dirname):
        """
        @summary: Find direcotory in a iter.
        @param iterParent: Tree where it will find.
        @param dirname:  Name of directory to find.
        @return: TreeIter if dirname exists in iterParent, 
            or None if dirname doesn't exist
        """
        iter = None
        
        if (iterParent != None):
            if (self.__model__.iter_has_child(iterParent)):
                iter = self.__model__.iter_children(iterParent)
        else:
            iter = self.__model__.get_iter_first()
        
        while (iter != None):
            value = self.__model__.get_value(iter, self.__NAME_COLUMN__)
            if (value == dirname):
                return iter
            iter = self.__model__.iter_next(iter)
        return None
    
    def __prepareDirectory__(self, directory, iter, glock=True):
        """
        @summary: Checks if a directory has some directory. 
            In truth case, add a temporal subitem.
        @param directory: Directory to prepare.
        @param iter: TreeIter of the directory.
        @param glock: True to lock gtk-loop.  
        """
        sSubDirs = self.__ioUtils__.getDirectories(directory)
        if (sSubDirs != None) and (len(sSubDirs) > 0):
                UIUtils.addIter(self.__model__,
                                iter,
                                (FactoryControls.getPixbufFromStock(gtk.STOCK_EXECUTE) ,
                                 _("Loading..."),
                                 self.__TEMP_NODE__
                                ),
                                glock
                            )
    
    def __expandPath__ (self, path, select):
        """
        @summary: Expand a path on navigator TreeView.
        @param path: Path to expand.
        @param select: True to select TreeIter.  
        """
        head, dir = os.path.split(path)
        iter = None
        
        if (path == os.path.expanduser("~")):
            __log__.debug("Expanding home directory...")
            iter = self.__findDirectoryOnParent__(None, self.__HOME_NODE__)
        elif(head == path):
            # If head is equal path, path is a drive or mount point
            iter = self.__findDirectoryOnParent__(None, head)

        if (iter == None):
            iterparent = self.__expandPath__ (head, False)
            if (iterparent != None):
                iter = self.__findDirectoryOnParent__ (iterparent, dir)

        if (iter != None):
            treepath = self.__model__.get_path(iter)
            self.__fillDirectory__(treepath)
            if (select):
                UIUtils.expandTreeview(self.__explorer__, treepath)

                selection = self.__explorer__.get_selection()
                selection.select_path(treepath)
                
                UIUtils.scrollTreeviewToPath(self.__explorer__, treepath)
                
        return iter
    
    def __getIterFromPath__(self, path):
        """
        @summary: Gets an iter from a path.
        @param path: Path to find its TreeIter.
        @return: TreeIter of the path. None when TreeIter has not found. 
        """
        head, dir = os.path.split(path)
        iter = None
        # If head is equal path, path is a drive or mount point
        if (head == path):
            return self.__findDirectoryOnParent__(None, head)
        else:
            iterparent = self.__getIterFromPath__(head)
            if (iterparent != None):
                return self.__findDirectoryOnParent__(iterparent, dir)
     
    def __handlerDirectoryMonitorEvents__(self, path, operation, type):
        """
        @summary: Handle events from directory monitors.
        @param path: Path of the event.
        @param operation: Operation that occurred.
        @param type: Type of path. Directory or File. 
        """
        if (type == DirectoryMonitor.DIRECTORY):
            if (operation == DirectoryMonitor.ADD):
                head, dirname = os.path.split(path)
                iter = self.__getIterFromPath__(head)
                if (iter != None):
                    icon = FactoryControls.getPixbufFromStock(gtk.STOCK_DIRECTORY)
                    self.addDirectory(dirname, path, icon, iter)
            elif (operation == DirectoryMonitor.DELETE):
                iter = self.__getIterFromPath__(path)
                if (iter != None):
                    self.deleteNode(iter)
     
    def __directoryNameComparer__(self, dir1, dir2):
        """
        @summary: Compare two directories.
        @param dir1: First directory to compare.
        @param dir2: Second directory to compare.  
        @return: 
            -1 when dir1 is less than dir2, 
            0 when dir1 is equals than dir2,
            1 when dir1 is greater than dir2.
        """
        dir1cmp = dir1.lower()
        dir2cmp = dir2.lower()
        
        if (dir1cmp > dir2cmp):
            return 1
        elif (dir1cmp < dir2cmp):
            return -1
        return 0
    
    # NAVIGATOR TREEVIEW EVENTS
    def __selectRowTvOneClickSignal__ (self, treeview):
        """
        @summary: Handle select row on explorer TreeView.
        @param treeview: TreeView associated with the event. 
        """
        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()
        if (iter != None):
            sPath = model.get_value(iter, self.__PATH_COLUMN__)
            if (sPath != self.__selectedPath__):
                self.__selectedPath__ = sPath
            else:
                return None
            
            treepath = model.get_path(iter)
            UIUtils.selectPath(selection, treepath, False)
            
            # Runs callback
            if (self.__selectCallback__ != None):
                self.__selectCallback__(self.__selectedPath__)
        else:
            __log__.warning("It could not get TreeIter")

    def __expandRowTVSignal__ (self, treeview, iter, path):
        """
        @summary: Handle expand event of the explorer TreeView.
        @param treeview: TreeView where a TreeIter was expanded.
        @param iter: TreeIter that was expanded.
        @param path: TreePath of the iter.   
        """
        Thread(target=self.__fillDirectory__, args=(path,)).start()
        self.expandToPath(path, glock=False)
    
    def __collapsedRowTVSignal__ (self, treeview, iter, path):
        """
        @summary: Handle collapse event of the explorer TreeView.
        @param treeview: TreeView where a TreeIter was collapsed.
        @param iter: TreeIter that was collapsed.
        @param path: TreePath of the iter.
        """
        sPath = self.__model__.get_value(iter, self.__PATH_COLUMN__)
        monitor = FactoryDirectoryMonitor.getMonitor(sPath)
        monitor.stop()
        self.collapsePath(path)
    
    def getControl(self):
        """
        @summary: Gets control to add into a container.
        @return: GtkScrolledWindow.
        """
        return self.__exportControl__
    
    def setSelectCallback(self, callback):
        """
        @summary: Sets callback that will be executed when directory is selected.
        @param callback: Funtion reference, like function(path : str) 
        """
        self.__selectCallback__ = callback
     
    def addDirectory (self, dirname, fullpath, icon, iter=None, glock=True):
        """
        @summary: Add a directory on navigator.
        @param dirname: Directory name.
        @param fullpath: Full path of the directory.
        @param icon: Icon associated with the directory.
        @param iter: Parent TreeIter. None to add directory as a root TreeIter,
        @param glock: True to lock gtk-loop.     
        """
        newIter = None
        if (iter != None):
            newIter = UIUtils.insertIter(self.__model__, iter, (icon, dirname, fullpath),
                                         self.__PATH_COLUMN__, self.__directoryNameComparer__, doGObject=glock)
        else:
            newIter = UIUtils.addIter(self.__model__, None, (icon, dirname, fullpath), glock)
            
        if (newIter != None):
            self.__prepareDirectory__(fullpath, newIter, glock=glock)
    
    def deleteNode (self, iter, glock=True):
        """
        @summary: Delete an iter from TreeView.
        @param iter: TreeIter to delete.
        @param glock: True to look gtk-loop. Default True.  
        """
        UIUtils.deleteIter(self.__model__, iter, glock)   
        
    def expandToPath(self, path, glock=True):
        """
        @summary: Expand row at path, expanding any ancestors as needed.
        @param path: Path to expand.
        @param glock: True to look gtk-loop. Default True.
        """
        UIUtils.expandTreeview(self.__explorer__, path, glock)

    def collapsePath(self, path):
        """
        @summary: Collapse row at path.
        @param path: Path to collapse.
        """
        # Gets current path
        iter = self.__model__.get_iter(path)
        sPath = self.__model__.get_value(iter, self.__PATH_COLUMN__)
        
        monitor = FactoryDirectoryMonitor.getMonitor(sPath)
        if (monitor != None):
            monitor.stop()
            monitor.removeListener(self.__handlerDirectoryMonitorEvents__)
        
        self.__explorer__.collapse_row(path)

    def applyPathOnNav (self, path, selected=False):
        """
        @summary: Put path in navigator.
        @param path: Path to apply.
        @param selected: True to select TreeIter. Default False. 
        """
        # Expand path on navigator
        Thread(target=self.__expandPath__, args=(path, selected,)).start()

    def sortNavigatorIter (self, iter):
        """
        @summary: Sort iter on navigator.
        @param iter: TreeIter to short. 
        """
        path = self.__model__.get_path(iter)
        self.__model__.rows_reordered(path, iter, new_order)
        
