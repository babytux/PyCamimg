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
from pycamimg.core.db.ConfigurationDB import ConfigurationDB
from pycamimg.core.Configuration import Configuration

__COLUMN_TEXT__ = 0
__COLUMN_VALUE__ = 1

class OptionsDialog (gtk.Dialog):
    """
    @summary: Class that manage option dialog.
    """
    
    __DEFAULT_WINDOW_WIDTH__ = 450
    __DEFAULT_WINDOW_HEIGHT__ = 350
    
    def __init__(self, languages, currentLanguage, callback=None, parent=None):
        """
        @summary: Create new options dialog. 
        @param languages: A list with supported languages.
        @param currentLanguage: Current language.
        @param callback: Callback that it will be executed when dialog closes    
        @param parent: GtkWindow parent.  
        """
        super(OptionsDialog, self).__init__()
        
        self.__langs__ = languages
        self.__currLang__ = currentLanguage
        
        super(OptionsDialog, self).set_title(_("Preferences"))
        super(OptionsDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(OptionsDialog, self).add_buttons(gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
                                               gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                               gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(OptionsDialog, self).set_transient_for(parent)
        if (parent != None):
            super(OptionsDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(OptionsDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(OptionsDialog, self).connect("response", self.__closeEvent__)
        super(OptionsDialog, self).set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)
        
        self.__initUI__()
        self.__callback__ = callback


    def __initUI__(self):
        """
        @summary: Initialize ui.
        """
        self.__nbTabs__ = gtk.Notebook()
        
        self.__initTabInterface__()
        self.__initTabLanguages__()
        self.__initTabCore__()
        self.__initTabPhotoAlbum__()
        
        self.get_child().pack_start(self.__nbTabs__, True, True)
        
        self.__nbTabs__.show_all()
    
    def __addTab__(self, name, widgetTab):
        """
        @summary: Add new tab with name
        """
        self.__nbTabs__.append_page(widgetTab, tab_label=gtk.Label(str=name))
    
    def __initTabInterface__(self):
        """
        @summary: Initialize tab of interface. 
        """
        vBoxTabInterface = gtk.VBox()
        self.__chkHiddenFiles__ = gtk.CheckButton(label=_("Show hidden files"))
        vBoxTabInterface.pack_start(self.__chkHiddenFiles__, False, True)
        vBoxTabInterface.pack_start(gtk.HSeparator(), False, True)
        
        
        # First expander....
        self.__spNumberColumns__ = gtk.SpinButton(climb_rate=1.00)
        self.__spNumberColumns__.set_name("__spNumberColumns__")
        self.__spNumberColumns__.set_increments(1.00, 5.00)
        self.__spNumberColumns__.set_range(0.00, 10.00)
        self.__spNumberColumns__.set_numeric(True)
        self.__spNumberColumns__.set_editable(True)
        self.__spNumberColumns__.set_update_policy(gtk.UPDATE_IF_VALID)
        
        self.__spHeightImageView__ = gtk.SpinButton(climb_rate=1.00)
        self.__spHeightImageView__.set_name("__spHeightImageView__")
        self.__spHeightImageView__.set_increments(1.00, 10.00)
        self.__spHeightImageView__.set_range(0.00, sys.maxint)
        self.__spHeightImageView__.set_numeric(True)
        self.__spHeightImageView__.set_editable(True)
        self.__spHeightImageView__.set_update_policy(gtk.UPDATE_IF_VALID)
        
        tImageView = gtk.Table(rows=2, columns=2, homogeneous=False)
        tImageView.set_col_spacings(10)
        tImageView.set_row_spacings(4)
        
        tImageView.attach(gtk.Label(str=_("Number of columns")), 0, 1, 0, 1, yoptions=gtk.FILL, xoptions=gtk.FILL)
        tImageView.attach(self.__spNumberColumns__, 1, 2, 0, 1, yoptions=gtk.FILL, xoptions=gtk.FILL)
        tImageView.attach(gtk.Label(str=_("Height of images")), 0, 1, 1, 2, yoptions=gtk.FILL, xoptions=gtk.FILL)
        tImageView.attach(self.__spHeightImageView__, 1, 2, 1, 2, yoptions=gtk.FILL, xoptions=gtk.FILL)
        
        lbl = gtk.Label(str=("<b>%s</b>" % _("View of images")))
        lbl.set_use_markup(True)
        
        eImageView = gtk.Expander()
        eImageView.set_label_widget(lbl)
        eImageView.add(tImageView)
        eImageView.set_expanded(True)
        
        vBoxTabInterface.pack_start(eImageView, True, True)
        
        vBoxTabInterface.pack_start(gtk.HSeparator(), False, True)
        # Second expander
        fListView = gtk.Frame()
        lFrameListView = gtk.Label()
        lFrameListView.set_use_markup(True)
        lFrameListView.set_text(_("Image Options"))
        fListView.set_label_widget(lFrameListView)
        
        aFrameListView = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        aFrameListView.set_padding(0, 0, 12, 0)
        
        vBoxListView = gtk.VBox()
        self.__chkShowImageList__ = gtk.CheckButton(label=_("Show image in list"))
        self.__chkShowImageList__.connect("toggled", self.__imageShowToggledEvent__)
        vBoxListView.pack_start(self.__chkShowImageList__, False, True)
        
        self.__spPercentResize__ = gtk.SpinButton(climb_rate=1.00)
        self.__spPercentResize__.set_name("__spPercentResize__")
        self.__spPercentResize__.set_increments(1.00, 10.00)
        self.__spPercentResize__.set_range(0.00, 100.00)
        self.__spPercentResize__.set_numeric(True)
        self.__spPercentResize__.set_editable(True)
        self.__spPercentResize__.set_update_policy(gtk.UPDATE_IF_VALID)
        
        self.__spMaxHeight__ = gtk.SpinButton(climb_rate=1.00)
        self.__spMaxHeight__.set_name("__spMaxHeight__")
        self.__spMaxHeight__.set_increments(1.00, 10.00)
        self.__spMaxHeight__.set_range(0.00, 300)
        self.__spMaxHeight__.set_numeric(True)
        self.__spMaxHeight__.set_editable(True)
        self.__spMaxHeight__.set_update_policy(gtk.UPDATE_IF_VALID)
        
        tListView = gtk.Table(rows=2, columns=2, homogeneous=False)
        tListView.set_col_spacings(10)
        tListView.set_row_spacings(4)
        
        tListView.attach(gtk.Label(str=_("Maximum Height")), 0, 1, 0, 1, yoptions=gtk.FILL, xoptions=gtk.FILL)
        tListView.attach(self.__spMaxHeight__, 1, 2, 0, 1, yoptions=gtk.FILL, xoptions=gtk.FILL)
        tListView.attach(gtk.Label(str=_("Percent to resize")), 0, 1, 1, 2, yoptions=gtk.FILL, xoptions=gtk.FILL)
        tListView.attach(self.__spPercentResize__, 1, 2, 1, 2, yoptions=gtk.FILL, xoptions=gtk.FILL)
        
        vBoxListView.pack_start(tListView, False, True)
        aFrameListView.add(vBoxListView)
        fListView.add(aFrameListView)
        
        lbl = gtk.Label(str=("<b>%s</b>" % _("List of images")))
        lbl.set_use_markup(True)
        
        eListView = gtk.Expander()
        eListView.set_label_widget(lbl)
        eListView.add(fListView)
        eListView.set_expanded(True)
        
        vBoxTabInterface.pack_start(eListView, True, True)
        
        self.__addTab__(_("Interface"), vBoxTabInterface)
        
                        
    def __initTabLanguages__(self):
        """
        @summary: Initialize tab of language.
        """
        vBoxTabLanguage = gtk.VBox()
        
        hBoxSelectLang = gtk.HBox()

        vBoxLabelLang = gtk.VBox()
        lLanguages = gtk.Label(str="<b>%s</b>" % _("Language"))
        lLanguages.set_use_markup(True)
        lLangNote = gtk.Label()
        lLangNote.set_use_markup(True)
        lLangNote.set_label('<span size="x-small">(%s)</span>' % _("Need to Restart"))
        vBoxLabelLang.pack_start(lLanguages, False, True)
        vBoxLabelLang.pack_start(lLangNote, False, True)

        hBoxSelectLang.pack_start(vBoxLabelLang, False, True)
        
        self.__cbLanguages__ = gtk.ComboBox()
        hBoxSelectLang.pack_start(self.__cbLanguages__, True, True, padding=10)
        
        vBoxTabLanguage.pack_start(hBoxSelectLang, False, True)
        
        self.__addTab__(_("Language"), vBoxTabLanguage)
        
    def __initTabCore__(self):
        """
        @summary: Initialize tab of core.
        """
        vBoxTabCore = gtk.VBox()
        
        self.__chkAddRecursive__ = gtk.CheckButton(label=_("Add recursive"))
        self.__chkAddRecursive__.connect("toggled", self.__addRecursiveToggledEvent__)
        
        hBoxRecursive = gtk.HBox()
        
        self.__spRecursiveLevel__ = gtk.SpinButton(climb_rate=1.00)
        self.__spRecursiveLevel__.set_name("__spRecursiveLevel__")
        self.__spRecursiveLevel__.set_increments(1.00, 5.00)
        self.__spRecursiveLevel__.set_range(0.00, 10)
        self.__spRecursiveLevel__.set_numeric(True)
        self.__spRecursiveLevel__.set_editable(True)
        self.__spRecursiveLevel__.set_update_policy(gtk.UPDATE_IF_VALID)
        
        hBoxRecursive.pack_start(gtk.Label(str=_("Recursive Level")), False, False)
        hBoxRecursive.pack_start(self.__spRecursiveLevel__, False, False, padding=10)
        
        aFrameRecursive = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        aFrameRecursive.set_padding(0, 0, 12, 0)
        aFrameRecursive.add(hBoxRecursive)
        
        fRecursive = gtk.Frame()
        fRecursive.set_label_widget(self.__chkAddRecursive__)
        fRecursive.set_shadow_type(gtk.SHADOW_NONE)
        
        fRecursive.add(aFrameRecursive)
        
        vBoxTabCore.pack_start(fRecursive, False, True)
        
        self.__addTab__(_("Core"), vBoxTabCore)
        
    def __initTabPhotoAlbum__(self):
        """
        @summary: Initialize tab of photoalbum.
        """
        vBoxPhotoAlbum = gtk.VBox()
        
        self.__chkEnablePhotoAlbum__ = gtk.CheckButton(label=_("Enable Photo Album"))
        self.__chkEnablePhotoAlbum__.connect("toggled", self.__enablePhotoAlbumToggledEvent__)
        
        hBoxPhotoAlbumPath = gtk.HBox()
        
        self.__txtPathPhotoAlbum__ = gtk.Entry()
        self.__txtPathPhotoAlbum__.set_editable(False)
        self.__txtPathPhotoAlbum__.set_name("__txtPathPhotoAlbum__")
        
        self.__bPathSelection__ = gtk.Button(label=None, stock=None, use_underline=False)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
        self.__bPathSelection__.set_relief(gtk.RELIEF_NONE)
        self.__bPathSelection__.set_border_width(0)
        self.__bPathSelection__.set_image(image)
        self.__bPathSelection__.connect("clicked", self.__selectPhotoAlbumPath__)
        
        hBoxPhotoAlbumPath.pack_start(gtk.Label(str=_("Photo Album Path")), False, False)
        hBoxPhotoAlbumPath.pack_start(self.__txtPathPhotoAlbum__, True, True, padding=10)
        hBoxPhotoAlbumPath.pack_start(self.__bPathSelection__, False, False)
        
        
        aFramePhotoAlbum = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        aFramePhotoAlbum.set_padding(0, 0, 12, 0)
        aFramePhotoAlbum.add(hBoxPhotoAlbumPath)
        
        fPhotoAlbum = gtk.Frame()
        fPhotoAlbum.set_label_widget(self.__chkEnablePhotoAlbum__)
        fPhotoAlbum.set_shadow_type(gtk.SHADOW_NONE)
        
        fPhotoAlbum.add(aFramePhotoAlbum)
        vBoxPhotoAlbum.pack_start(fPhotoAlbum, False, True)
        
        self.__addTab__(_("Photo Album"), vBoxPhotoAlbum)

    def __fillLanguages__(self, gtkLock=False):
        """
        @summary: Fill combobox with available languages.
        @param gtkLock: True to lock gtk-loop. 
        """
        
        if (not hasattr(self, "__lsLanguages__")):
            self.__lsLanguages__ = gtk.ListStore(gobject.TYPE_STRING,
                                                     gobject.TYPE_STRING)
            render_text = gtk.CellRendererText()
            UIUtils.setModelTreeview(self.__cbLanguages__, self.__lsLanguages__, doGObject=gtkLock)
            
            self.__cbLanguages__.pack_start(render_text)
            self.__cbLanguages__.add_attribute(render_text, 'text', __COLUMN_TEXT__)
        
        iterSelected = None
        for key, lang in self.__langs__.iteritems():
            if (lang == ""):
                continue
            iter = UIUtils.addIterListView(self.__lsLanguages__, (lang, key), doGObject=gtkLock)
            if (key == self.__currLang__):
                iterSelected = iter

        if (iterSelected != None):
            UIUtils.setActiveIter(self.__cbLanguages__, iterSelected, doGObject=gtkLock)
        else:
            UIUtils.setActiveIter(self.__cbLanguages__, 0, doGObject=gtkLock)

    def __initData__(self):
        """
        @summary: Set data to dialog.
        """        
        config = Configuration().getConfiguration()
        
        if ((config == None) or 
            (not isinstance(config, ConfigParser.SafeConfigParser))):
            __log__.error("There isn't configuration in OptionsDialog")
            return None 

        self.__chkHiddenFiles__.set_active(
            config.getboolean("NAVIGATOR", "show_hiddens"))
        self.__chkShowImageList__.set_active(
            config.getboolean("TABPROJECT", "show_image_list"))
        self.__spMaxHeight__.set_value(
            float(config.getint("TABPROJECT", "max_height_list")))
        self.__spPercentResize__.set_value(
            config.getfloat("TABPROJECT", "resize_percent_list"))
        self.__spNumberColumns__.set_value(
            float(config.getint("TABPROJECT", "number_of_columns_iconview")))
        self.__spHeightImageView__.set_value(
            float(config.getint("TABPROJECT", "max_height_imagelist")))
        
        self.__chkAddRecursive__.set_active(
            config.getboolean("UI_CORE", "add_recursive"))
        self.__spRecursiveLevel__.set_value(
            config.getint("UI_CORE", "recursive_level"))
        
        self.__chkEnablePhotoAlbum__.set_active(
            config.getboolean("UI_CORE", "enable_db"))
        
        if (config.getboolean("UI_CORE", "enable_db") and 
            (ConfigurationDB().getPhotoFolder() != None)):
            self.__txtPathPhotoAlbum__.set_text(
                ConfigurationDB().getPhotoFolder())
        else:
            self.__txtPathPhotoAlbum__.set_text("")

        self.__spMaxHeight__.set_sensitive(self.__chkShowImageList__.get_active())
        self.__spPercentResize__.set_sensitive(self.__chkShowImageList__.get_active())
        
        self.__spRecursiveLevel__.set_sensitive(self.__chkAddRecursive__.get_active())

        self.__fillLanguages__(False)

    def __addRecursiveToggledEvent__(self, b):
        """
        @summary: Handle add recursive check toggled.
        @param b: GtkButton associated. 
        """
        self.__spRecursiveLevel__.set_sensitive(self.__chkAddRecursive__.get_active())
        
    def __enablePhotoAlbumToggledEvent__(self, b):
        """
        @summary: Handle enable photo album check toggled.
        @param b: GtkButton associated. 
        """
        self.__bPathSelection__.set_sensitive(self.__chkEnablePhotoAlbum__.get_active())
        self.__txtPathPhotoAlbum__.set_sensitive(self.__chkEnablePhotoAlbum__.get_active())
    
    def __selectPhotoAlbumPath__(self, b):
        '''
        @summary: Create a selection folder dialog 
            and set selected folder as target folder
        @param doBlock: True to block gtk-loop. 
        '''
        try:
            targetSel = gtk.FileChooserDialog(title=_("Photo Album folder"),
                                              parent=self,
                                              action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                              buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                       gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        
            targetSel.set_default_response(gtk.RESPONSE_CANCEL)
            targetSel.set_modal(True)
            targetSel.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            if (ConfigurationDB().getPhotoFolder() != None):
                __log__.debug("Set target before open. %s" % ConfigurationDB().getPhotoFolder())
                targetSel.set_current_folder(ConfigurationDB().getPhotoFolder())
            targetSel.show()
            if (targetSel.run() == gtk.RESPONSE_ACCEPT):
                self.__target__ = targetSel.get_current_folder()
                filename = targetSel.get_filename()
                if (filename != None):
                    self.__txtPathPhotoAlbum__.set_text(os.path.join(self.__target__, filename))
                __log__.info("Set %s as target folder" % ConfigurationDB().getPhotoFolder())
        finally:
            targetSel.destroy()
        
    def __imageShowToggledEvent__(self, b):
        """
        @summary: Handle show image list check toggled.
        @param b: GtkButton associated. 
        """ 
        self.__spMaxHeight__.set_sensitive(self.__chkShowImageList__.get_active())
        self.__spPercentResize__.set_sensitive(self.__chkShowImageList__.get_active())

    def __closeEvent__(self, w, res):
        """
        @summary: Handle response about options dialog.
        @param w: GtkDialog associated.
        @param res: Response associated with the event.  
        """
        config = Configuration().getConfiguration()
        if (config == None):
            __log__.error("It could not recover configuration")
            res == gtk.RESPONSE_CANCEL
        
        if ((res == gtk.RESPONSE_OK) or
            (res == gtk.RESPONSE_APPLY)):
            hasChanged = False
            
            iter = self.__cbLanguages__.get_active_iter()
            key = self.__lsLanguages__.get_value(iter, __COLUMN_VALUE__)

            if (config.get("LANGUAGE", "default") != key):
                hasChanged = True
                config.set("LANGUAGE", "default", key)

            if (config.getboolean("NAVIGATOR", "show_hiddens") != self.__chkHiddenFiles__.get_active()):
                hasChanged = True
                config.set("NAVIGATOR",
                           "show_hiddens",
                           ("%d" % self.__chkHiddenFiles__.get_active()))
            if (config.getboolean("TABPROJECT", "show_image_list") != self.__chkShowImageList__.get_active()):
                hasChanged = True
                config.set("TABPROJECT",
                           "show_image_list",
                           ("%d" % self.__chkShowImageList__.get_active())) 
            if (config.getint("TABPROJECT", "max_height_list") != self.__spMaxHeight__.get_value_as_int()):
                hasChanged = True
                config.set("TABPROJECT",
                           "max_height_list",
                           ("%d" % self.__spMaxHeight__.get_value_as_int()))
            if (config.getfloat("TABPROJECT", "resize_percent_list") != self.__spPercentResize__.get_value()):
                hasChanged = True
                config.set("TABPROJECT",
                           "resize_percent_list",
                           ("%f" % self.__spPercentResize__.get_value()))
            if (config.getint("TABPROJECT", "number_of_columns_iconview") != self.__spNumberColumns__.get_value_as_int()):
                hasChanged = True
                config.set("TABPROJECT",
                           "number_of_columns_iconview",
                           ("%d" % self.__spNumberColumns__.get_value_as_int()))
            if (config.getint("TABPROJECT", "max_height_imagelist") != self.__spHeightImageView__.get_value_as_int()):
                hasChanged = True
                config.set("TABPROJECT",
                           "max_height_imagelist",
                           ("%d" % self.__spHeightImageView__.get_value_as_int()))

            if (config.getboolean("UI_CORE", "add_recursive") != self.__chkAddRecursive__.get_active()):
                hasChanged = True
                config.set("UI_CORE",
                           "add_recursive",
                           ("%d" % self.__chkAddRecursive__.get_active()))
            if (config.getint("UI_CORE", "recursive_level") != self.__spRecursiveLevel__.get_value_as_int()):
                hasChanged = True 
                config.set("UI_CORE",
                           "recursive_level",
                           ("%d" % self.__spRecursiveLevel__.get_value_as_int()))
                
            if (config.getint("UI_CORE", "enable_db") != self.__chkEnablePhotoAlbum__.get_active()):
                hasChanged = True 
                config.set("UI_CORE",
                           "enable_db",
                           ("%d" % self.__chkEnablePhotoAlbum__.get_active()))
            if (ConfigurationDB().getPhotoFolder() != self.__txtPathPhotoAlbum__.get_text()):
                hasChanged = True
                ConfigurationDB().setPhotoFolder(self.__txtPathPhotoAlbum__.get_text())
                

            if (hasChanged):
                Configuration().saveConfiguration()
                ConfigurationDB().save()
                if (self.__callback__ != None):
                    self.__callback__(self if res == gtk.RESPONSE_APPLY else None)
           
        if (res != gtk.RESPONSE_APPLY):
            w.hide()

    def setCallback(self, callback):
        """
        @summary: Set callback to execute when confirm configuracion.
        @param callback: Function reference. 
        @note: callback model: callback (dialog: gtk.Dialog)        
        """
        self.__callback__ = callback

    def setLanguages(self, listLanguages, current):
        """
        @summary: Set languages.
        @param listLanguages: List with all available languages.
        @param current: Current language.  
        """
        self.__langs__ = listLanguages
        self.__currLang__ = current

        self.__fillLanguages__(True)

    def run(self):
        """
        @summary: Show option  dialog.
        """
        self.__initData__()
        super(OptionsDialog, self).run()

