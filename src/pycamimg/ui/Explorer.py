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

try:
    import gtk, gobject
    import gtk.gdk
except ImportError, ioe:
    __log__.fatal("It can not import gtk, gdk module. Sure you have installed pygtk?" )
    raise ioe

try:
    from TreeExplorer import TreeExplorer
except ImportError, ioe:
    __log__.fatal("It could not import TreeExplorer. %s" % ioe)
    raise ioe
try:
    from FileExplorer import FileExplorer
except ImportError, ioe:
    __log__.fatal("It could not import FileExplorer. %s" % ioe)
    raise ioe
try:
    import UIUtils
except ImportError, ioe:
    __log__.fatal("It could not import UIUtils. %s" % ioe)
    raise ioe
try:
    import FactoryControls
except ImportError, ioe:
    __log__.fatal("It could not import FactoryControls. %s" % ioe)
    raise ioe

from pycamimg.core.Configuration import Configuration

class Explorer:
    """
    @summary: This class is an file system explorer like Nautilus
    """
    #Widgets
    __tvExplorer__ = None
    __fileExplorer__ = None
    __bBack__ = None
    __bForward__ = None
    __bUp__ = None
    __bHome__ = None

    #Separator for splitting drag&drop selection
    SEP = "\n"
    #ID of data for drag&drop
    TARGET_TEXT = 80
    MAX_STACK = 50
    
    def __init__(self, showHiddens = True):
        """
        @summary: Create an explorer.
        @param showHiddens: True if you show hidden files. Default True
        """
    
        # Initialize the stack of directories
        self.__stackDirs__ = []
        self.__currPointStack__ = -1
        self.__maxStackSize__ = self.MAX_STACK
        __log__.debug("Set size of history stack %d" % self.__maxStackSize__)
        
        self.__showHiddens__ = showHiddens
        __log__.debug("Show hiddens: %s" % showHiddens)
        
        __log__.debug("Setting controls of explorer...")
        # Generates TreeViews
        self.__tvExplorer__ = TreeExplorer(selectCallback=self.__selectDirectoryOnTreeNav__,
                                           showHiddens=self.__showHiddens__)
        __log__.debug("Created TreeExplorer. %s" % self.__tvExplorer__)
        
        self.__fileExplorer__ = FileExplorer(showHiddens=self.__showHiddens__)
        self.__fileExplorer__.setEnterDirectoryCallback(self.__enterDirectory__)
        self.__fileExplorer__.setBeginLoadCallback(self.__loading__)
        self.__fileExplorer__.setEndLoadCallback(self.__loaded__)     
        __log__.debug("Created FileExplorer. %s" % self.__fileExplorer__)
        
        self.__initUI__()
    
    def __initUI__(self):
        """
        @summary: Initialize UI of explorer.
        """
        self.__uiManager__ = None
        self.__exportControl__ = gtk.VBox()
        
        self.__initToolbar__()
        if (hasattr(self, "__toolBar__")):
            self.__exportControl__.pack_start(self.__toolBar__, False)
            
        lTreeExplorer = gtk.Label(_("<b><u>Tree</u></b>"))
        lTreeExplorer.set_use_markup(True)
        vBoxTree = gtk.VBox()
        vBoxTree.pack_start(lTreeExplorer, False)
        vBoxTree.pack_start(self.__tvExplorer__.getControl(), True, True)
            
        hPaned = gtk.HPaned()
        hPaned.add1(vBoxTree)
        hPaned.add2(self.__fileExplorer__.getControl())
        hPaned.set_position(250)
            
        # Navigator frame.
        self.__imgLoad__ = gtk.Image()
        self.__pathIcon__ = os.path.join(__ICONS_FOLDER__, "loading.gif")
        
        lNav = gtk.Label(_("<b>Navigator</b>"))
        lNav.set_use_markup(True)
        
        hBoxNav = gtk.HBox()
        hBoxNav.pack_start(self.__imgLoad__, False)
        hBoxNav.pack_start(lNav, True)
        
        fNavFrame = gtk.Frame()
        fNavFrame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        fNavFrame.set_label_widget(hBoxNav)
        fNavFrame.add(hPaned)
        
        self.__exportControl__.pack_start(fNavFrame, True, True)
        
    def __initToolbar__(self):
        """
        @summary: Initialize UI of toolbar.
        """
        actionGroupExplorer = gtk.ActionGroup("ActionGroupExplorer")
        
        # Create actions
        actionGroupExplorer.add_actions([("BackExplorerAction", gtk.STOCK_GO_BACK, _("_Back"), None, _("Go back in history"), self.__goBackEvent__),
                                         ("ForwardExplorerAction", gtk.STOCK_GO_FORWARD, _("_Forward"), None, _("Go forward in history"), self.__goForwardEvent__),
                                         ("UpExplorerAction", gtk.STOCK_GO_UP, _("Up"), None, _("Go up level in explorer"), self.__goUpLevelEvent__),
                                         ("HomeExplorerAction", gtk.STOCK_HOME, _("_Home"), None, _("Go Home"), self.__goHomeEvent__)])
        
        actionGroupExplorer.set_translation_domain(pycamimg.gettextName)
        
        __log__.debug("There is a xml path. UI Menus and tools will be recovered from path %s" % __XMLUI_FOLDER__)
        self.__uiManager__ = FactoryControls.getUIManager(os.path.join(__XMLUI_FOLDER__, "Explorer.xml"), None, actionGroupExplorer)[0]

        self.__toolBar__ = self.__uiManager__.get_widget("/ToolsExplorer")
        self.__toolBar__.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        self.__toolBar__.set_tooltips(True)
        
        self.__bBack__ = self.__uiManager__.get_widget("/ToolsExplorer/Back")
        self.__bBack__.set_is_important(True)
        self.__bForward__ = self.__uiManager__.get_widget("/ToolsExplorer/Forward")
        self.__bUp__ = self.__uiManager__.get_widget("/ToolsExplorer/Up")
        self.__bHome__ = self.__uiManager__.get_widget("/ToolsExplorer/Home")

    def __addDirToStack__(self, dir):
        """
        @summary: Adds a directory in stack
        @param dir: Path to add to history stack. 
        """
        insert = True
        if (self.__currPointStack__ > -1):
            last = self.__stackDirs__.pop(self.__currPointStack__)
            if (last != dir):
                self.__stackDirs__.insert(self.__currPointStack__, last)
            else:
                self.__currPointStack__ -= 1
            
        initial = self.__currPointStack__ + 1
        while (initial < len(self.__stackDirs__)):
            self.__stackDirs__.pop(len(self.__stackDirs__) - 1)

        self.__currPointStack__ += 1
        self.__stackDirs__.insert(self.__currPointStack__, dir)
        

        while (len(self.__stackDirs__) > self.__maxStackSize__):
            self.__stackDirs__.pop(0)
            self.__currPointStack__ -=1

        if (self.__currPointStack__ < -1):
            self.__currPointStack__ = -1

        self.enabledNavigationButtons()
    
    def __printDirectory__ (self, path):
        """
        @summary: Print a directory path.
        @param path: Path to print into explorer. 
        """
        self.__fileExplorer__.applyPath(path)
        self.__tvExplorer__.applyPathOnNav(path, True)
        __log__.debug("%s path set" % path)

    def __printCurrDirectory__(self):
        """
        @summary: Prints the current directory.
        """
        self.__printDirectory__(self.getCurrentDirectory())
        
    def __goHomeEvent__(self, b):
        """
        @summary: Goes to home directory.
        @param b: GtkButton thats generates event. 
        """
        self.goHome()
    
    def __goBackEvent__(self, b):
        """
        @summary: Goes one step back into history.
        @param b: GtkButton thats generates event. 
        """
        self.back()
        
    def __goForwardEvent__(self, b):
        """
        @summary: Goes one step forward into history.
        @param b: GtkButton thats generates event. 
        """
        self.forward()
        
    def __goUpLevelEvent__(self, b):
        """
        @summary: Goes up level from the current directory.
        @param b: GtkButton thats generates event. 
        """
        self.upLevel()
        
