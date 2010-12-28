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
import logging
import pycamimg
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
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e

import threading, thread
from threading import Thread
import time

from pycamimg.util.ImgMeta import ImgMeta
from pycamimg.util import FactoryDirectoryMonitor
import FactoryControls
import UIUtils
from OptionsDialog import OptionsDialog
from OperationsDialog import OperationsDialog
from PluginsDialog import PluginsDialog
import ExecuteWindow
from ExecuteWindow import ExecuteWindow
from Explorer import Explorer
from RegOperations import RegOperations
from TabProject import TabProject
from pycamimg.core.operations import Operations
from pycamimg.core.operations.Operations import Operation
from pycamimg.core.CamCore import CamCore
from pycamimg.core.plugins import Loader
from pycamimg.core.Configuration import Configuration

class MainWindow:
    
    PYCAMIMG_FILE_EXTENSION = ".cmmg"
    PYCAMIMG_TITLE = "PyCamimg"
    
    __DEFAULT_WINDOW_WIDTH__ = 800
    __DEFAULT_WINDOW_HEIGHT__ = 600
    
    def __init__(self, 
                 cores, 
                 domain=None,
                 languages=None,
                 currentLang=None,
                 setLanguage=None):
        """
        @summary: Initialize PyCamimg main window.
        @param cores: List of preloaded CamCores.
        @param domain: GetText domain to use.
        @param languages: List of languages that it can use.
        @param currentLang: Current language of the list.
        @param setLanguage: Function reference to set new language.     
        """
        #Initialize current tab
        self.__lsTabs__ = []
        self.__currentTab__ = None

        # Language configuration
        self.__langs__ = languages
        self.__currLang__ = currentLang

        # Set pycamimg domain if domain is None
        if (domain == None):
            domain = pycamimg.gettextName

        # Initialize UI
        self.__initUI__(domain)
        
        #Initialize other treeviews
        self.__initTargets__(cores)

    def __initUI__(self, domain):
        """
        @summary: Initialize UI of PyCamimg.
        @param domain: GetText domain to use.
        """
        self.__menuBar__ = None
        self.__toolBar__ = None
        
        __log__.debug("Initializing UI...")        
        # Create the toplevel window
        self.__mainWindow__ = gtk.Window()
        self.__mainWindow__.connect("destroy", self.__quitEvent__)
        self.__mainWindow__.connect("delete-event", self.__queryQuitEvent__)
        self.__mainWindow__.set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)
        self.__mainWindow__.set_title(self.PYCAMIMG_TITLE)
        self.__mainWindow__.set_icon_from_file(os.path.join(__ICONS_FOLDER__, "pycamimg.png"))
        
        vbox = gtk.VBox()
        self.__mainWindow__.add(vbox)
        
        self.__initUIMenu__(domain)
        
        if (self.__menuBar__ != None):
            vbox.pack_start(self.__menuBar__, False)
        
        # Recovers TreeViews
        self.__eExplorer__ = Explorer(showHiddens=Configuration().getConfiguration().getboolean("NAVIGATOR", "show_hiddens"))
        __log__.debug("\tExplorer widget: %s" % self.__eExplorer__)
        
        # Enabled navigator buttons (back and forward buttons)
        self.__eExplorer__.enabledNavigationButtons()
        
        #self.__eExplorer__.goHome()
        __log__.debug("Went to home directory");
        
        self.__operations__ = RegOperations()
        __log__.debug("\tOperations widget: %s" % self.__operations__)
        
        hPaned = gtk.HPaned()
        hPaned.set_position(int(self.__DEFAULT_WINDOW_WIDTH__ * 0.85))
        hPaned.pack1(self.__eExplorer__.getControl())
        hPaned.pack2(self.__operations__.getControl(), False, True)
        
        vBoxWorkArea = gtk.VBox()
        if (self.__toolBar__ != None):
            vBoxWorkArea.pack_start(self.__toolBar__, False)
            
        self.__nbProjects__ = gtk.Notebook()
        self.__nbProjects__.set_tab_pos(gtk.POS_TOP)
        self.__nbProjects__.set_scrollable(True)
        self.__nbProjects__.set_show_border(True)
        self.__nbProjects__.connect("switch-page", self.__changeProjectEvent__)
        __log__.debug("Project Notebook: %s" % self.__nbProjects__)
        
        vBoxWorkArea.pack_start(self.__nbProjects__, True, True)
        
        vPaned = gtk.VPaned()
        vPaned.set_position(int(self.__DEFAULT_WINDOW_HEIGHT__ * 0.40))
        
        vPaned.add1(hPaned)
        vPaned.add2(vBoxWorkArea)
        
        vbox.pack_start(vPaned, True, True)
        
        
        self.__statBar__ = gtk.Statusbar()
        self.__statBar__.set_has_resize_grip(True)
        
        vbox.pack_start(self.__statBar__, False)
        
        #Search project plugins, that define the kind of project.
        self.__searchPlugins__()
        
        self.__enableOptions__(blockGtk=False)
    
    def __initUIMenu__(self, domain):
        """
        @summary: Initialize menu of window. 
        @param domain: Domain used to translation.
        """
        actionGroupMenu = gtk.ActionGroup("ActionGroupMenu")
        
        # Create actions
        actionGroupMenu.add_actions([("FileMenuAction", None, _("_File")),
                                     ("NewProjectAction", None, _("New Project")), 
                                     ("OpenProjectAction", gtk.STOCK_OPEN, _("_Open"), "<Control>o", _("Open PyCamimg project"), self.__openProjectEvent__),
                                     ("SaveProjectAction", gtk.STOCK_SAVE, _("_Save"), "<Control>s", _("Save current project"), self.__saveProjectEvent__),
                                     ("SaveAsProjectAction", gtk.STOCK_SAVE_AS, _("Save _As"), None, _("Save current project"), self.__saveAsProjectEvent__),
                                     ("QuitAction", gtk.STOCK_QUIT, _("_Quit"), "<Control>q", _("Quit PyCamimg"), self.__queryQuitMenuItemEvent__),
                                     ("ToolsMenuAction", None, _("_Tools")),
                                     ("OperationsAction", None, _("Operations")),
                                     ("PreferencesAction", gtk.STOCK_PREFERENCES, _("_Preferences"), None, _("Preferences of PyCamimg"), self.__openOptionsEvent__),
                                     ("PluginsAction", gtk.STOCK_CONNECT, _("P_lugins"), None, _("Plugins of PyCamimg"), self.__openPlunginsEvent__),
                                     ("HelpMenuAction", None, _("_Help")),
                                     ("AboutAction", gtk.STOCK_ABOUT, _("_About PyCamimg"), None, _("Preferences of PyCamimg"), self.__openAboutEvent__),
                                     ("AddItemAction", gtk.STOCK_ADD, _("Add Images"), None, _("Add selected images"), self.__addImageEvent__),
                                     ("DelItemAction", gtk.STOCK_DELETE, _("Delete Images"), None, _("Delete selected images"), self.__deleteImageEvent__),
                                     ("DelOperationsAction", gtk.STOCK_CLEAR, _("Delete Operations"), None, _("Delete selected operations"), self.__deleteOperationsEvent__),
                                     ("RunAction", gtk.STOCK_EXECUTE, _("Run"), None, _("Run current project"), self.__runEvent__)])
        actionGroupMenu.add_toggle_actions([("ChangeViewAction", gtk.STOCK_CONVERT, _("Toggle view"), None, _("Toggle between differents views"), self.__changeViewProjectEvent__)])

        actionGroupMenu.set_translation_domain(domain)
        
        __log__.debug("There is a xml path. UI Menus and tools will be recovered from path %s" % __XMLUI_FOLDER__)
        print __XMLUI_FOLDER__
        self.__uiManager__ = FactoryControls.getUIManager(os.path.join(__XMLUI_FOLDER__, "MainMenu.xml"), self.__mainWindow__, actionGroupMenu)[0]
        
        self.__menuBar__ = self.__uiManager__.get_widget("/MenuPyCaming")
        self.__toolBar__ = self.__uiManager__.get_widget("/ToolsPyCamimg")
        self.__toolBar__.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        self.__toolBar__.set_tooltips(True)
        

    
    def __searchPlugins__(self):
        """
        @summary: Search plugins of PyCamimg.
        """
        self.__searchProjectPlugins__()
        self.__searchOperationsPlugins__()
    
    def __searchProjectPlugins__(self):
        """
        @summary: Search new kind of projects, and create a menu item for each.
        """
        __log__.debug("Project modules are loaded")
        
        projectTypes = Loader.getPluginsType(pycamimg.core.plugins.ICamimgPlugin.PLUGIN_TYPE.PROJECT)
        actionGroupProjectPlugins = gtk.ActionGroup("ActionGroupProjectPlugins")
        self.__uiManager__.insert_action_group(actionGroupProjectPlugins, pos=-1)
        
        for project in projectTypes:
            __log__.debug("Processing plugin %s" % project[Loader.INDEX_PLUGIN].getName())    
                        
            projectInstance = project[Loader.INDEX_PLUGIN_INSTANCE]()
            __log__.debug("Creating new menu item for project type %s" % projectInstance.getTypeName())
            
            aAction = projectInstance.getGtkAction()
            if (aAction != None):
                aAction.connect("activate", self.__newProjectEvent__, project[Loader.INDEX_PLUGIN_INSTANCE])
                __log__.debug("Add activate signal to  %s" % projectInstance.getTypeName())
                actionGroupProjectPlugins.add_action(aAction)
            else:
                __log__.debug("There is not action for %s" % projectInstance.getTypeName())
                
            if (projectInstance.getXmlLocation() != ""):
                self.__uiManager__.add_ui_from_file(os.path.join(__XMLUI_FOLDER__, projectInstance.getXmlLocation()))
            
                mi = self.__uiManager__.get_widget("/MenuPyCaming/FileMenu/NewProject/NewProjectAdditions/%s" % projectInstance.getTypeName())
                if (mi != None):
                    iconPath = os.path.join(__ICONS_FOLDER__, projectInstance.getIconName())
                    __log__.debug("Get project icon from %s" % iconPath)
                    UIUtils.setImageToMenuItem(mi, iconPath, doGObject=False)
                else:
                    __log__.warning("It could not update icon of %s. Action name %s was not found." % (projectInstance.getTypeName(), projectInstance.getTypeName()))
            else:
                __log__.debug("%s is not in menu." % projectInstance.getTypeName())
                
            __log__.debug("Added new project type %s" % projectInstance.getTypeName())
            
    def __searchOperationsPlugins__(self):
        """
        @summary: Search operations, and create a menu item for each.
        """
        __log__.debug("Project modules are loaded")
        
        operationsPlugins = Loader.getPluginsType(pycamimg.core.plugins.ICamimgPlugin.PLUGIN_TYPE.OPERATION)
        actionGroupOperationPlugins = gtk.ActionGroup("ActionGroupOperationPlugins")
        self.__uiManager__.insert_action_group(actionGroupOperationPlugins, pos=-1)
        
        for operation in operationsPlugins:
            __log__.debug("Processing plugin %s" % operation[Loader.INDEX_PLUGIN])    
                        
            operationInstance = operation[Loader.INDEX_PLUGIN_INSTANCE]()
            __log__.debug("Creating operation %s" % operationInstance.getOperationName())
            
            lActions = operationInstance.getActions()
            if (lActions != None):
                for aAction in lActions:
                    aAction.connect("activate", self.__activateOperation__, operationInstance.callbackAction)
                    __log__.debug("Add activate signal to  %s" % operationInstance.getOperationName())
                    actionGroupOperationPlugins.add_action(aAction)
            else:
                __log__.debug("There is not action for %s" % operationInstance.getOperationName())
                
            if (operationInstance.getXmlLocation() != ""):
                self.__uiManager__.add_ui_from_file(os.path.join(__XMLUI_FOLDER__, operationInstance.getXmlLocation()))
                
                dIcons = operationInstance.getIconsActions()
                for actionPath, iconPath in dIcons.iteritems():
                    mi = self.__uiManager__.get_widget(actionPath)
                    if (mi != None): 
                        iconPath = os.path.join(__ICONS_FOLDER__, iconPath)            
                        __log__.debug("Get project icon from %s" % iconPath)
                        if (isinstance(mi, gtk.ImageMenuItem)):
                            UIUtils.setImageToMenuItem(mi, iconPath, doGObject=False)
                        elif (isinstance(mi, gtk.ToolButton)):
                            UIUtils.setImageToToolItem(mi, iconPath, size=self.__toolBar__.get_icon_size(), doGObject=False)
                        else:
                            __log__.warning("Unknown type control.")
                    else:
                        __log__.warning("It could not update icon of %s. Action name %s was not found." % (operationInstance.getOperationName(), actionPath))
            else:
                __log__.debug("%s is not in menu." % operationInstance.getOperationName())
                
            __log__.debug("Added new operation %s" % operationInstance.getOperationName())
    
    
