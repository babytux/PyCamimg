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
import os
import os.path

if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

try:
    import pygtk
    pygtk.require('2.0')
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e
try:
    import gtk, gobject, gtk.gdk
except Exception, e:
    __log__.fatal("It can not import gtk & glade module. Sure you have installed pygtk?" )
    raise e

try:
    from PIL import Image
    Image._initialized=2
except ImportError, e:
    __log__.fatal("It could not import Image.PIL. Sure you have installed PIL library. %s" % e)

import threading, thread
from threading import Thread

from pycamimg.core.plugins import IOperationPlugin
from pycamimg.ui import FactoryControls
from pycamimg.util.ImgMeta import ImgMeta
from pycamimg.util import ImageUtils
import FlipOperation
from FlipOperation.FlipDialog import FlipDialog
from FlipOperation import Operation

import gettext
import FlipOperation.camimgplugin
    

class CamimgPlugin(IOperationPlugin.OperationPlugin):
    """
    @summary: Defines flip operation.
    """
    def __init__(self):
        """
        @summary: Creates new flip operation plugin.
        """
        self.__gtkAction__ = gtk.Action("FlipMirrorAction", self.__trans__("Flip/Mirror Images"), self.__trans__("Flip/Mirror selected images"), None)
        self.__gtkAction__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkAction__.set_tool_item_type(gtk.ToolButton)
        
        self.__gtkActionFlip__ = gtk.Action("FlipAction", self.__trans__("Flip Images"), self.__trans__("Flip selected images"), None)
        self.__gtkActionFlip__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkActionFlip__.set_tool_item_type(gtk.ToolButton)
        
        self.__gtkActionMirror__ = gtk.Action("MirrorAction", self.__trans__("Mirror Images"), self.__trans__("Mirror selected images"), None)
        self.__gtkActionMirror__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkActionMirror__.set_tool_item_type(gtk.ToolButton)
    
    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(FlipOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)    
        
    def callbackAction(self, action, currentTab, userData = None):
        """
        @summary: Callback that will be thrown when any action is actived.
        @param action: gtk.Action activated.
        @param currentTab: Current Tab. pycamimg.ui.TabProject.TabProject
        @param userData: User data
        """
        if ((action.get_name() != "FlipMirrorAction") and 
            (action.get_name() != "FlipAction") and 
            (action.get_name() != "MirrorAction")):
            __log__.warning("It is not a valid action. %s" % action.get_name())
            return
        if (currentTab == None):
            __log__.warning("There is not current project")
            return
        
        self.__currentTab__ = currentTab
        parentWindow = userData
        paths = currentTab.getSelection()
        model = currentTab.getModel()
        if ((paths == None) or (model == None)):
            __log__.error("It can not recover tree selection. Set selection at 0.")
            iNRows = 0
        else:
            iNRows = len(paths)
            
        if iNRows > 0:
            if (action.get_name() == "FlipAction"):
                self.__doFlip__(None, Operation.VERTICAL)
            elif(action.get_name() == "MirrorAction"):
                self.__doFlip__(None, Operation.HORIZONTAL)
            elif(action.get_name() == "FlipMirrorAction"):
                flipDialog = FlipDialog(callback = self.__doFlip__,
                                            parent = parentWindow)
                __log__.debug("Flip dialog created. %s" % flipDialog )
                if (iNRows == 1):
                    iter = model.get_iter(paths[0])
                    itemPath = model.get_value(iter, self.__currentTab__.COLUMN_SOURCE)
                    item = self.__currentTab__.getCore().getItem(itemPath)
                    flipDialog.setData(item)
                flipDialog.run()
            pass
        else:
            FactoryControls.getMessage(self.__trans__("Select one or more items"), 
                                       title=self.__trans__("Flip"),
                                       parent = parentWindow)
        
        return
    
    def __doFlip__(self, dialog, orientation):
        """
        @summary: Handle response of flip dialog, 
                    when user want to flip some images
        """
        if (self.__currentTab__ != None):
            params = {"orientation":(orientation, self.__checkOrientation__)}
            
            flipThread = Thread(target=self.__currentTab__.doOperation, args=(Operation.OPERATION, params, self.__trans__("Flipping..."),))
            flipThread.start()
            
            __log__.debug("Flip thread started. %s" % flipThread)
        else:
            __log__.debug("There is not a tab selected")
            
        if (dialog != None):
            del dialog
    
    def __checkOrientation__(self, oldValue, addValue):
        """
        @summary: Check and correct flip orientation.
        @param oldValue: Old value.
        @param addValue: value to add to old value.
        @return: New value.  
        """
        # Checks rotation...
        if (oldValue == None):
            oldValue = Operation.NONE
        if (addValue == None):
            addValue = Operation.NONE
            
        orientation = oldValue ^ addValue
        
        if (orientation > Operation.BOTH):
            orientation -= Operation.BOTH
        elif (orientation < 0):
            orientation += Operation.BOTH
            
        return orientation
    
    def getIconsActions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {"/ToolsPyCamimg/ActionsToolItems/Flip": "flip.png",
                "/ToolsPyCamimg/ActionsToolItems/Mirror": "mirror.png",
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/Flip and Mirror": None,
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/Flip": "flip.png",
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/Mirror": "mirror.png"}
    
    def getOperationName(self):
        """
        @summary: Gets name of this operation.
        @return: String with operation name.
        """
        return Operation.OPERATION
    
    def getXmlLocation(self):
        """
        @summary: Gets xml file that contains XmlMenu and its options.
        @return: String with path 
        """
        return "flipoperation.xml"
    
    def getActions(self):
        """
        @summary: Gets a list of gtk.Action.
        @return: List of gtk.Action with actions of operations. 
        """
        return [self.__gtkActionFlip__, self.__gtkActionMirror__, self.__gtkAction__]