#TREEVIEW EVENTS
    def __selectDirectoryOnTreeNav__(self, path):
        """
        @summary: Runs when directory is selected on navigator.
        @param path: Path that it was selected. 
        """
        self.__fileExplorer__.applyPath(path)
        
#FILE EXPLORER EVENTS
    def __enterDirectory__ (self, path):
        """
        @summary: Handle enter in directory.
        @param path: Path that it was selected. 
        """
        if (os.path.isdir(path)):
            self.__addDirToStack__(path)
            self.__tvExplorer__.applyPathOnNav(path, True)
        else:
            __log__.warning("It could not recover file path.")
            
    def __loading__(self):
        """
        @summary: Update ui when explorer is loading.
        """
        UIUtils.setAnimation(self.__imgLoad__, self.__pathIcon__)
    
    def __loaded__(self):
        """
        @summary: Update ui when explorer is loaded.
        """
        UIUtils.clearImage(self.__imgLoad__)
    
#####PUBLIC METHODS#######  
    def getControl(self):
        """
        @summary: Gets control to add into a container.
        @return: GtkVBox.
        """
        return self.__exportControl__

    def getCurrentDirectory(self):
        """
        @summary: Gets current directory.
        @return: string with current directory path. No if there is not current path
        """
        if ((self.__currPointStack__ <= -1) or
            (self.__currPointStack__ >= len(self.__stackDirs__))):
            return None

        return self.__stackDirs__[self.__currPointStack__]
    
    def getSelectedFiles(self):
        """
        @summary: Gets selected files from file explorer.
        @return: An array with all selected files.
        """
        return self.__fileExplorer__.getSelectedFiles()
    
    def enabledNavigationButtons(self, glock=False):
        """
        @summary: Enabled or disabled navigation buttons.
        @param glock: True if gtk loop must be locked. 
        """
        UIUtils.enabledWidget(self.__bBack__, self.__currPointStack__ > 0, glock)
        UIUtils.enabledWidget(self.__bForward__, self.__currPointStack__ < (len(self.__stackDirs__)-1), glock)

    def refresh(self):
        """
        @summary: prints again current directory.
        """
        self.__printCurrDirectory__()

    def goHome(self):
        """
        @summary: Goes to home directory.
        """
        self.go(os.path.expanduser("~"))

    def go (self, path):
        """
        @summary: Goes to a directory.
        @param path: Path that it will be selected.
        """
        dir = None
        if (not os.path.isdir(path)):
            __log__.debug("% is not a directory. Go to parent directory." % path)
            dir, file = os.path.split(path)
            __log__.debug("% is not a directory. Go to parent directory [%s]." % (path, dir))
        else:
            dir = path
        
        if (dir != None):
            self.__addDirToStack__(dir)
            self.__printDirectory__(dir)
            
    def back (self):
        """
        @summary: Goes one step back into history.
        """
        if (self.__currPointStack__ > 0):
            self.__currPointStack__ -= 1

        self.enabledNavigationButtons()
        self.__printCurrDirectory__()
            
    def forward (self):
        """
        @summary: Goes one step forward into history.
        """
        if (self.__currPointStack__ < (len(self.__stackDirs__) - 1)):
            self.__currPointStack__ += 1

        self.enabledNavigationButtons()
        self.__printCurrDirectory__()

    def upLevel (self):
        """
        @summary: Goes up level from the current directory.
        """ 
        path = self.getCurrentDirectory()
        if (path != None):
            sPath, dir = os.path.split(path)
            if (path != sPath):
                self.__addDirToStack__(sPath)
                self.__printDirectory__(sPath)
        else:
            __log__.warning("There is not current path. It is not possible determinte which is the parent directory.")