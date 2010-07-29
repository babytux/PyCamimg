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

import time
from threading import Thread
from threading import Semaphore
import ConfigParser

try:
    import pygtk
    pygtk.require('2.0')
    import pango
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e
try:
    import gtk, gobject
except Exception, e:
    __log__.fatal("It can not import gtk module. Sure you have installed pygtk?" )
    raise e

from pycamimg.core.CamItem import CamItem
from pycamimg.core.CamCore import CamCore
import FactoryControls

__MODE_ALL__ = 0
__MODE_RUN_AND_CLOSE__ = 1
__MODE_EXECUTING__ = 2
__MODE_CLOSE__ = 3

__EXEC_BTN_INDEX__ = 2
__CANCEL_BTN_INDEX__ = 3
__CLOSE_BTN_INDEX__ = 0
__SPLIT_INDEX__ = [1, 4]

__INIT_OPTIONS_INDEX__ = 5

STATE_IDLE = 0
STATE_EXEC = 1
STATE_FINISH = 2

class ExecuteWindow(gtk.Window):
    """
    @summary: Class that manage execution dialog.
    """
    
    def __init__(self, core, domain=None, parent=None):
        """
        @summary: Create ExecutionDialog handle
        @param core: Core to run. 
        @param domain: domain to translate window.
        @param parent: Main window
        """
        self.__semaphore__ = Semaphore()
        self.__core__ = core
        __log__.debug("Created semaphore. %s" % self.__semaphore__)
        
        super(ExecuteWindow, self).__init__()
        
        super(ExecuteWindow, self).set_title(_("Execute"))
        super(ExecuteWindow, self).set_flags(gtk.DIALOG_DESTROY_WITH_PARENT)
        
        super(ExecuteWindow, self).set_transient_for(parent)
        if (parent != None):
            super(ExecuteWindow, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(ExecuteWindow, self).set_position(gtk.WIN_POS_CENTER)
        
        self.__parent__ = parent
        
        super(ExecuteWindow, self).set_size_request(450, 300)
        super(ExecuteWindow, self).set_icon_from_file(os.path.join(__ICONS_FOLDER__, "pycamimg.png"))
        
        super(ExecuteWindow, self).connect("destroy", self.__quitEvent__)
        super(ExecuteWindow, self).connect("delete-event", self.__queryQuitEvent__)
        
        # Add signals
        #super(ExecuteWindow, self).connect("response", self.__closeEvent__)
        if (domain == None):
            domain = pycamimg.gettextName
        self.__domain__ = domain
        
        self.__initUI__()
        self.__initData__()

    def __initUI__(self):
        """
        @summary: Initialize UI of dialog.
        """
        self.__vMain__ = gtk.VBox()
        self.__initToolbar__()
        
        self.__initLog__()
        
        self.__pb__ = gtk.ProgressBar()
        self.__vMain__.pack_start(self.__pb__, False, True)
        
        self.add(self.__vMain__)
        
    def __initToolbar__(self):
        """
        @summary: Initialize toolbar
        """
        actionGroupExecute = gtk.ActionGroup("ActionGroupExecute")
        
        # Create actions
        actionGroupExecute.add_actions([("ExitAction", gtk.STOCK_QUIT, _("Exit"), None, _("Close execute dialog"), self.__closeEvent__),
                                        ("ExecuteAction", gtk.STOCK_EXECUTE, _("Execute"), None, _("Execute current project"), self.__executeEvent__),
                                        ("CancelAction", gtk.STOCK_CANCEL, _("Cancel"), None, _("Cancel current execution"), self.__cancelEvent__)])

        actionGroupExecute.set_translation_domain(self.__domain__)
        
        __log__.debug("There is a xml path. UI Menus and tools will be recovered from path %s" % __XMLUI_FOLDER__)
        self.__uiManager__ = FactoryControls.getUIManager(os.path.join(__XMLUI_FOLDER__, "execute.xml"), self, actionGroupExecute)[0]

        self.__toolBar__ = self.__uiManager__.get_widget("/ToolsExecute")
        self.__toolBar__.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        self.__toolBar__.set_tooltips(True)
        
        self.__vMain__.pack_start(self.__toolBar__, False, True)
    
    def __initLog__(self):
        """
        @summary: Initialize log part of window.
        """
        self.__txtLog__ = gtk.TextView()
        self.__logBuffer__ = self.__txtLog__.get_buffer()
        fontLog = pango.FontDescription("Courier 10")
        self.__txtLog__.modify_font(fontLog)
        swLog = gtk.ScrolledWindow()
        swLog.add(self.__txtLog__)
        
        
        eLog = gtk.Expander(label=("<b>%s</b>" % _("Log")))
        eLog.set_use_markup(True)
        eLog.add(swLog)
        eLog.set_expanded(True)
        
        self.__vMain__.pack_start(eLog, True, True)

    def __initProjectOptions__(self):
        """
        @summary: Initialize project options.
        """
        if (self.__core__ != None):
            if (self.__core__.getProjectType().hasOptions()):
                actionGroupOptions = gtk.ActionGroup("ActionGroupOptions")
                self.__uiManager__.insert_action_group(actionGroupOptions, pos=-1)
                
                __log__.debug("Adding options of project. %s" % self.__core__.getProjectType().getTypeName())
                
                lActions = self.__core__.getProjectType().getOptions()
                if (lActions != None):
                    for aAction in lActions:
                        __log__.debug("Add action %s" % aAction.get_name())
                        actionGroupOptions.add_action(aAction)
                else:
                    __log__.warning("Actions has not been retrieved.")
                
                self.__uiManager__.add_ui_from_string(self.__core__.getProjectType().getStringUIManager())
                
                dIcons = self.__core__.getProjectType().getIconsOptions()
                for actionPath, iconPath in dIcons.iteritems():
                    mi = self.__uiManager__.get_widget(actionPath)
                    if (mi != None): 
                        iconPath = os.path.join(__ICONS_FOLDER__, iconPath)            
                        __log__.debug("Get icon from %s" % iconPath)
                        if (isinstance(mi, gtk.ImageMenuItem)):
                            UIUtils.setImageToMenuItem(mi, iconPath, doGObject=False)
                        elif (isinstance(mi, gtk.ToolButton)):
                            UIUtils.setImageToToolItem(mi, iconPath, size=self.__toolBar__.get_icon_size(), doGObject=False)
                        else:
                            __log__.warning("Unknown type control.")
        else:
            __log__.warning("There is not core.")
        

    def __initData__(self):
        """
        @summary: Set data to window.
        """
        self.__logBuffer__.set_text(_("Press Accept to start"))
        self.__pb__.set_fraction(0.00)
        self.set_title("%s (%s)" % (_("Execute project"), self.__core__.getName())) 
        
        if (self.__core__ != None):
            self.__initProjectOptions__()
            
            if (len(self.__core__.getItems()) > 0):
                self.setData(float(1) / len(self.__core__.getItems()), 
                             self.__core__, gtkLock=False)
                self.__updateOptions__(blockGtk=False)
            else:
                __log__.info("Try to run a project with Zero items")
                self.__logBuffer__.set_text(_("No items in project."))
                self.__updateOptions__(mode=__MODE_CLOSE__, blockGtk=False)
        else:
            __log__.warning("There is not a core selected.")

    def __updateOptions__(self, mode=__MODE_ALL__, blockGtk=True):
        """
        @summary: Enable or disable all options.
        @param mode: Mode of update.
        @param blockGtk: True if it is necesary block gtk-loop. 
        """
        toolbar = self.__uiManager__.get_widget("/ToolsExecute")
        iOptions = 0
        enable = True
        
        if (toolbar != None):
            iOptions = toolbar.get_n_items()
            
        if (iOptions > 0):
            
            for i in range(0, iOptions):
                enable = True
                if (i in __SPLIT_INDEX__):
                    continue
                elif ((i == __CANCEL_BTN_INDEX__) and (mode != __MODE_EXECUTING__)):
                    enable = False
                elif ((i == __EXEC_BTN_INDEX__) and ((mode == __MODE_EXECUTING__) or (mode == __MODE_CLOSE__))):
                    enable = False
                elif((i == __CLOSE_BTN_INDEX__) and (mode == __MODE_EXECUTING__)):
                    enable = False
                elif ((mode != __MODE_ALL__) and (i >= __INIT_OPTIONS_INDEX__)):
                    enable = False
                
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

    def __beginItemOnExecute__ (self, item):
        """
        @summary: Called when an item starts its process.
        @param item: Item that is going to process
        """
        self.writeLog(_("\tProcessing: ") + item.getPath().strip() + "... ")
        
    def __endItemOnExecute__ (self, item):
        """
        @summary: Called when an item ends its process.
        @param item: Item that just ends. 
        """
        self.writeLog(" OK\n")
        self.incProgress()

    def __incProgress__ (self):
        """
        @summary: Add a step in progress bar.
        """
        fraction = self.__pb__.get_fraction() + self.__pb__.get_pulse_step()
        if (fraction > 1.0):
            fraction = 1.0
        self.__pb__.set_fraction(fraction)

    def __writeLog__ (self, message):
        """
        @summary: Write a message in txtLog.
        @param message: Message to write. 
        """
        self.__semaphore__.acquire()
        iter = self.__logBuffer__.get_end_iter()
        self.__logBuffer__.insert(iter, message)
        self.__txtLog__.scroll_to_iter(iter, 0.0)
        self.__semaphore__.release()

    def __endExecution__ (self):
        """
        @summary: Called when execution ends.
        """
        __log__.info("Enter in __endExecution__ function.")
        
        self.__updateOptions__(mode=__MODE_CLOSE__, blockGtk=False)
            #close.show()
        self.writeLog(_("\nProcess finished"), async=False)
        
        __log__.info("Execution ends.")

    def incProgress (self, async = True):
        """
        @summary: Add a step in progress bar.
        @param async: True to execute as async method. Default value is True 
        """
        if (async):
            gtk.gdk.threads_enter()
        try:
            self.__incProgress__()
        finally:
            if (async):
                gtk.gdk.threads_leave()

    def getState(self):
        """
        @summary: Get state of the execution
        @return: STATE_IDLE, STATE_EXEC or STATE_FINISH
        """
        return self.__core__.getState()

    def writeLog (self, message, async = True):
        """
        @summary: Write a message in txtLog.
        @param message: Message to write.
        @param async: True to execute as async method. Default value is True.
        """
        if (async):
            gtk.gdk.threads_enter()
        try:
            self.__writeLog__(message)
        finally:
            if (async):
                gtk.gdk.threads_leave()

    def endExecutionAsync(self):
        """
        @summary: Run this method when process ends.
        """
        self.endExecution(True)
        
    def endExecution (self, async):
        """
        @summary: Run this method when process ends.
        @param async: True to execute as async method.
        """
        if (async):
            gtk.gdk.threads_enter()
        try:
            self.__endExecution__()
        finally:
            if (async):
                gtk.gdk.threads_leave()

    def setData (self, pulseStep, core, gtkLock=True):
        """
        @summary: Set data to execute dialog.
        @param pulseStep: Float value to define the progress bar forwarding.
        @param core: CamCore that will be executed.  
        """
        self.__core__ = core
        if (gtkLock):
            gtk.gdk.threads_enter()
        try:
            self.__pb__.set_pulse_step(pulseStep)
        finally:
            if (gtkLock):
                gtk.gdk.threads_leave()
        __log__.debug("Set data: pulseStep=%f" % pulseStep)

    def expandLog (self, expander):
        """
        @summary: Runs when the expander toggles.
        @param expander: 
        """
        super(ExecuteWindow, self).resize_children()
    
    def __cancelThread__(self):
        """
        @summary: Cancel current thread.
        """
        self.__core__.cancel()
    
    def __queryClose__(self):
        """
        @summary: Query close.
        """
        if (self.__core__.getState() == STATE_EXEC):               
            if (gtk.RESPONSE_YES == FactoryControls.getConfirmMessage(_("Current project is running. Are you sure you want to exit?"), 
                                                                      title=_("Close execution project"),
                                                                      parent = self)):
                return True
            else:
                return False
        
        return True
            
    def __closeEvent__(self, b):
        """
        @summary: Handle exit button.
        @param b: Button that call this function
        """
        if (self.__queryClose__()):
            self.hide()
            self.destroy()        

    def __queryQuitEvent__(self, window, event=None):
        """
        @summary: Handle query quit event.
        @param window: GtkWindow that threw event. 
        """
        return not self.__queryClose__()

    def __quitEvent__(self, b):
        """
        @summary: Handle quit event.
        @param b: GtkObject that threw event. 
        """
        __log__.debug("Closing execute window...")
        self.__cancelThread__()
        __log__.debug("Execute window closed.")

    def __cancelEvent__(self, b):
        """
        @summary: Handle cancel button.
        @param b: Button that call this function
        """
        if (self.__core__.getState() == STATE_EXEC):
            if (gtk.RESPONSE_YES == FactoryControls.getConfirmMessage(_("Are you sure you want to cancel project?"), 
                                                                      title=_("Cancel project"),                    
                                                                      parent = self)):
                self.__cancelThread__()
                self.__updateOptions__(mode=__MODE_CLOSE__, blockGtk=False)
        else:
            __log__.debug("Execution is just finished")
            
        
    def __executeEvent__(self, b):
        """
        @summary: Handle execute button.
        @param b: Button that call this function
        """
        if (self.__core__.getState() == STATE_EXEC):
            return
        
        self.__logBuffer__.set_text("")
        
        self.__updateOptions__(mode=__MODE_EXECUTING__, blockGtk=False)
        
        self.__core__.setMainWindow(self)
        self.__core__.setCallbackBeginItem(self.__beginItemOnExecute__)
        self.__core__.setCallbackEndItem(self.__endItemOnExecute__)
        self.__core__.setCallbackEndProcess(self.endExecutionAsync)

        __log__.debug("All callbacks are defined.");

        self.writeLog(_("Begin process of project: ") + 
                      self.__core__.getName() + "\n", async=False)
        
        __log__.debug("Running current core [PRE]...")
        if (not self.__core__.process()):
            self.__updateOptions__(blockGtk=False)
            __log__.warning("Project can not run")
        else:
            __log__.debug("Running current core...")

    def run(self):
        """
        @summary: Show option  dialog. 
        it will run this callback before show execute dialog.  
        """
        if (len(self.__core__.getItems()) <= 0):
            FactoryControls.getMessage(
                _("There aren't items"), 
                title=_("Execute"),
                parent = self.get_transient_for())
            __log__.info("Trying to execute a core without items. Exiting from execute dialog.")
            return

        super(ExecuteWindow, self).show_all()
        
