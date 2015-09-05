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
    import gtk, gobject
    
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

import ConfigParser
import FactoryControls
import UIUtils
from pycamimg.core.Configuration import Configuration

class OperationsDialog (gtk.Dialog):
    """
    @summary: Class that manage operations dialog.
    """
    COLUMN_KEY = 0
    COLUMN_OPERATION = 1
    COLUMN_PARAMETERS = 2
    COLUMN_DELETE = 3
    
    __DEFAULT_WINDOW_WIDTH__ = 400
    __DEFAULT_WINDOW_HEIGHT__ = 350
    
    def __init__(self, item, iter, callback=None, parent=None):
        """
        @summary: Create new operations dialog.
        @param callback: Callback that it will be executed when dialog closes    
        @param parent: GtkWindow parent.  
        """
        super(OperationsDialog, self).__init__()
        
        super(OperationsDialog, self).set_title("%s: %s" % (_("Operations"), item.getPath()))
        super(OperationsDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(OperationsDialog, self).add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                  gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(OperationsDialog, self).set_transient_for(parent)
        if (parent != None):
            super(OperationsDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(OperationsDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(OperationsDialog, self).connect("response", self.__closeEvent__)
        super(OperationsDialog, self).set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)
        
        self.__item__ = item
        self.__iter__ = iter
        
        self.__initUI__()
        self.__callback__ = callback


    def __initUI__(self):
        """
        @summary: Initialize ui.
        """
        treeview = gtk.TreeView()
        self.__model__ = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_BOOLEAN)

        # self.__model__.set_default_sort_func(lambda *args: -1)
        
        __log__.debug("Created model for new project")
    
        treeview.set_model(self.__model__)
        treeview.set_headers_visible(True)
        treeview.set_headers_clickable(False)
        treeview.set_rules_hint(True)
        treeview.set_enable_search(False)
        treeview.set_fixed_height_mode(False)
        treeview.set_tooltip_column(self.COLUMN_OPERATION)
        treeview.set_show_expanders(False)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview.set_reorderable(False)
        
        # Creates columns of the TreeView of target files
        columnOperation = FactoryControls.getTreeColumnText(_("Operation"), self.COLUMN_OPERATION, sortable=False)
        treeview.append_column(columnOperation)
        columnParams = FactoryControls.getTreeColumnText(_("Parameters"), self.COLUMN_PARAMETERS, sortable=False)
        treeview.append_column(columnParams)
        columnDel = FactoryControls.getTreeColumnToggle(_("Delete"), self.__model__, self.COLUMN_DELETE)
        treeview.append_column(columnDel)
        
        self.__treeview__ = treeview
        
        scroll = gtk.ScrolledWindow()
        scroll.add(self.__treeview__)
        
        vBox = gtk.VBox()
        vBox.pack_start(scroll, True, True)
        
        self.get_child().pack_start(vBox, True, True)
        vBox.show_all()

    def __initData__(self, gtkLock=False):
        """
        @summary: Set data to dialog.
        """        
        if (self.__item__ != None):
            lOperations = self.__item__.getOperations()
            if (lOperations != None):
                for key, op in lOperations.iteritems():
                    newRowData = [key, op.getOp(), op.toString(), False]
                    UIUtils.addIterListView(self.__model__,
                                            newRowData,
                                            doGObject=gtkLock)
                    __log__.info("New file inserted into operations treeview. %s" % key)

    
    def __closeEvent__(self, w, res):
        """
        @summary: Handle response about options dialog.
        @param w: GtkDialog associated.
        @param res: Response associated with the event.  
        """
        if (res == gtk.RESPONSE_OK):
            iter = self.__model__.get_iter_first()
            while (iter != None):
                bDelete = self.__model__.get_value(iter, self.COLUMN_DELETE)
                keyOp = self.__model__.get_value(iter, self.COLUMN_KEY)
                if (bDelete):
                    self.__item__.removeOperation(keyOp)
                iter = self.__model__.iter_next(iter)
            
            if (self.__callback__ != None):
                self.__callback__(self.__item__, self.__iter__)
           
        w.hide()

    def setCallback(self, callback):
        """
        @summary: Set callback to execute when confirm configuracion.
        @param callback: Function reference. 
        @note: callback model: callback (dialog: gtk.Dialog)        
        """
        self.__callback__ = callback

    def run(self):
        """
        @summary: Show option  dialog.
        """
        self.__initData__()
        super(OperationsDialog, self).run()

