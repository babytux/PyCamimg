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
import RotateOperation
from RotateOperation.RotateDialog import RotateDialog
from RotateOperation import Operation

import gettext
import RotateOperation.camimgplugin
    

class CamimgPlugin(IOperationPlugin.OperationPlugin):
    """
    @summary: Defines rotate operation.
    """
    def __init__(self):
        """
        @summary: Creates new rotate operation plugin.
        """
        self.__gtkAction__ = gtk.Action("RotateAction", self.__trans__("Rotate Images"), self.__trans__("Rotate selected images"), None)
        self.__gtkAction__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkAction__.set_tool_item_type(gtk.ToolButton)
        
        self.__gtkActionLeft__ = gtk.Action("RotateLeftAction", self.__trans__("Rotate On Left"), self.__trans__("Rotate selected images on the left"), None)
        self.__gtkActionLeft__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkActionLeft__.set_tool_item_type(gtk.ToolButton)
        
        self.__gtkActionRight__ = gtk.Action("RotateRightAction", self.__trans__("Rotate On Right"), self.__trans__("Rotate selected images on the right"), None)
        self.__gtkActionRight__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkActionRight__.set_tool_item_type(gtk.ToolButton)
    
    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(RotateOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)    
        
    def callbackAction(self, action, currentTab, userData = None):
        """
        @summary: Callback that will be thrown when any action is actived.
        @param action: gtk.Action activated.
        @param currentTab: Current Tab. pycamimg.ui.TabProject.TabProject
        @param userData: User data
        """
        if ((action.get_name() != "RotateAction") and 
            (action.get_name() != "RotateLeftAction") and 
            (action.get_name() != "RotateRightAction")):
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
            if (action.get_name() == "RotateLeftAction"):
                self.__doRotate__(None, 90)
            elif(action.get_name() == "RotateRightAction"):
                self.__doRotate__(None, 270)
            elif(action.get_name() == "RotateAction"):
                rotateDialog = RotateDialog(callback = self.__doRotate__,
                                            parent = parentWindow)
                if (iNRows == 1):
                    iter = model.get_iter(paths[0])
                    itemPath = model.get_value(iter, self.__currentTab__.COLUMN_SOURCE)
                    item = self.__currentTab__.getCore().getItem(itemPath)
                    rotateDialog.setData(item)
                __log__.debug("Rotate dialog created. %s" % rotateDialog )
                rotateDialog.run()
            pass
        else:
            FactoryControls.getMessage(self.__trans__("Select one or more items"), 
                                       title=self.__trans__("Rotate"),
                                       parent = parentWindow)
        
        return
    
    def __doRotate__(self, dialog, degrees, plusDegrees = False):
        """
        @summary: Handle response of rotate dialog, 
                    when user want to rotate some images
        """
        if (self.__currentTab__ != None):
            params = {"degrees":(degrees, self.__checkRotation__), "filter":(Image.BICUBIC, None)}
            
            rotateThread = Thread(target=self.__currentTab__.doOperation, args=(Operation.OPERATION, params, self.__trans__("Rotating..."),))
            rotateThread.start()
            
            __log__.debug("Rotate thread started. %s" % rotateThread)
        else:
            __log__.debug("There is not a tab selected")
            
        if (dialog != None):
            del dialog
    
    def __checkRotation__(self, oldValue, addValue):
        """
        @summary: Check and correct rotation.
        @param oldValue: Old value.
        @param addValue: value to add to old value.
        @return: New value.  
        """
        # Checks rotation...
        if (oldValue == None):
            oldValue = 0
        if (addValue == None):
            addValue = 0
            
        rotation = oldValue + addValue
        
        if (rotation >= 360):
            rotation -= 360
        elif (rotation < 0):
            rotation += 360
            
        return rotation
    
    def getIconsActions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {"/ToolsPyCamimg/ActionsToolItems/Rotate": "rotate.png",
                "/ToolsPyCamimg/ActionsToolItems/RotateLeft": "rotateLeft.gif",
                "/ToolsPyCamimg/ActionsToolItems/RotateRight": "rotateRight.gif",
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/Rotate": "rotate.png",
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/RotateLeft": "rotateLeft.gif",
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/RotateRight": "rotateRight.gif"}
    
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
        return "rotateoperation.xml"
    
    def getActions(self):
        """
        @summary: Gets a list of gtk.Action.
        @return: List of gtk.Action with actions of operations. 
        """
        return [self.__gtkActionLeft__, self.__gtkActionRight__, self.__gtkAction__]