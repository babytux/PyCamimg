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
from pycamimg.ui import FactoryControls
from pycamimg.util.ImgMeta import ImgMeta
from pycamimg.util import ImageUtils
from ResizeOperation.ResizeDialog import ResizeDialog
from ResizeOperation import Operation

import gettext
import ResizeOperation.camimgplugin
    

class CamimgPlugin(IOperationPlugin.OperationPlugin):
    """
    @summary: Defines resize operation.
    """
    def __init__(self):
        """
        @summary: Creates new resize operation plugin.
        """
        self.__gtkAction__ = gtk.Action("ResizeAction", self.__trans__("Resize Images"), self.__trans__("Resize selected images"), None)
        self.__gtkAction__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkAction__.set_tool_item_type(gtk.ToolButton)
      
    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(ResizeOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)
      
    def callbackAction(self, action, currentTab, userData = None):
        """
        @summary: Callback that will be thrown when any action is actived.
        @param action: gtk.Action activated.
        @param currentTab: Current Tab. pycamimg.ui.TabProject.TabProject
        @param userData: User data
        """
        if (action.get_name() != "ResizeAction"):
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
            resizeDialog = ResizeDialog(callback = self.__doResize__,
                                        parent = parentWindow)
            __log__.debug("Resize dialog created. %s" % resizeDialog)
            if (iNRows > 1):
                resizeDialog.setData(100.0, 100.0, ImageUtils.PERCENT)
            else:
                path = paths[0]
                iter = model.get_iter(path)
                file = model.get_value(iter, 1)
                
                size = (100.0, 100.0)
                scale = ImageUtils.PERCENT
                
                resizeNew = True

                item = currentTab.getCore().getItem(file)
                if (item != None):
                    op = item.getOperation(Operation.OPERATION)
                    if (op != None):
                        size = (op.getParameter("width"), op.getParameter("height"))
                        scale = op.getParameter("scale")
                        if (scale == ImageUtils.PERCENT):
                            meta = ImgMeta(file)
                            srcSize = meta.getSize()
                            size = (
                                srcSize[0] * (size[0] / float(100)),
                                srcSize[1] * (size[1] / float(100)))
                            scale = ImageUtils.PIXEL
                            
                        resizeDialog.setData(size[0],size[1],scale,srcSize)
                        resizeNew = False
                if (resizeNew):
                    meta = ImgMeta(file)
                    size = meta.getSize()
                    scale = ImageUtils.PIXEL
                    resizeDialog.setData(size[0], size[1], scale)
                
            resizeDialog.run()
        else:
            FactoryControls.getMessage(self.__trans__("Select one or more items"), 
                                       title=self.__trans__("Resize"),
                                       parent = parentWindow)
        
        return
    
    def __doResize__(self, dialog, width, height, unit):
        """
        @summary: Handle response of resize dialog, 
                    when user want to resize some images
        """
        if (self.__currentTab__ != None):
            params = {"width": (width, None), "height": (height, None), "scale": (unit, None), "filter": (Image.ANTIALIAS, None)}
            
            resizeThread = Thread(target=self.__currentTab__.doOperation, args=(Operation.OPERATION, params, self.__trans__("Resizing..."),))
            resizeThread.start()
            __log__.debug("Resize thread started. %s" % resizeThread)
        else:
            __log__.debug("There is not a tab selected")
            
        del dialog
    
    def getIconsActions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {"/ToolsPyCamimg/ActionsToolItems/Resize": "resize.png",
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/Resize": "resize.png"}
    
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
        return "resizeoperation.xml"
    
    def getActions(self):
        """
        @summary: Gets a list of gtk.Action.
        @return: List of gtk.Action with actions of operations. 
        """
        return [self.__gtkAction__]