### INITIALIZE TreeViews ###
    def __initTargets__(self, cores):
        """
        @summary: Initialize tabs.
        @param cores: A list of cores that are preloaded. 
        """
        for core in cores:
            self.__addNewProject__(core)
        __log__.info("Initialized target projects")
            
    def __addNewProject__(self, core=None, threadBlock = True, focused = False, projectType=None):
        """
        @summary: Add new project.
        @param core: Core that will be added. Default value is None
        @param threadBlock: True if it will be locked gtk-loop. Default True
        @param focused: True if new tab project will get the focus.
        """
        __log__.debug("Add new project: core=%s | threadBlock=%s | focused=%s | projectType=%s" % (core, threadBlock, focused, projectType))
        if (core == None):
            core = CamCore(temp=__TEMP_FOLDER__, projectType=projectType)
            __log__.debug("New core created. %s" % core)
            
        text = ""
        if (core.getName() == ""):    
            text = "%s_%d" % (_("Project"), len(self.__lsTabs__))
        else:
            text = core.getName()
        __log__.info("Project name %s" % text)
        tab = TabProject(core, name=text, iconsPath=os.path.join(__ICONS_FOLDER__), 
                         iconName=core.getProjectType().getIconName())
        tab.setCloseCallback(self.__closeProject__)
        __log__.debug("Callbacks set")
        core.setName(text)
        tab.addToNotebook(self.__nbProjects__, threadBlock = threadBlock, focused = focused)
        tab.load()
        
        self.__lsTabs__.append(tab)
        
        if (self.__currentTab__ == None):
            __log__.debug("There is not current tab. It will set %s as current tab." % core.getName())
            self.__currentTab__ = tab
        
        __log__.debug("New project added to project notebook")
        
        self.__enableOptions__(blockGtk=threadBlock)
                
    def __closeProject__(self, index):
        """
        @summary: Runs when project is closed.
        @param index: Index of project that will be closed. 
        """
        __log__.debug("Close project %d" % index)
        
        tab = self.__lsTabs__[index]
        if (tab != None):
            core = tab.getCore()
            if (core != None):
                __log__.debug("%s will be deleted" % core.getName())
                del core
                core = None
            self.__lsTabs__.remove(tab)
            if (tab == self.__currentTab__):
                self.__currentTab__ = None
            tab.closeTab()            
            del tab
            __log__.debug("Tab was closed and core was deleted")
        else:
            __log__.warn("Index %d does not exist" % index)
        
        self.__enableOptions__(blockGtk=False)
    
    def __refreshProjects__(self):
        """
        @summary: Refresh all open projects.
        """
        for tbTab in self.__lsTabs__:
            if (tbTab != None):
                tbTab.load()
                __log__.debug("Core %s reloaded" % tbTab.getCore().getName())
                
    
    def __enableOptions__(self, blockGtk=True):
        """
        @summary: Enable or disable all options.
        """
        enable = (self.__currentTab__ != None)
        
        toolbar = self.__uiManager__.get_widget("/ToolsPyCamimg")
        imiSave = self.__uiManager__.get_widget("/MenuPyCaming/FileMenu/SaveProject")
        imiSaveAs = self.__uiManager__.get_widget("/MenuPyCaming/FileMenu/SaveAsProject")
        iOptions = 0
        
        mOperations = self.__uiManager__.get_widget("/MenuPyCaming/ToolsMenu/Operations")
        if (mOperations != None):
            if (mOperations.get_submenu() != None):
                __log__.debug("Enabling operations of operation menu")
                mOperations.get_submenu().foreach(lambda mi: UIUtils.enabledWidget(mi, enable, blockGtk) )
            else:
                __log__.debug("Operation menu does not have menu")
                        
        if (toolbar != None):
            iOptions = toolbar.get_n_items()
            
        if (iOptions > 0):
            for i in range(0, iOptions):
                itItem = toolbar.get_nth_item(i)
                if (itItem != None):
                    if (blockGtk):
                        gtk.gdk.threads_enter()
                    try:
                        itItem.set_sensitive(enable)
                    finally:
                        if (blockGtk):
                            gtk.gdk.threads_leave()
                else:
                    __log__.warning("It could not recover item of index %d" % i)
        else:
            __log__.debug("There are not options.")
            
        if (imiSave != None):
            imiSave.set_sensitive(enable)
            
        if (imiSaveAs != None):
            imiSaveAs.set_sensitive(enable)
            
           
    def __updateTitle__(self, threadBlock = False):
        """Update title of the window"""
        title = ""
        if (self.__currentTab__ != None):
            if (self.__currentTab__.getCore().getFilename() != None):
                title = "%s - %s - %s" % (self.__currentTab__.getCore().getName(), 
                                          self.__currentTab__.getCore().getFilename(),
                                          self.PYCAMIMG_TITLE)
            else:
                title = "%s - %s" % (self.__currentTab__.getCore().getName(), self.PYCAMIMG_TITLE)
        else:
            title = self.PYCAMIMG_TITLE
            
        __log__.debug("New window title %s" % title)

        UIUtils.setTitleWindow(self.__mainWindow__, title, doGObject=threadBlock)

