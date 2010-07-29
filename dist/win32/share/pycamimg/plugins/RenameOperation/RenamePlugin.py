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
from pycamimg.util.IOUtils import IOUtils
import RenameOperation
from RenameOperation.RenameDialog import RenameDialog
from RenameOperation import Operation
    
import gettext
import RenameOperation.camimgplugin

class CamimgPlugin(IOperationPlugin.OperationPlugin):
    """
    @summary: Defines rename operation.
    """
    def __init__(self):
        """
        @summary: Creates new rename operation plugin.
        """
        self.__gtkAction__ = gtk.Action("RenameAction", self.__trans__("Rename Images"), self.__trans__("Rename selected images"), None)
        self.__gtkAction__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkAction__.set_tool_item_type(gtk.ToolButton)
    
    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(RenameOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)
      
    def callbackAction(self, action, currentTab, userData = None):
        """
        @summary: Callback that will be thrown when any action is actived.
        @param action: gtk.Action activated.
        @param currentTab: Current Tab. pycamimg.ui.TabProject.TabProject
        @param userData: User data
        """
        if (action.get_name() != "RenameAction"):
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
            renameDialog = RenameDialog(iNRows, 
                                        callback = self.__doRename__,
                                        parent = parentWindow)
            __log__.debug("Rename dialog created. %s" % renameDialog )
            renameDialog.run()
        else:
            FactoryControls.getMessage(self.__trans__("Select one or more items"), 
                                       title=self.__trans__("Rename"),
                                       parent = parentWindow)
        
        return
    
    def __doRename__(self, dialog, format, initial):
        """
        @summary: Handle response of rename dialog, 
                    when user want to rename some images
        """
        if (self.__currentTab__ != None):
            value = (format, initial)
            params = {"target": (value, self.__applyNumber__), }
            
            renameThread = Thread(target=self.__currentTab__.doOperationOnItem, args=(Operation.OPERATION, params, _("Renaming..."),))
            renameThread.start()
            
            __log__.debug("Rename thread started. %s" % renameThread)
        else:
            __log__.debug("There is not a tab selected")
            
        if (dialog != None):
            del dialog
        
    def __applyNumber__(self, item, iter, count, key, value):
        """
        @summary: Apply a number to a item.
        @param item: pycamimg.core.CamItem.CamItem
        @param iter: GtkTreeIter.
        @param count: Current item. 
        @param value: Tuple of format and initial. 
        """
        format, initial = value
        ioUtils = IOUtils()
        
        ext = ioUtils.getExtension(item.getPath()) 
        
        if (initial != -1):
            return "%s%s" % (format % (initial + count), ext)
        else:
            return "%s%s" % (format, ext)
    
    def getIconsActions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {"/ToolsPyCamimg/ActionsToolItems/Rename": "rename.gif",
                "/MenuPyCaming/ToolsMenu/Operations/OperationsMenuAdditions/Rename": "rename.gif"}
    
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
        return "renameoperation.xml"
    
    def getActions(self):
        """
        @summary: Gets a list of gtk.Action.
        @return: List of gtk.Action with actions of operations. 
        """
        return [self.__gtkAction__]