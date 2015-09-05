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
from pycamimg.core.plugins import Loader
from pycamimg.core.plugins.ICamimgPlugin import PLUGIN_TYPE

class PluginsDialog (gtk.Dialog):
    """
    @summary: Class that manage plugins dialog.
    """
    COLUMN_KEY = 0
    COLUMN_PLUGIN = 1
    COLUMN_TYPE = 2
    COLUMN_OBJECT = 3
    
    __RESPONSE_PREFERENCE__ = 200
    
    __DEFAULT_WINDOW_WIDTH__ = 500
    __DEFAULT_WINDOW_HEIGHT__ = 400
    
    def __init__(self, callback=None, parent=None):
        """
        @summary: Create new plugins dialog.
        @param callback: Callback that it will be executed when dialog closes    
        @param parent: GtkWindow parent.  
        """
        super(PluginsDialog, self).__init__()
        
        super(PluginsDialog, self).set_title(_("Plugins"))
        super(PluginsDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        # super(PluginsDialog, self).add_buttons(gtk.STOCK_PREFERENCES, self.__RESPONSE_PREFERENCE__,
        #                                       gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(PluginsDialog, self).set_transient_for(parent)
        if (parent != None):
            super(PluginsDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(PluginsDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(PluginsDialog, self).connect("response", self.__closeEvent__)
        super(PluginsDialog, self).set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)
        
        self.__initUI__()
        self.__callback__ = callback


    def __initUI__(self):
        """
        @summary: Initialize ui.
        """
        self.__btConfig__ = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        self.__btConfig__.set_sensitive(False)
        self.__btConfig__.show_all()
        super(PluginsDialog, self).add_action_widget(self.__btConfig__, self.__RESPONSE_PREFERENCE__)
        super(PluginsDialog, self).add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        treeview = gtk.TreeView()
        self.__model__ = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_OBJECT)

        # self.__model__.set_default_sort_func(lambda *args: -1)
        
        __log__.debug("Created model for new project")
    
        treeview.set_model(self.__model__)
        treeview.set_headers_visible(True)
        treeview.set_headers_clickable(False)
        treeview.set_rules_hint(True)
        treeview.set_enable_search(False)
        treeview.set_fixed_height_mode(False)
        treeview.set_tooltip_column(self.COLUMN_PLUGIN)
        treeview.set_show_expanders(False)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview.set_reorderable(False)
        
        treeview.connect_after("cursor-changed", self.__changedRow__)
        # treeview.connect("cursor-changed", self.__changedRow__)
        
        # Creates columns of the TreeView of target files
        columnPlugin = FactoryControls.getTreeColumnText(_("Plugin"), self.COLUMN_PLUGIN, sortable=True)
        treeview.append_column(columnPlugin)
        columnType = FactoryControls.getTreeColumnText(_("Type"), self.COLUMN_TYPE, sortable=True)
        treeview.append_column(columnType)
        
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
        mPlugins = Loader.pluginsLoaded
        if (mPlugins != None):
            for key, lPlugins in mPlugins.iteritems():
                for plugin, pluginRef in lPlugins:
                    obj = gobject.GObject()
                    obj.set_data("plugin", plugin)
                    newRowData = [plugin.getId(), plugin.getName(), PLUGIN_TYPE.getTypeDescription(plugin.getType()), obj]
                    UIUtils.addIterListView(self.__model__,
                                            newRowData,
                                            doGObject=gtkLock)
                    __log__.info("New file inserted into plugins treeview. %s" % plugin.getId())
        else:
            __log__.debug("There are not plugins")

    def __getSelectedPlugin__(self, tv):
        """
        @summary: Gets plugin object that is an implementation of 
        pycamimg.core.plugins.ICamimgPlugin.ICamimgPlugin
        @param tv: Treeview where model within plugis is. 
        @return: Found plugin or None if it was not found
        """
        plugin = None
        if (tv != None):
            selection = tv.get_selection()
            if (selection.count_selected_rows() == 1):
                model, iter = selection.get_selected()
                if (selection.iter_is_selected(iter)):
                    plugin = None
                    pluginObj = model.get_value(iter, self.COLUMN_OBJECT)
                    if (pluginObj != None):
                        plugin = pluginObj.get_data("plugin")
                    
        return plugin

    def __changedRow__(self, tv):
        """
        @summary: Handle cursor-changed signal on treeview.
        @param tv: Treeview that threw the signal. 
        """
        enabled = False
        plugin = self.__getSelectedPlugin__(tv)
        if (plugin != None):
            enabled = plugin.hasConfiguration()
        if (enabled):
            __log__.debug("It's a plugin with configuration.")
        else:
            __log__.debug("Selected plugin does not have configuration.")
        self.__btConfig__.set_sensitive(enabled)
    
    def __runPluginPreferences__(self):
        """
        @summary: Handles thrown event when user press plugin preferences.
        """
        plugin = self.__getSelectedPlugin__(self.__treeview__)
        if (plugin != None):
            plugin.showPluginConfiguration(parent=self)
    
    def __closeEvent__(self, w, res):
        """
        @summary: Handle response about plugins dialog.
        @param w: GtkDialog associated.
        @param res: Response associated with the event.  
        """
        if (res == gtk.RESPONSE_OK):
            if (self.__callback__ != None):
                self.__callback__()
           
        elif (res == self.__RESPONSE_PREFERENCE__):
            self.__runPluginPreferences__()
        if (res != self.__RESPONSE_PREFERENCE__):
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
        super(PluginsDialog, self).run()