#####PUBLIC METHODS#######
# TOOLBAR ITEMS: CLICK EVENT

    def __addImageEvent__ (self, b):
        """
        @summary: Add into target TreeView selected files from the files TreeView.
        @param b: Button that threw event. 
        """
        files = self.__eExplorer__.getSelectedFiles()
        if (self.__currentTab__ != None):
            # Send files to target TreeView
            addThread = Thread(target=self.__currentTab__.addTargetFiles, args=(files,))
            addThread.start()
            __log__.debug("Add thread started. %s" % addThread)
        else:
            __log__.debug("There is not a tab selected")

    def __deleteImageEvent__ (self, b):
        """
        @summary: Delete files from target TreeView.
        @param b: Button that threw event.
        """
        if (self.__currentTab__ != None):
            delThread = Thread(target=self.__currentTab__.deleteSelectedImages, args=())
            delThread.start()
            __log__.debug("Delete thread started. %s" % delThread)
        else:
            __log__.debug("There is not a tab selected")

    def __deleteOperationsEvent__ (self, b):
        """
        @summary: Delete operations of an item.
        @param b: Button that threw event.
        """
        if (self.__currentTab__ == None):
            __log__.debug("There is not current project")
            return
        
        paths = self.__currentTab__.getSelection()
        model = self.__currentTab__.getModel()
        if ((paths == None) or (model == None)):
            __log__.error("It can not recover tree selection. Set selection at 0.")
            iNRows = 0
        else:
            iNRows = len(paths)
        
        if iNRows > 0:
            path = paths[0]
            iter = model.get_iter(path)
            if (iter != None):
                file = model.get_value(iter, self.__currentTab__.COLUMN_SOURCE)
                item = self.__currentTab__.getCore().getItem(file)
                operationsDialog = OperationsDialog(
                                    item,
                                    iter,
                                    callback = self.__applyDeleteOperationsItemCallback__,
                                    parent = self.__mainWindow__)
        
                __log__.debug("Operations dialog created. %s" % operationsDialog)
                operationsDialog.run()
                del operationsDialog
            else:
                __log__.error("It can not recover iter from path %s. Abort open delete operations dialog." % path)
                FactoryControls.getMessage(_("It can not get item"), 
                                           title=_("Delete operations"),
                                           type=gtk.MESSAGE_ERROR,
                                           parent = self.__mainWindow__)
            
        else:
            FactoryControls.getMessage(_("Select one item"), 
                                       title=_("Delete operations"),
                                       parent = self.__mainWindow__)

    def __applyDeleteOperationsItemCallback__(self, item, iter):
        """
        @summary: Apply changes on item.
        @param item: Item that has changes. 
        @param iter: Iter where item is. 
        """
        if ((item != None) and (iter != None)):
            self.__currentTab__.updateItemDescription(iter, item, gtkLock=False)

    def openPreview (self, b):
        """
        @summary: Open image.
        @param b: Button that threw event. 
        """
        
        if (self.__currentTab__ == None):
            __log__.debug("There is not current project")
            return
        
        paths = self.__currentTab__.getSelection()
        model = self.__currentTab__.getModel()
        if ((paths == None) or (model == None)):
            __log__.error("It can not recover tree selection. Set selection at 0.")
            iNRows = 0
        else:
            iNRows = len(paths)
        
        if iNRows > 0:
            path = paths[0]
            iter = model.get_iter(path)
            if (iter != None):
                file = model.get_value(iter, 1)
                meta = ImgMeta(file)
                meta.show()
            else:
                __log__.error("It can not recover iter from path %s. Abort preview" % path)
                FactoryControls.getMessage(_("It can not show image"), 
                                           title=_("Preview"),
                                           type=gtk.MESSAGE_ERROR,
                                           parent = self.__mainWindow__)
            
        else:
            FactoryControls.getMessage(_("Select one item"), 
                                       title=_("Preview"),
                                       parent = self.__mainWindow__)

    def __openPlunginsEvent__(self, b):
        """
        @summary: Open plugins window.
        @param b: Button that threw event.
        """
        pluginsDialog = PluginsDialog(parent = self.__mainWindow__)
        __log__.debug("Plugins dialog created. %s" % pluginsDialog)
        pluginsDialog.run()
            
        del pluginsDialog
        pluginsDialog = None

    def __openOptionsEvent__ (self, b):
        """
        @summary: Open options window.
        @param b: Button that threw event.
        """
        optionsDialog = OptionsDialog(self.__langs__,
                                      self.__currLang__,
                                      callback = self.__applyConfigurationCallback__,
                                      parent = self.__mainWindow__)
        
        __log__.debug("Option dialog created. %s" % optionsDialog)
        optionsDialog.run()
        
    def __changeProjectEvent__ (self, notebook, page, pageNum):
        """
        @summary: Handle change tab signal.
        @param notebook: GtkNotebook control that threw event.
        @param page: New page.
        @param pageNum: Number of new page.  
        """
        if (self.__lsTabs__ != None):
            if (len(self.__lsTabs__) > pageNum):
                self.__currentTab__ = self.__lsTabs__[pageNum]
                self.__updateTitle__(threadBlock=False)
                self.__enableOptions__(blockGtk=False)
            else:
                __log__.warning("There is not tab at index %d" % pageNum)
        else:
            __log__.warning("There is not list of tabs.")
    

    def __runEvent__ (self, b):
        """
        @summary: Do current project.
        @param b: Button that threw event.
        """
        if (self.__currentTab__ != None):
            self.__currentTab__.setOrderToCore()
            exWindow = ExecuteWindow(self.__currentTab__.getCore(), 
                                     parent = self.__mainWindow__)
            __log__.debug("Execute window created. %s" % exWindow)            
            exWindow.run()
        else:
            FactoryControls.getMessage(
                _("There isn't current project"), 
                title=_("Execute"),
                parent = self.__mainWindow__)

    def __activateOperation__ (self, action, callback=None):
        """
        @summary: Handle operation action.
        @param action: Action that threw event.
        @param callback: Function reference of operation. 
        """
        if (isinstance(action, gtk.Action)):
            if (callback != None):
                callback(action, self.__currentTab__, userData=self.__mainWindow__)
                __log__.info("Action of operation %s threw." % action.get_name())
            else:
                __log__.debug("Callback of %s is None" % action.get_name())
        else:
            __log__.warning("action is not gtk.Action")

    def __openAboutEvent__ (self, b):
        """
        @summary: Handle button about.
        @param b: Button that threw event.
        """
        self.showAbout()

    def __newProjectEvent__ (self, b, projectType=None):
        """
        @summary: Handle new project action.
        @param b: Button that threw event.
        @param projectType: Class reference of project to create. 
        """
        self.__addNewProject__(threadBlock=False, projectType=projectType)
        __log__.info("New project created.")
    
    def __openProjectEvent__ (self, b):
        """
        @summary: Handle open project action.
        @param b: Button that threw event.
        """
        
        fileSel = gtk.FileChooserDialog(title=_("Open project"),
                                        parent=self.__mainWindow__,
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        
        fileSel.set_default_response(gtk.RESPONSE_CANCEL)
        
        filterCam = gtk.FileFilter()
        filterCam.set_name(_("PyCamimg file"))
        filterCam.add_pattern("*%s" % self.PYCAMIMG_FILE_EXTENSION)
        fileSel.add_filter(filterCam)
        
        fileSel.set_modal(True)
        fileSel.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        if (fileSel.run() == gtk.RESPONSE_ACCEPT):
            filename = fileSel.get_filename()
            __log__.debug("Open project from %s" % filename)
            if (not filename.endswith(self.PYCAMIMG_FILE_EXTENSION)):
                filename = "%s%s" % (filename, self.PYCAMIMG_FILE_EXTENSION)
            
            try:
                core = CamCore.load(filename, tempFolder=__TEMP_FOLDER__)
            except Exception, e:
                __log__.error("It could not load project from %s. %s" % (filename, e))
                FactoryControls.getMessage(_("An error was occurred when it was loading project from %s" % filename),
                                           type=gtk.MESSAGE_ERROR, 
                                           title=_("Open project"),
                                           parent = self.__mainWindow__)
                return
            finally:
                fileSel.destroy()
                
            self.__addNewProject__(core = core, threadBlock = False, focused=True)
            __log__.info("Project loaded from %s" % filename)
        else:
            fileSel.destroy()
        
    def __saveProjectEvent__ (self, b):
        """
        @summary: Handle save project action.
        @param b: Button that threw event.
        """
        if (self.__currentTab__ == None):
            __log__.debug("There is not current project")
            return
        core = self.__currentTab__.getCore()
        __log__.debug("Saving current project %s" % core.getName())
        if (core.isSaved()):
            __log__.debug("Current project is already saved on %s. Overwriting file." % core.getFilename())
            try:
                core.save()
            except Exception, e:
                __log__.error("It could not save current project to %s. %s" % (core.getFilename(), e))
                FactoryControls.getMessage(_("An error was occurred when it was saving current project to %s" % core.getFilename()),
                                           type=gtk.MESSAGE_ERROR, 
                                           title=_("Save project"),
                                           parent = self.__mainWindow__)
                return
        else:
            __log__.debug("Current project is not saved yet. Opening save dialog")
            try:
                self.__saveAsProjectEvent__(b, raiseError=True)
            except Exception, e:
                __log__.error("It could not save current project to %s. %s" % (core.getFilename(), e))
                FactoryControls.getMessage(_("An error was occurred when it was saving current project to %s" % core.getFilename()),
                                           type=gtk.MESSAGE_ERROR, 
                                           title=_("Save project"),
                                           parent = self.__mainWindow__)
                return
        __log__.info("Current project save on %s" % core.getFilename())
    
    def __saveAsProjectEvent__ (self, b, raiseError=False):
        """
        @summary: Handle save project action.
        @param b: Button that threw event.
        @param raiseError: True to throw an error when occurrs. 
        """
        if (self.__currentTab__ == None):
            __log__.debug("There is not current project")
            return
        
        fileSel = gtk.FileChooserDialog(title=_("Save project"),
                                        parent=self.__mainWindow__,
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        fileSel.set_default_response(gtk.RESPONSE_CANCEL)
        
        filterCam = gtk.FileFilter()
        filterCam.set_name(_("PyCamimg file"))
        filterCam.add_pattern("*%s" % self.PYCAMIMG_FILE_EXTENSION)
        fileSel.add_filter(filterCam)
        
        fileSel.set_modal(True)
        fileSel.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        if (fileSel.run() == gtk.RESPONSE_ACCEPT):
            filename = fileSel.get_filename()
            __log__.debug("Save project to %s" % filename)
            if (not filename.endswith(self.PYCAMIMG_FILE_EXTENSION)):
                filename = "%s%s" % (filename, self.PYCAMIMG_FILE_EXTENSION)
            
            try:
                if (not self.__currentTab__.getCore().save(path=filename)):
                    raise Exception()
            except Exception, e:
                if (raiseError):
                    raise e
                else:
                    __log__.error("It could not save current project to %s. %s" % (filename, e))
                    FactoryControls.getMessage(_("An error was occurred when it was saving current project to %s" % filename),
                                               type=gtk.MESSAGE_ERROR, 
                                               title=_("Save project"),
                                               parent = self.__mainWindow__)
                    return
            finally:
                fileSel.destroy()
        
            __log__.info("Current project saved on %s" % filename)
        else:
            fileSel.destroy()
            
        self.__updateTitle__(threadBlock=False)

    def __changeViewProjectEvent__(self, b):
        """
        @summary: Handle change view action in tab project.
        @param b: Button that threw event.
        """
        if (self.__currentTab__ == None):
            __log__.debug("There is not current project")
            return
        value = self.__currentTab__.VIEW_TREEVIEW
        bChange = self.__uiManager__.get_widget("/ToolsPyCamimg/ChangeView")
        if (bChange != None):
            if (bChange.get_active()):
                value = self.__currentTab__.VIEW_ICONVIEW
                __log__.debug("Set ICONVIEW")
        else:
            __log__.warning("It has not found ChangeView toolbutton")
        self.__currentTab__.changeView(value)

    def __queryQuitMenuItemEvent__(self, b):
        """
        @summary: Handle quit action from menu item.
        @param b: Button that threw event.
        """
        if (not self.__queryQuitEvent__(b)):
            self.__quitEvent__(b)
            
    def __queryQuitEvent__(self, window, event=None):
        """
        @summary: Handle query quit event.
        @param window: GtkWindow that threw event. 
        """
        if (gtk.RESPONSE_YES == FactoryControls.getConfirmMessage(_("Are you sure you want to close PyCamimg?"), 
                                                                  title=_("Close PyCamimg"),
                                                                  parent = self.__mainWindow__)):
            return False
        else:
            return True

    def __quitEvent__(self, b):
        """
        @summary: Handle quit event.
        @param b: GtkObject that threw event. 
        """
        __log__.debug("Closing main window...")
        FactoryDirectoryMonitor.removeAll()
        gtk.main_quit()
        __log__.debug("Main window closed.")
        
#OPTIONS DIALOG

    def __applyConfigurationCallback__(self, dialog):
        """
        @summary: Handle response of options dialog
        @param dialog: Dialog associated. 
        """
        self.__refreshProjects__()
        __log__.debug("Projects refreshed")
        
        if (dialog != None):
            del dialog


    def show(self, resetExplorer = True):
        """
        @summary: Show main window.
        @param resetExplorer: True to put home directory on explorer. 
        """
        self.__mainWindow__.show_all()
        if (resetExplorer):
            self.__eExplorer__.goHome()

#ABOUT DIALOG

    def showAbout(self):
        """
        @summary: Show about dialog.
        """
        if (hasattr(self, "__aboutDialog__")):
            if (self.__aboutDialog__ == None):
                self.__aboutDialog__ = FactoryControls.getAbout(
                    __VERSION_FILE__,
                    self.__closeAbout__, 
                    __COPYING_FILE__,
                    parent=self.__mainWindow__)
        else:
            self.__aboutDialog__ = FactoryControls.getAbout(
                __VERSION_FILE__,
                __COPYING_FILE__,
                parent=self.__mainWindow__)

        self.__aboutDialog__.run()
        
if __name__ == "__main__":
    print "It is not a program"
        
