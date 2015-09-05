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
    import gtk, gobject
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

import time

import FactoryControls
import UIUtils
from pycamimg.util.Singleton import Singleton

# Store class to access as singleton
__instanceRegOp__ = 1
__instanceRegOp__ = None

class RegOperations:
    """
    @summary: Class to handler a treeview as a register of operations
    """        
    __metaclass__ = Singleton
    
    # Index of each column
    __ID_COLUMN__ = 0
    __NAME_COLUMN__ = 1
    __VALUE_COLUMN__ = 2
    __STEP_COLUMN__ = 3
    __ELEMNS_COLUMN__ = 4
    
    def __init__(self):
        """
        @summary: Create new handler.
        @param listWidget: GtkTreeView to handler as a register 
        """
        self.__tvOps__ = gtk.TreeView()
        
        lFrame = gtk.Label(_("<b>Operations</b>"))
        lFrame.set_use_markup(True)
        
        self.__exportControl__ = gtk.Frame()
        self.__exportControl__.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.__exportControl__.set_label_widget(lFrame)
        self.__exportControl__.add(self.__tvOps__)
        
        self.__opsModel__ = None
        
        # Initialize operation TreeView
        self.__initOperations__()
        
    def __call__(self):
        """
        @summary: obfuscate singleton  
        """
        return self
    
    def __initOperations__(self):
        """
        @summary: Initialize operations TreeView
        """
        self.__opsModel__ = gtk.ListStore(gobject.TYPE_STRING,
                                          gobject.TYPE_STRING,
                                          gobject.TYPE_FLOAT,
                                          gobject.TYPE_FLOAT,
                                          gobject.TYPE_FLOAT)

        __log__.debug("Create new model of treeview for the register")

        self.__tvOps__.set_model(self.__opsModel__)
        self.__tvOps__.set_headers_visible(True)
        self.__tvOps__.set_show_expanders(False)
        self.__tvOps__.get_selection().set_mode(gtk.SELECTION_NONE)

        __log__.debug("Sets features of the treeview")

        # Creates columns of the TreeView of Files
        columnProcess = FactoryControls.getTreeColumnText(_("Process"), self.__NAME_COLUMN__)
        self.__tvOps__.append_column(columnProcess)
        
        columnProgress = FactoryControls.getTreeColumnProgress(self.__VALUE_COLUMN__)
        self.__tvOps__.append_column(columnProgress)
        
        __log__.debug("Adds columns to treeview")
        
    def __getOperationNodeById__(self, id):
        """
        @summary: Gets iter of an operation with id
        @param id: Id of the operation to get its node.
        @return: TreeNode of the operation. 
            None if id of the operation does not exist  
        """
        iter = self.__opsModel__.get_iter_first()
        
        while (iter != None):
            value = self.__opsModel__.get_value(iter, self.__ID_COLUMN__)
            if (value == id):
                return iter
            iter = self.__opsModel__.iter_next(iter)
           
        __log__.warning("Operation %s does not exist" % id) 
        return None
        
    def getControl(self):
        """
        @summary: Gets control to add into a container.
        @return: GtkFrame.
        """
        return self.__exportControl__
        
    def getDataOperation(self, id, name, elems):
        """
        @summary: Gets data to add in operations TreeView.
        @param id: Id of the operation.g
        @param name: Name of the operation. It will be shown
        @param elems: Number of steps that have the operation.
        @return: Tuple with operation data. (id, name, value, step)
        """
        value = 0.00
        step = 1
        if (elems > 0):
            step = float(1) / float(elems)
        return (id, name, value, step, elems)

    def addOperation(self, data):
        """
        @summary: Adds an operation in operation treeview.
        @param data: Tuple with operation data. (id, name, value, step)
        @return: New iter inserted.
        """
        return UIUtils.addIterListView(self.__opsModel__, data)

    def addElements(self, iter, elements, gtkLock=True):
        """
        @summary: Sets new values of progress bar.
        @param iter: GtkTreeIter where progress bar is.
        @param elements: New number of elements.
        @param gtkLock: True when lock gtk-loop.
        """               
        newValue = 0.00
        newStep = 1
        if (elements > 0):
            currElems = self.__opsModel__.get_value(iter, self.__ELEMNS_COLUMN__)
            newStep = float(1) / (float(currElems) + float(elements))
            
            currValue = float(self.__opsModel__.get_value(iter, self.__VALUE_COLUMN__)) / 100
            currStep = self.__opsModel__.get_value(iter, self.__STEP_COLUMN__)
            
            newValue = newStep * (currValue / currStep)
            
            UIUtils.setIterData(self.__opsModel__, iter, self.__ELEMNS_COLUMN__, float(currElems) + float(elements), doGObject=gtkLock)
            UIUtils.setIterData(self.__opsModel__, iter, self.__STEP_COLUMN__, newStep, doGObject=gtkLock)
            UIUtils.setIterData(self.__opsModel__, iter, self.__VALUE_COLUMN__, newValue, doGObject=gtkLock)
        else:
            __log__.warning("It can not set 0 elements on a operation")

    def stepOperation(self, iter):
        """
        @summary: Does a step.
        @param iter: Do a step on a iter.
        """
        value = float(self.__opsModel__.get_value(iter, self.__VALUE_COLUMN__)) / 100
        step = self.__opsModel__.get_value(iter, self.__STEP_COLUMN__)
        value += step
        UIUtils.setIterData(self.__opsModel__, iter, self.__VALUE_COLUMN__, value * 100)
    
    def stepOperationById(self, id):
        """
        @summary: Does a step of an operation with id.
        @param id: Id of a operation. 
        """
        iter = self.__getOperationNodeById__(id)
        if (iter != None):
            self.stepOperation(iter)
        else:
            __log__.warning("Iter of the operation %s has not found. " % id)
        
    def removeOperation(self, iter):
        """
        @summary: Removes an operation from TreeView.
        @param iter: Iter to delete. 
        """
        UIUtils.deleteIter(self.__opsModel__, iter)
        del iter
        
    def removeOperationById(self, id):
        """
        @summary: Removes an operation from TreeView that operation id matches.
        @param id: Id of a operation to remove. 
        """
        iter = self.__getOperationNodeById__(id)
        if (iter != None):
            self.removeOperation(iter)
        else:
            __log__.warning("It could not get a iter with operation %s" % id)
