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

try:
    import pygtk
    if (not (sys.platform == "win32")):
        pygtk.require('2.0')
    import gtk, gobject, gtk.gdk
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e

import os.path
from threading import Thread
import time
import urllib
from urlparse import urlparse
import cPickle
import ConfigParser

import UIUtils
import FactoryControls
from RegOperations import RegOperations
from pycamimg.util.ImgMeta import ImgMeta
from pycamimg.util.IOUtils import IOUtils
from pycamimg.util import ImageUtils

from pycamimg.core.CamItem import CamItem
from pycamimg.core.CamCore import CamCore
from pycamimg.core.Configuration import Configuration
from pycamimg.core.operations import Operations
from pycamimg.core.operations.Operations import Operation

DEFAULT_COLUMNS = 4
WAIT_UPDATE = 200

class TabProject:
    """
    @summary: Class to manage a tab as a project.
    """
    VIEW_TREEVIEW = 0
    VIEW_ICONVIEW = 1
    
    COLUMN_IMAGE = 0
    COLUMN_SOURCE = 1
    COLUMN_DATE = 2
    COLUMN_TARGET = 3
    COLUMN_OPERATIONS = 4
    COLUMN_PREVIEW = 5
    COLUMN_DO_IMG = 6
    COLUMN_LOADING = 7
    
    FROM_ITSELF = [("MY_TREE_MODEL_ROW", gtk.TARGET_SAME_WIDGET, 0)]
    TARGET_TEXT = 80
    TO_TEXT = [("text/uri-list", 0, TARGET_TEXT),
               ("MY_TREE_MODEL_ROW", gtk.TARGET_SAME_WIDGET, 0)
               ]
    
    def __init__(self, core, name="", iconsPath=None, iconName=None, numberColumns=DEFAULT_COLUMNS):
        """
        @summary: Create new tab project.
        @param name: Name that will be shown.
        @param iconsPath: Path where icons are.
        @param iconName: Icon that will represent to type of project.
        """
        self.__name__ = name
        self.__core__ = core
        self.__treeview__ = None
        self.__iconview__ = None
        self.__model__ = None
        self.__scroll__ = None
        self.__button__ = None
        self.__label__ = None
        self.__tabWidget__ = None
        self.__notebook__ = None
        self.__receivedCallback__ = None
        self.__closeCallback__ = None
        self.__currentView__ = self.VIEW_TREEVIEW

        self.__doPreviewList__ = Configuration().getConfiguration().getboolean("TABPROJECT", "show_image_list")
        self.__maxHeight__ = Configuration().getConfiguration().getint("TABPROJECT", "max_height_list")
        self.__rescalePercent__ = Configuration().getConfiguration().getfloat("TABPROJECT", "resize_percent_list")
        self.__maxHeightImageIconView__ = Configuration().getConfiguration().getint("TABPROJECT", "max_height_imagelist")
        self.__numberOfColumns__ = Configuration().getConfiguration().getint("TABPROJECT", "number_of_columns_iconview")
        
        if (numberColumns == DEFAULT_COLUMNS):
            self.__numberOfColumns__ = Configuration().getConfiguration().getint("TABPROJECT", "number_of_columns_iconview")
            if (self.__numberOfColumns__ == 0):
                self.__numberOfColumns__ = DEFAULT_COLUMNS
        else:
            self.__numberOfColumns__ = numberColumns
        
        self.__iconsPath__ = iconsPath
        self.__iconName__ = iconName
        
        self.__initializeUI__(numberColumns)    
            
    def __initializeUI__(self, numberColumns):
        """
        @summary: Initialize TreeView Target.
        """
        iconview = gtk.IconView()
        treeview = gtk.TreeView()

        model = gtk.ListStore(gtk.gdk.Pixbuf, 
                              gobject.TYPE_STRING, 
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gtk.gdk.Pixbuf, 
                              gobject.TYPE_BOOLEAN,
                              gobject.TYPE_BOOLEAN)

        model.set_default_sort_func(lambda *args: -1)
        
        __log__.debug("Created model for new project")
    
        treeview.set_model(model)
        treeview.set_headers_visible(True)
        treeview.set_headers_clickable(True)
        treeview.set_rules_hint(True)
        treeview.set_enable_search(False)
        treeview.set_fixed_height_mode(False)
        treeview.set_tooltip_column(self.COLUMN_SOURCE)
        treeview.set_show_expanders(False)
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        treeview.set_reorderable(True)
    
        iconview.set_model(model)
        iconview.set_text_column(self.COLUMN_TARGET)
        iconview.set_pixbuf_column(self.COLUMN_PREVIEW)
        iconview.set_tooltip_column(self.COLUMN_SOURCE)
        iconview.set_columns(numberColumns)
        iconview.set_selection_mode(gtk.SELECTION_MULTIPLE)
        iconview.set_reorderable(True)
    
        __log__.debug("Applied settings")
    
        # Creates columns of the TreeView of target files
        column = FactoryControls.getTreeColumnTextAndPixbuf(_("Name"), self.COLUMN_SOURCE, self.COLUMN_IMAGE)
        treeview.append_column(column)
        columnDate = FactoryControls.getTreeColumnText(_("Photo Date"), self.COLUMN_DATE)
        treeview.append_column(columnDate)
        columnTarget = FactoryControls.getTreeColumnText(_("Target Name"), self.COLUMN_TARGET)
        treeview.append_column(columnTarget)
        columnOps = FactoryControls.getTreeColumnText(_("Operations"), self.COLUMN_OPERATIONS)
        treeview.append_column(columnOps)
    
        __log__.debug("Columns added")
    
        # Enabled as drag source
        treeview.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, 
                                          self.FROM_ITSELF, 
                                          gtk.gdk.ACTION_MOVE)
    
        iconview.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, 
                                          self.FROM_ITSELF, 
                                          gtk.gdk.ACTION_MOVE)
            
        # Enabled as drop target
        treeview.enable_model_drag_dest(self.TO_TEXT, 
                                        gtk.gdk.ACTION_DEFAULT
                                        |gtk.gdk.ACTION_COPY
                                        |gtk.gdk.ACTION_MOVE)
        
        iconview.enable_model_drag_dest(self.TO_TEXT, 
                                        gtk.gdk.ACTION_DEFAULT
                                        |gtk.gdk.ACTION_COPY
                                        |gtk.gdk.ACTION_MOVE)
        
        treeview.connect("drag-data-get", self.__dragTarget__)
        treeview.connect("drag-data-received", self.__dropTarget__)
        treeview.connect("key-press-event", self.__keyPressEvent__)
        
        iconview.connect("drag-data-get", self.__dragTarget__)
        iconview.connect("drag-data-received", self.__dropTarget__)
        iconview.connect("key-press-event", self.__keyPressEvent__)
        
        __log__.debug("Drag & Drop enabled")
        
        scroll = gtk.ScrolledWindow()
        scroll.add(treeview)
        
        size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        if ((self.__iconName__ != None) and (self.__iconName__ != "")):
            pbProject = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(self.__iconsPath__, self.__iconName__),
                                                             size[0], size[1])
        else:
            pbProject = FactoryControls.getPixbufFromStock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_MENU)
            
        imageProject = gtk.Image()
        imageProject.set_from_pixbuf(pbProject)
        
        bClose = gtk.Button(label=None, stock=None, use_underline=False)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        bClose.set_relief(gtk.RELIEF_NONE)
        bClose.set_border_width(0)
        bClose.set_image(image)
        bClose.connect("clicked", self.__buttonActivateSignal__)
        
        lTitle = gtk.Label(str=self.__name__)
        hbTab = gtk.HBox()
        
        hbTab.pack_start(imageProject, expand=False, fill=False, padding=1)
        hbTab.pack_start(lTitle, expand=False, fill=False, padding=2)
        hbTab.pack_start(bClose, expand=False, fill=False)
        
        __log__.debug("Scroll created")
        
        self.__label__ = lTitle
        self.__button__ = bClose
        self.__tabWidget__ = hbTab
        
        self.__treeview__ = treeview
        self.__iconview__ = iconview
        self.__model__ = model
        self.__scroll__ = scroll
    
    def __addTargetFiles__(self, files, defaultIcon, 
                           iterOp, 
                           iter = None, 
                           position = gtk.TREE_VIEW_DROP_AFTER,
                           recursiveLevel = 0,
                           gtkLock = True):
        """
        @summary: Add files to target listview.
        @param files: List of files to add.
        @param defaultIcon: Default icon to associate with each file.
        @param iterOp: GtkIter of operation progress bar.
        @param recursiveLevel: Current recursive level.
        @param iter: Iter that it will use as reference to insert new files.
        @param position: Position over iter.    
        @param gtkLock: True to do a lock on gtk loop.
        """
        if (files != None):
            operations = RegOperations()
            
            # Add each file into target TreeView
            for file in files:
                __log__.debug("Adding %s" % file)
                if (iterOp != None):
                    operations.stepOperation(iterOp)
                if (file == ""):
                    __log__.warn("Empty file path. Skip file")
                    continue
                if (self.__core__.getItem(file) != None):
                    __log__.info("File %s already exists in target file list" % file)
                    continue
                
                # Checks if is a folder and system is configured to add files recursively
                if (os.path.isdir(file) and Configuration().getConfiguration().getboolean("UI_CORE", "add_recursive")):
                    __log__.debug("%s is folder. Adding images into folder." % file)
                    # Do recursivity
                    if (recursiveLevel < Configuration().getConfiguration().getint("UI_CORE", "recursive_level")):
                        ioUtils = IOUtils()
                        listNewFiles = []
                        if ((recursiveLevel + 1) != Configuration().getConfiguration().getint("UI_CORE", "recursive_level")):
                            listNewFiles += ioUtils.getDirectories(file, Configuration().getConfiguration().getboolean("NAVIGATOR", "show_hiddens"), getFullpath=True)
                        
                        listNewFiles += ioUtils.getFiles(file, Configuration().getConfiguration().getboolean("NAVIGATOR", "show_hiddens"), getFullpath=True)
                        __log__.debug("Adding images from folder %s" % file)
                        
                        operations.addElements(iterOp, len(listNewFiles), gtkLock=gtkLock)
                        self.__addTargetFiles__(listNewFiles, defaultIcon, iterOp, 
                                                iter=iter, position=position,
                                                recursiveLevel=(recursiveLevel+1), gtkLock=gtkLock)
                        
                        del ioUtils
                    else:
                        __log__.debug("Max. recursive level got.")
                    continue
    
                head, filename = os.path.split(file)
                item = CamItem(file, target=filename)
                __log__.debug("New CamItem created for filename %s. %s" % (filename, item))
                    
                # Create a new row
                newRowData = [defaultIcon, 
                              file, 
                              _("Loading..."), 
                              filename , 
                              item.getDescription(),
                              defaultIcon,
                              False,
                              True]
                
                iterAdd = UIUtils.insertIterAtPathPosition(self.__model__, newRowData, 
                                                           iter, position=position,
                                                           doGObject=gtkLock)
                __log__.info("New file inserted into target treeview. %s" % file)
            
                if (iterAdd != None):
                    self.__core__.addItem(file, item)
                    self.updateItem(iterAdd, item, gtkLock=gtkLock)
                else:
                    __log__.error("It could not insert new item into project. %s" % file)
                    del newRowData
                    del item
        else:
            __log__.warning("Files parameter is None")
        
    
    def __updateImageTarget__(self, iter, item, delMetadata=False):
        """
        @summary: Updates image of target file.
        @param iter: Iter of listview that matches with target file.
        @param item: CamItem to update.
        @param delMetadata: True to delete metadata at the end of function
        """
        little = None
        big = None
        
        item.waitLoadThumbnail()
        imgPil = item.doPreview()
        if (imgPil != None):
            metaData = ImgMeta(item.getPath(), image=imgPil)
        else:
            metaData = item.getMetadata()
        
        UIUtils.setIterData(self.getModel(), iter, self.COLUMN_LOADING, True)
        
        if (self.__doPreviewList__):
            if (not self.__model__.get_value(iter, self.COLUMN_DO_IMG)):
                __log__.debug("Get thumbnail from %s" % file)
                little = metaData.getIcon(maxHeight=self.__maxHeight__, rescale=self.__rescalePercent__)

                if (little):
                    UIUtils.setIterData(self.__model__, iter, self.COLUMN_IMAGE, little)
                    UIUtils.setIterData(self.__model__, iter, self.COLUMN_DO_IMG, True)
            
        __log__.debug("Doing preview image of %s" % self.__model__.get_value(iter, self.COLUMN_SOURCE))
        if (metaData != None):
            big = metaData.getIcon(rescale=100, maxHeight=self.__maxHeightImageIconView__)
        if (big):
            __log__.debug("Updating data on model for %s." % self.__model__.get_value(iter, self.COLUMN_SOURCE))
            UIUtils.setIterData(self.__model__, iter, self.COLUMN_PREVIEW, big)
            
        if (delMetadata and (metaData != None)):
            del metaData
            
        UIUtils.setIterData(self.getModel(), iter, self.COLUMN_LOADING, False)
    
    def setCore(self, core):
        """
        @summary: Sets core that is associated with tabproject.
        @param core: pycamimg.core.CamCore 
        """
        self.__core__ = core
        
    def getCore(self):
        """
        @summary: Gets core that is associated with tabproject.
        @return: pycamimg.core.CamCore
        """
        return self.__core__

    def setCloseCallback (self, callback):
        """
        @summary: Sets callback that will do when tab closed.
        @param callback: Callback reference 
        """
        self.__closeCallback__ = callback
        
    def getCloseCallback (self):
        """
        @summary: Gets callback that will do when tab closed.
        @return: Callback reference
        """
        return self.__closeCallback__
        
    def setName(self, name):
        """
        @summary: Sets name of the project.
        @param name: Name of the project. 
        """
        self.__name__ = name
        
    def getName(self):
        """
        @summary: Gets name of the project.
        @return: Name of the project.
        """
        return self.__name__
    
    def getTreeview(self):
        """
        @summary: Gets treeview.
        @return: Get a GtkTreeView
        """
        return self.__treeview__
    
    def getIconview(self):
        """
        @summary: Gets iconview
        @return: Gets a GtkIconView
        """
        return self.__iconview__
    
    def getModel(self):
        """
        @summary: Gets model of the treeview.
        @return: Gets a GtkTreeModel.
        """
        return self.__model__
    
    def getSelection(self):
        """
        @summary: Gets selection in the project.
        @return: Gets selection 
        """
        selection = None
        if (self.__currentView__ == self.VIEW_TREEVIEW):
            treeselection = self.__treeview__.get_selection()
            if (treeselection != None):
                model, paths = treeselection.get_selected_rows()
                selection = paths
            else:
                __log__.debug("Treeselection is None")
        elif (self.__currentView__ == self.VIEW_ICONVIEW):
            selection = self.__iconview__.get_selected_items()
        else:
            __log__.warning("Unknown view")
        return selection
    
    def getScrollWidget(self):
        """
        @summary: Gets scroll widget.
        @return: Gets a GtkScrolledWindow
        """
        return self.__scroll__
    
    def getTabWidget(self):
        """
        @summary: Get widget to place on tab.
        @return: Gets GtkBox
        """
        return self.__tabWidget__
    
    def addToNotebook(self, notebook, threadBlock = True, focused = True):
        """
        @summary: Add tab to notebook.
        @param notebook: Notebook where tab will be added.
        @param threadBlock: True for block gtk loop.
        @param focused: True for focus tab when will be added.   
        """
        self.__notebook__ = notebook
        UIUtils.addTabControl(notebook, 
                              self.__scroll__,
                              self.__tabWidget__,
                              doGObject = threadBlock)
        if (focused):
            self.__notebook__.set_current_page(self.__notebook__.page_num(self.__scroll__)) 
    
    def closeTab (self):
        """
        @summary: Close tab from notebook.
        """
        UIUtils.removeTab(self.__notebook__, self.__scroll__, doGObject=False)
    
    def updateItem(self, iter, item, updateImage=True, gtkLock=True):
        """
        @summary: Update an item.
        @param iter: GtkTreeIter that represents an item.
        @param item: CamItem to update.:
        @param gtkLock: True to do the action with gtklock 
        """
        
        self.updateItemDescription(iter, item, gtkLock=gtkLock)
        self.updateItemTarget(iter, item, gtkLock=gtkLock)
        self.updateItemDate(iter, item, gtkLock=gtkLock)
        if (updateImage):
            self.updateItemImage(iter, item)
    
    def updateItemImage(self, iter, item):
        """
        @summary: Update image preview of an item.
        @param iter: GtkTreeIter that represents an item.
        @param item: CamItem to update.
        """
        __log__.debug("Updating image of %s" % item.getPath())
        Thread(target=self.__updateImageTarget__, args=(iter, item, True,)).start()
    
    def updateItemDate(self, iter, item, gtkLock=True):
        """
        @summary: Update target of an item.
        @param iter: GtkTreeIter that represents an item.
        @param item: CamItem to update.
        @param gtkLock: True to do the action with gtklock
        @return: true if operation is done.
        """
        item.waitLoadThumbnail()
        if (item.getMetadata() == None):
            __log__.warn("There is not metadata in %s. Skip file" % item.getPath())
            UIUtils.setIterData(self.getModel(), iter, self.COLUMN_DATE, _("Unknown"), doGObject=gtkLock)
            
            return False
        else:
            UIUtils.setIterData(self.getModel(), iter, self.COLUMN_DATE, item.getMetadata().getDateTimeDigitized(), doGObject=gtkLock)
        
        return True
            
    def updateItemTarget(self, iter, item, gtkLock=True):
        """
        @summary: Update target of an item.
        @param iter: GtkTreeIter that represents an item.
        @param item: CamItem to update.
        @param gtkLock: True to do the action with gtklock
        """
        UIUtils.setIterData(self.getModel(), iter, self.COLUMN_TARGET, item.getTarget(), doGObject=gtkLock)
    
    def updateItemDescription(self, iter, item, gtkLock=True):
        """
        @summary: Update description of an item.
        @param iter: GtkTreeIter that represents an item.
        @param item: CamItem to update.
        @param gtkLock: True to do the action with gtklock.
        """
        UIUtils.setIterData(self.getModel(), iter, self.COLUMN_OPERATIONS, item.getDescription(), doGObject=gtkLock)
        
    def changeView(self, view, doGObject=False):
        """
        @summary: Change the type of view in tab project.
        @param view: Type of view. VIEW_TREEVIEW or VIEW_ICONVIEW
        @param doGObject: True to do the action with gtklock  
        """
        if (doGObject):
            gtk.gdk.threads_enter()
        try:
            if (self.__scroll__ != None):
                if (self.__currentView__ != view):
                    if (view == self.VIEW_TREEVIEW):
                        self.__scroll__.remove(self.__iconview__)
                        self.__scroll__.add(self.__treeview__)
                        
                        #Update treeview selection
                        treeselection = self.__treeview__.get_selection()
                        treeselection.unselect_all()
                        paths = self.getSelection()
                        if (paths != None):
                            for path in paths:
                                treeselection.select_path(path)
                        else:
                            __log__.debug("There are not path selected")
                        
                        self.__scroll__.show_all()
                    elif (view == self.VIEW_ICONVIEW):
                        self.__scroll__.remove(self.__treeview__)
                        self.__scroll__.add(self.__iconview__)
                        
                        #Update iconview selection
                        self.__iconview__.unselect_all()
                        paths = self.getSelection()
                        if (paths != None):
                            for path in paths:
                                self.__iconview__.select_path(path)
                        else:
                            __log__.debug("There are not path selected")
                        
                        self.__scroll__.show_all()
                    else:
                        __log__.info("Unknown view %d" % view)
                        
                    self.__currentView__ = view
                else:
                    __log__.debug("It is not going to change view. It is same")
            else:
                __log__.warning("It could no recover scroll widget")
        finally:
            if (doGObject):
                gtk.gdk.threads_leave()
    
    
    def moveTargetFiles(self,
                        paths,
                        iterRef = None,
                        position = gtk.TREE_VIEW_DROP_AFTER,
                        gtkLock = True):
        """
        @summary: Move files into target view.
        @param paths:  A list of TreePath to move.
        @param iterRef: Iter that it will use as reference to insert new files.
        @param position: Position over iter.
        @param gtkLock: True to do a lock on gtk loop.    
        """
        if (paths != None):
            for path in paths:
                iter = self.__model__.get_iter(path)
                if (iter != None):
                    UIUtils.moveIterAtPathPosition(self.__model__, iter, iterRef, position, doGObject=gtkLock)
                else:
                    __log__.warning("It could not retrieve iter from path")
        else:
            __log__.debug("There are not paths to move")
    
    def addTargetFiles(self, 
                       files,
                       iter = None, 
                       position = gtk.TREE_VIEW_DROP_AFTER,
                       gtkLock = True):
        """
        @summary: Add a file list into target view.
        @param files:  A list of files to add.
        @param iter: Iter that it will use as reference to insert new files.
        @param position: Position over iter.    
        @param gtkLock: True to do a lock on gtk loop.    
        """
        if (self.__core__ == None):
            __log__.debug("There is not a project in tabproject")
            return
        
        if (files != None):
            iNImages = len(files)
            __log__.debug("Adding new %d images" % iNImages)
            
            operations = RegOperations()
            iterOp = None
            if (operations != None):
                opData = operations.getDataOperation("AddImg",
                                                     _("Adding images..."), 
                                                     iNImages)
                # Add new operation to operation treeview
                iterOp = operations.addOperation(opData)
                
            # Gets pixbuf file 
            icon = FactoryControls.getPixbufFromStock(gtk.STOCK_FILE)

            self.__addTargetFiles__(files, icon, iterOp, 
                                    iter=iter, position=position, 
                                    gtkLock=gtkLock)

            if (iterOp != None):
                operations.removeOperation(iterOp)
        else:
            __log__.debug("There are not files to insert")
    
    def deleteImages (self, paths, gtkLock=True):
        """
        @summary: Delete images from target treeview.
        @param paths: Paths to delete 
        @param gtkLock: True to do a lock on gtk loop.
        """
        if (paths != None):
            paths.sort(reverse=True)
            for path in paths:
                # Delete selected items on target treeview
                iter = self.__model__.get_iter(path)
                if (iter != None):
                    text = self.__model__.get_value(iter, self.COLUMN_SOURCE)
                else:
                    __log__.warn("Can not find iter from path %s. Skip path" % path)
                    continue
                
                waitDelete = self.__model__.get_value(iter, self.COLUMN_LOADING)
                while (waitDelete):
                    time.sleep(WAIT_UPDATE)
                    waitDelete = self.__model__.get_value(iter, self.COLUMN_LOADING)
                
                
                self.__core__.removeItem(text)
                UIUtils.deleteIter(self.__model__, iter, doGObject=gtkLock)
                __log__.info("Delete file %s from project" % text)
        else:
            __log__.debug("There are not files to delete")
    
    def deleteSelectedImages (self, gtkLock=True):
        """
        @summary: Delete files from target TreeView
        @param gtkLock: True to do a lock on gtk loop.
        """
        paths = self.getSelection()
        if (paths == None):
            __log__.error("It can not recover tree selection. Abort delete operation.")
            return
        self.deleteImages(paths, gtkLock=gtkLock)
    
    def doOperation (self, name, parameters = {}, description = "", gtkLock=True):
        """
        @summary: Do operation on selected items.
        @param name: New size for images.
        @param parameters: Dictionary with parameters and their values.
        @param description: Description of operation. 
        @param gtkLock: True to do a lock on gtk loop.
        """      
        __log__.debug("Begin %s operation..." % name)
        paths = self.getSelection()
        if (paths == None):
            __log__.error("It can not recover tree selection. Abort %s operation." % name)
            return
        iNImages = len(paths)
        __log__.debug("Images to %s: %d" % (name, iNImages))
        
        iterOp = None
        operations = RegOperations()
        if (operations != None):
            opData = operations.getDataOperation(name, description, iNImages)
            iterOp = operations.addOperation(opData)        
        
        for path in paths:
            __log__.debug("Do %s on %s" % (name, path))
            if (iterOp != None):
                operations.stepOperation(iterOp)
            # Add selected files from files TreeView
            iter = self.__model__.get_iter(path)
            if (iter != None):
                file = self.__model__.get_value(iter, self.COLUMN_SOURCE)
            else:
                __log__.warn("It can not recover an iter from path %s. Skip it" % path)
                continue

            item = self.__core__.getItem(file)
            if (item != None):
                __log__.debug("Get item %s from file %s" % (item, file))
                op = item.getOperation(name)
                if (op == None):
                    classname = Operations.getOperation(name)
                    op = classname()
                    item.addOperation(name, op)
                
                if (op != None):
                    #the value of dictionary is a tuple that contains, new value
                    # and a callback to do before assignment. (newValue, callback)
                    # callback must be return new value, and accept two parameters.
                    # old value and new value.
                    for keyParam, tupleParam in parameters.iteritems():
                        valueParam, callbackParam = tupleParam
                        oldValue = op.getParameter(keyParam)
                        if ((callbackParam != None) and (oldValue != None)):
                            op.setParameter(keyParam, callbackParam(oldValue, valueParam))
                        else:
                            op.setParameter(keyParam, valueParam)
                    
                __log__.info("File %s done %s operation." % (file, name))
                self.updateItem(iter, item, gtkLock=gtkLock)
                __log__.debug("File %s updated" % file)
            else:
                __log__.warning("Core does not have file %s" % file)
        
        if (iterOp != None):
            operations.removeOperation(iterOp)
    
    def doOperationOnItem (self, name, parameters = {}, description = "", gtkLock=True):
        """
        @summary: Do operation on properties of item.
        @param name: New size for images.
        @param parameters: Dictionary with parameters and their values.
        @param description: Description of operation. 
        @param gtkLock: True to do a lock on gtk loop.
        """
        __log__.debug("Begin %s operation..." % name)
        paths = self.getSelection()
        if (paths == None):
            __log__.error("It can not recover tree selection. Abort %s operation." % name)
            return
        iNImages = len(paths)
        __log__.debug("Images to %s: %d" % (name, iNImages))
        
        iterOp = None
        operations = RegOperations()
        if (operations != None):
            opData = operations.getDataOperation(name, description, iNImages)
            iterOp = operations.addOperation(opData)        
        
        count = 0
        for path in paths:            
            __log__.debug("Do %s on %s" % (name, path))
            if (iterOp != None):
                operations.stepOperation(iterOp)
            # Add selected files from files TreeView
            iter = self.__model__.get_iter(path)
            if (iter != None):
                file = self.__model__.get_value(iter, self.COLUMN_SOURCE)
            else:
                __log__.warn("It can not recover an iter from path %s. Skip it" % path)
                continue

            item = self.__core__.getItem(file)
            if (item != None):
                __log__.debug("Get item %s from file %s" % (item, file))
                
                for keyProperty, parameter in parameters.iteritems():
                    #the value of dictionary is a tuple that contains, new value
                    # and a callback to do before assignment. (newValue, callback)
                    # callback must be return new value, and accept four parameters.
                    # item: pycamimg.core.CamItem, iter: GtkTreeIter, count: int, newValue.
                    valueProperty, functionProperty = parameter
                    if (functionProperty != None):
                        item.setProperty(keyProperty, functionProperty(item, iter, count, keyProperty, valueProperty))
                    else:
                        item.setProperty(keyProperty, valueProperty)
                    
                __log__.info("File %s done %s operation." % (file, name))
                self.updateItem(iter, item, updateImage=False, gtkLock=gtkLock)
                __log__.debug("File %s updated" % file)
            else:
                __log__.warning("Core does not have file %s" % file)
            
            count += 1
        
        if (iterOp != None):
            operations.removeOperation(iterOp)
    
    def setOrderToCore(self):
        """
        @summary: Sets order into core to process items.
        """
        listOrder = []
        iterIterator = self.__model__.get_iter_first()
        while (iterIterator != None):
            pathFile = self.__model__.get_value(iterIterator, self.COLUMN_SOURCE)
            listOrder.append(pathFile)
            iterIterator = self.__model__.iter_next(iterIterator)
        
        self.__core__.setOrderItemProcess(listOrder)
    
    def load(self):
        """
        @summary: Load core information in treeview. 
        """
        Thread(target=self.__loadCore__, args=(self.__core__,)).start()
    
    def loadCore (self, core):
        """
        @summary: Load core information in treeview.
        @param core: Core that will be loaded into tab project. 
        """
        Thread(target=self.__loadCore__, args=(core,)).start()
    
    
    def __loadCore__(self, core):
        """
        @summary: Load core information in treeview. It will be called by a thread.
        @param core: Core that will be loaded into tab project.
        """
        self.__doPreviewList__ = Configuration().getConfiguration().getboolean("TABPROJECT", "show_image_list")
        self.__maxHeight__ = Configuration().getConfiguration().getint("TABPROJECT", "max_height_list")
        self.__rescalePercent__ = Configuration().getConfiguration().getfloat("TABPROJECT", "resize_percent_list")
        self.__maxHeightImageIconView__ = Configuration().getConfiguration().getint("TABPROJECT", "max_height_imagelist")
        self.__numberOfColumns__ = Configuration().getConfiguration().getint("TABPROJECT", "number_of_columns_iconview")
        
        gtk.gdk.threads_enter()
        try:
            self.__iconview__.set_columns(self.__numberOfColumns__)
        finally:
            gtk.gdk.threads_leave()
        
        UIUtils.clearModelTreeview(self.__model__)
        
        # Gets pixbuf file 
        icon = FactoryControls.getPixbufFromStock(gtk.STOCK_FILE)
        
        for key, item in core.getItems().iteritems():
            item.refreshThumbnail()
            
            # Handler to extract metadata
            metaData = item.getMetadata()
            
            # Create a new row
            newRowData = [icon, 
                          item.getPath(), 
                          metaData.getDateTimeDigitized(), 
                          item.getTarget() , 
                          item.getDescription(),
                          icon,
                          False]
            
            iterAdd = UIUtils.insertIterAtPathPosition(self.__model__, newRowData, 
                                                        None, position=gtk.TREE_VIEW_DROP_AFTER)
            __log__.info("File inserted into target treeview. %s" % file)
            
            self.updateItemImage(iterAdd, item)
            
        self.__core__ = core
    
    def __buttonActivateSignal__ (self, button):
        """
        @summary: Handle activate signal.
        @param button: GtkButton that raise event. 
        """
        index = self.__notebook__.page_num(self.__scroll__)
        if (self.__closeCallback__ != None):
            self.__closeCallback__(index)
        
    def __dragTarget__ (self, treeview, context, selection, info, timestamp):
        """
        @summary: Handle drag get data event of the target TreeView.
        @param treeview: TreeView that receives data.
        @param context: Drag&Drop context.
        @param selection: Drag&Drop selection.
        @param info: Drag&Drop information.
        @param timestamp: Timestamp when the event raise.    
        """
        paths = self.getSelection()
        text = cPickle.dumps(paths, protocol=cPickle.HIGHEST_PROTOCOL)
        selection.set(selection.target, 8, text)
    
    def __dropTarget__ (self, treeview, context, x, y, selection, info, etime):
        """
        @summary: Handle drop event on target treeview.
        @param treeview: TreeView that receives data.
        @param context: Drag&Drop context.
        @param x: X coordinate.
        @param y: Y coordinate.  
        @param selection: Drag&Drop selection.
        @param info: Drag&Drop information.
        @param timestamp: Timestamp when the event raise.
        """
        iter = None
        path = None
        position = gtk.TREE_VIEW_DROP_AFTER
        drop_info = None
        
        # Gets model of the TreeView
        model = treeview.get_model()
        
        # Gets drop position into TreeView
        if (treeview == self.__treeview__):
            drop_info = treeview.get_dest_row_at_pos(x, y)
        elif (treeview == self.__iconview__):
            drop_info = treeview.get_dest_item_at_pos(x, y)
        else:
            __log__.warning("Unknown view")
        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)
        
        if (selection.data == None):
            __log__.info("There is not data in the drag & drop event.")
            context.finish(False, False, etime)
        if ((info == self.TARGET_TEXT) and
            (context.action != gtk.gdk.ACTION_COPY)):
            __log__.info("It can not receive these data.")
            context.finish(False, False, etime)
        elif ((info == 0) and 
              (context.action != gtk.gdk.ACTION_MOVE)):
            __log__.info("It can not receive these data.")
            context.finish(False, False, etime)

        if (info == self.TARGET_TEXT):
            # Declare a list of files that are going to drop on target TreeView
            files = []
            # Check type target
            uris = selection.get_uris()
            
            if (uris != None):
                __log__.debug("Checking each file received")
                for uri in uris:
                    (scheme, netloc, path, params, query, fragment) = urlparse(uri)
                    if (scheme == "file"):
                        files.append(urllib.url2pathname(path))
                    else:
                        __log__.warning("URI scheme not supported. %s" % scheme)

            if (len(files) == 0):
                __log__.info("There are not valid files.")
                context.finish(False, False, etime)
                
            # Add items
            Thread(target=self.addTargetFiles, 
                   args=(files, iter, position,)).start()

            context.finish(True, False, etime)
                
        elif  (info == 0):
            # Gets model of the TreeView
            model = treeview.get_model()
            paths = None
            try:
                paths = cPickle.loads(selection.data)
            except:
                __log__.warning("Data was not retrieved.")
                paths = None
            if (paths != None):
                sortTuple = self.__model__.get_sort_column_id()
                if (sortTuple[0] != None):
                    if (sortTuple[0] >= 0):
                        UIUtils.setColumnOrder(self.__model__, -2, gtk.SORT_ASCENDING, False)
                else:
                    UIUtils.setColumnOrder(self.__model__, -2, gtk.SORT_ASCENDING, False)
                self.moveTargetFiles(paths, iter, position, gtkLock = False)
            
            context.finish(True, False, etime)
        else:
            context.finish(False, False, etime)
            
    def __keyPressEvent__(self, widget, event):
        """
        @summary: Handler to key press event.
        @param widget: Widget where event has occurred.
        @param event: Event associated with signal.
        """
        if (gtk.gdk.keyval_name(event.keyval) == "Delete"):
            paths = self.getSelection()
            if (paths != None):
                if (len(paths) > 0):
                    Thread(target=self.deleteSelectedImages).start()
                else:
                    __log__.debug("There are not selected items")
            else:
                __log__.debug("There are not selected items")
        
        
        return False
