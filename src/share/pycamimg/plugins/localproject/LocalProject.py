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
import shutil
import logging

if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

import gettext
import localproject.camimgplugin

from pycamimg.core.plugins import IProjectType
from pycamimg.ui import FactoryControls

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

import os.path

class CamimgPlugin(IProjectType.Project):
    """
    @summary: Defines local project structure.
    """
    
    def __init__(self):
        """
        Initialize plugin.
        """
        self.ACTION_COPY = 0
        self.ACTION_MOVE = 1
        
        self.__action__ = self.ACTION_COPY
        self.__mainWindow__ = None
        self.__target__ = None
        self.__gtkAction__ = gtk.Action("LocalProjectAction", self.__trans__("Local Project"), self.__trans__("Create new local project"), None)
        self.__gtkAction__.set_menu_item_type(gtk.ImageMenuItem)

        self.__gtkActionTarget__ = gtk.Action("SelectTargetAction", self.__trans__("Target Folder"), self.__trans__("Select a target folder"), gtk.STOCK_DIRECTORY)
        self.__gtkActionTarget__.connect("activate", self.__selectTargetEvent__)

    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(localproject.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)

    def __selectTargetEvent__(self, b):
        """
        @summary: Process select target event.
        @param b: Action associated with event. 
        """
        self.setTargetFolder(doBlock=False)
    
    def setBlockWindow(self, window):
        """
        @summary: Sets window as parent window.
        """
        self.__mainWindow__ = window
    
    def setTargetFolder(self, doBlock=True):
        """
        @summary: Create a selection folder dialog 
            and set selected folder as target folder
        @param doBlock: True to block gtk-loop. 
        """
        if (doBlock):
            gtk.gdk.threads_enter()
        try:
            targetSel = gtk.FileChooserDialog(title=self.__trans__("Target folder"),
                                              parent=self.__mainWindow__,
                                              action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                              buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                       gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        
            targetSel.set_default_response(gtk.RESPONSE_CANCEL)
            targetSel.set_modal(True)
            targetSel.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            if (self.__target__ != None):
                __log__.debug("Set target before open. %s" % self.__target__)
                targetSel.set_current_folder(self.__target__)
            targetSel.show()
            if (targetSel.run() == gtk.RESPONSE_ACCEPT):
                self.__target__ = targetSel.get_current_folder()
                filename = targetSel.get_filename()
                if (filename != None):
                    self.__target__ = os.path.join(self.__target__, filename)
                __log__.info("Set %s as target folder" % self.__target__)
        finally:
            if (doBlock):
                gtk.gdk.threads_leave()
            targetSel.destroy()
    
    def getAction(self):
        """
        @summary: Gets action on local project.
        @return: ACTION_COPY or ACTION_MOVE.
        """
        return self.__action__
    
    def setAction(self, action):
        """
        @summary: Sets action on local project.
        @param action: ACTION_COPY or ACTION_MOVE.
        """
        self.__action__ = action
    
    def getIconName(self):
        """
        @summary: Gets name of icon that represents this project type.
        @return: String with icon name
        @note: Always return 'pycamimg.png'. 
        """
        return "pycamimg.png"
    
    def getXmlLocation(self):
        """
        @summary: Gets xml file that contains XmlMenu and its options.
        @return: String with path 
        """
        return "localproject.xml"
    
    def getGtkAction(self):
        """
        Gets gtk.Action of project
        """
        return self.__gtkAction__
    
    def getTypeName(self):
        """
        @summary: Gets name of this project type.
        @return: String with type name.
        @note: Always return 'Local Project'.
        """
        return "LocalProject"
    
    def hasOptions(self):
        """
        @summary: Gets if the type of project has any option.
        @return: True when it has any option.
        """
        return True
    
    def getStringUIManager(self):
        """
        @summary: Gets string to add to UIManager.
        @return: str with menus.
        """
        return '<ui><toolbar name="ToolsExecute"><placeholder name="ExecuteToolItems"> \
                <toolitem name="SelectTarget" action="SelectTargetAction" /> \
                </placeholder></toolbar></ui>'
    
    def getIconsOptions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {}
    
    def getOptions(self):
        """
        @summary: Gets options of the project.
        @return: List of gtk.Actin. None if there are not options 
        """
        return [self.__gtkActionTarget__]
        
    
    def PreDoProject(self, core, blockWindow=None):
        """
        @summary: Execute before items of project process.
        @param core: CamCore to execute.
        @param blockWindow: GtkWindow to block by any dialog.
        @return: True if all is right.
        """
        self.__mainWindow__ = blockWindow
        if (self.__target__ == None):
            __log__.debug("Target folder is not defined, executing target callback.")
            self.setTargetFolder(doBlock=False)
            if (self.__target__ == None):
                __log__.debug("There is not target folder")
                FactoryControls.getMessage(
                    self.__trans__("Target folder is not defined."), 
                    title=self.__trans__("Execute"),
                    type=gtk.MESSAGE_ERROR,
                    parent=self.__mainWindow__,
                    gtkLock=False)
                
                __log__.debug("Target folder is not defined, exiting from execute dialog.")
                return False
        return True
    
    def PostDoItem(self, source):
        """
        @summary: Execute after operations.
        @param source: source file.
        @return: True if it is all right 
        """
        if (self.__target__ == None):
            __log__.debug("Target folder is not defined. %s was not processed." % source)
            return False
        else:
            head, filename = os.path.split(source)
            newFile = os.path.join(self.__target__, filename)
            shutil.move(source, newFile)
            __log__.debug("Move file from %s to %s" % (source, newFile))
        
        return True