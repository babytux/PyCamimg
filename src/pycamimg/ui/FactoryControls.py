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
import types
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
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

try:
    import gtk, gobject
    import gtk.gdk
except ImportError, ioe:
    __log__.fatal("It can not import gtk, gdk modules. Sure you have installed pygtk?")
    raise ioe

try:
    import pkg_resources
except ImportError, ioe:
    __log__.warning("Can not import pkg_resources. %s" % ioe)
    
import ConfigParser


def getGladeUI(path, widgetName=None, domain=""):
    """
    @summary: Gets UI from glade file.
    @param path: Path of the glade file.
    @param widgetName: Widget from it will be started to load. Default is None
    @param domain: Translation name for glade file. Default is ""
    @return: gtk.glade.XML object.
    @raise TypeError: raise when path is None.
    @raise RuntimeError: raise when glade file could not loaded. 
    """
    if (not isinstance(path, str)):
        __log__.error("path is not str")
        raise TypeError("path is not str")    
    
    try:
        xml = gtk.glade.XML(path, root=widgetName, domain=domain)
    except RuntimeError, ree:
        __log__.error("It could not recover %s. %s" (path, ree))
        raise RuntimeError("Can not recover %s" % path)
    return xml
    
def getGladeUIResource(module, resource, widgetName=None, domain=""):
    """
    @summary: Gets UI from glade resource.
    @param module: Module where glade file is.
    @param resource: Filename of glade file.
    @param widgetName: Widget from it will be started to load. Default is None
    @param domain: Translation name for glade file. Default is ""
    @return: gtk.glade.XML object.  
    """
    return getGladeUI(pkg_resources.resource_filename(module, resource),
                      widgetName=widgetName, domain=domain)

def getUIManager(path, window, actionGroup, domain=""):
    """
    @summary: Gets UI Manager from xml file.
    @param path: Path of the glade file.
    @param window: Window where it will set accelgroup.
    @param actionGroup: Action group to apply to UIManager.  
    @param domain: Translation name for xml file. Default is ""
    @return: Tuple within gtk.UIManager object and merge_id.
    @raise TypeError: raise when path is None.
    @raise RuntimeError: raise when xml file could not loaded. 
    """
    if (not isinstance(path, str)):
        __log__.error("path is not str")
        raise TypeError("path is not str")    
    
    try:
        uiManager = gtk.UIManager()
        if (window != None):
            # Add the accelerator group to window
            window.add_accel_group(uiManager.get_accel_group())
        if (actionGroup != None):
            # Add the actiongroup to the uimanager
            uiManager.insert_action_group(actionGroup, 0)
            
        merge_id = uiManager.add_ui_from_file(path)
    except Exception , ex:
        __log__.error("It could not recover %s. %s" (path, ex))
        raise Exception ("Can not recover %s" % path)
    return (uiManager, merge_id)

def getUIManagerResource(module, resource, window, actionGroup, domain=""):
    """
    @summary: Gets UI Manager from xml resource.
    @param module: Module where xml file is.
    @param resource: Filename of xml file.
    @param window: Window where it will set accelgroup.
    @param actionGroup: Action group to apply to UIManager.
    @param domain: Translation name for xml file. Default is ""
    @return: Tuple within gtk.UIManager object and merge_id.
    @raise TypeError: raise when path is None.
    @raise RuntimeError: raise when xml file could not loaded.   
    """
    return getUIManager(pkg_resources.resource_filename(module, resource),
                        window, actionGroup, domain=domain)

def getTreeColumnProgress(index):
    """
    @summary: Gets a TreeColumn that contains a processbar.
    @param index: Index of column data that will be asociated to progress bar.
    @return: Column model with progress bar.
    @raise TypeError: raise when type of index is not correct.
    """
    if (isinstance(index, int)):    
        column = gtk.TreeViewColumn()
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_clickable(True)
        column.set_title(_("Progress"))
        render = gtk.CellRendererProgress()
        column.pack_start(render, expand=True)
        column.add_attribute(render, 'value', index)
        return column
    else:
        __log__.error("index is not int")
        raise TypeError("index is not int")
    

def getTreeColumnTextAndPixbuf(title, indexText, indexPixbuf, sortable=True):
    """
    @summary: Gets a TreeColumn that contains a Text and a Pixbuf.
    @param title: Title of the column.
    @param indexText: Index of column data that will be asociated to text.
    @param indexPixbuf: Index of column data that will be asociated to image.
    @param sortable: If column is sortable or not.
    @return: Column model with an image and a text.
    @raise TypeError: raise when any parameter type is not correct 
    """
    if (not isinstance(title, str)):
        __log__.error("title is not str")
        raise TypeError("title is not str")    
    if (not isinstance(indexText, int)):
        __log__.error("indexText is not int")
        raise TypeError("indexText is not int")
    
    if (not isinstance(indexPixbuf, int)):
        __log__.error("indexPixbuf is not int")
        raise TypeError("indexPixbuf is not int")
    
    column = gtk.TreeViewColumn()
    column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    column.set_resizable(True)
    column.set_clickable(True)
    column.set_title(title)
    render_pixbuf = gtk.CellRendererPixbuf()
    column.pack_start(render_pixbuf, expand=False)
    column.add_attribute(render_pixbuf, 'pixbuf', indexPixbuf)
    render_text = gtk.CellRendererText()
    column.pack_start(render_text, expand=True)
    column.add_attribute(render_text, 'text', indexText)
    if (sortable):
        column.set_sort_column_id(indexText)
    return column

def getTreeColumnText(title, indexValue, sortable=True):
    """
    @summary: Gets a TreeColumn that contains a Text.
    @param title: Title of the column.
    @param indexValue: Index of column data that will be asociated to text.
    @param sortable: If column is sortable or not.
    @return: Column model with a text.
    @raise TypeError: raise when any parameter type is not correct
    """
    if (not isinstance(title, str)):
        __log__.error("title is not str")
        raise TypeError("title is not str")
    
    if (not isinstance(indexValue, int)):
        __log__.error("indexValue is not int")
        raise TypeError("indexValue is not int")
    
    column = gtk.TreeViewColumn()
    column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    column.set_resizable(True)
    column.set_clickable(True)
    column.set_title(title)
    if (sortable):
        column.set_sort_column_id(indexValue)
    render_text = gtk.CellRendererText()
    column.pack_start(render_text, expand=True)
    column.add_attribute(render_text, 'text', indexValue)
    return column

def getTreeColumnToggle(title, model, indexValue):
    """
    @summary: Gets a TreeColumn that contains a ToggleButton.
    @param title: Title of the column.
    @param model: Model where toggle change value.
    @param indexValue: Index of column data that will be asociated to toggle.
    @return: Column model with a text.
    @raise TypeError: raise when any parameter type is not correct
    """
    if (not isinstance(title, str)):
        __log__.error("title is not str")
        raise TypeError("title is not str")
    
    if (not isinstance(indexValue, int)):
        __log__.error("indexValue is not int")
        raise TypeError("indexValue is not int")
    
    render_toggle = gtk.CellRendererToggle()
    render_toggle.connect('toggled', __toggled_callback__, (model, indexValue))
    column = gtk.TreeViewColumn()
    column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    column.set_resizable(True)
    column.set_clickable(False)
    column.set_title(title)
    column.pack_start(render_toggle, expand=False)
    column.add_attribute(render_toggle, 'active', indexValue)
    
    return column

def __toggled_callback__ (cell, path, tuple=None):
    model, indexValue = tuple
    iter = model.get_iter(path)
    model.set_value(iter, indexValue, not cell.get_active())

def getPixbufFromStock(iconName, size=gtk.ICON_SIZE_MENU):
    """
    @summary: Gets a pixbuf from stock.
    @param iconName: Name of the icon, if it is in current theme.
    @param size: Size of the icon.
    @return: Pixbuf with the icon.
    @raise TypeError: raise when any parameter type is not correct
    """
    if (not isinstance(iconName, str)):
        __log__.error("iconName is not str")
        raise TypeError("iconName is not str")
    if (not isinstance(size, (int, int))):
        __log__.error("size is not (int, int)")
        raise TypeError("size is not (int, int)")
    
    icon = None
    theme = gtk.icon_theme_get_default()
    
    if (iconName != None):
        if (theme.has_icon(iconName)):
            pixelSize = gtk.icon_size_lookup(size)
            icon = theme.load_icon(iconName, pixelSize[0], 0)
        else:
        	if (icon == None):
	        	lk = gtk.stock_lookup(iconName)
    	    	if (lk != None):
        			ctrl = gtk.MenuItem()
        			icon = ctrl.render_icon(lk[0], size)
	        		ctrl = None
		elif (iconName == gtk.STOCK_FILE):
			icon = None
		elif (iconName != gtk.STOCK_MISSING_IMAGE):
			icon = getPixbufFromStock(gtk.STOCK_FILE)
    	    	else:
			__log__.warning("There is not an icon with name %s" % iconName)
            		icon = None
    else:
        __log__.warning("iconName is None.")
        icon = None
        
    return icon

def getAbout(
    versionFile,
    fileLicense,
    parent=None):
    """
    @summary: Gets PyCamimg about dialog.
    @param versionFile: Version file of the program
    @param closeFunction: Function that it will be called as callback when dialog closes.
    @param fileLicense: File where license is stored.
    @param parent: GtkWindow that call.    
    @return: gtk.AboutDialog.
    @raise TypeError: raise when any parameter type is not correct
    """
    if (not isinstance(versionFile, str)):
        __log__.error("versionFile is not str")
        raise TypeError("versionFile is not str")
    if (not isinstance(fileLicense, str)):
        __log__.error("fileLicense is not str")
        raise TypeError("fileLicense is not str")
    if (not isinstance(parent, gtk.Window)):
        __log__.error("fileLicense is not gtk.Window")
        raise TypeError("fileLicense is not gtk.Window")
    
    version = ConfigParser.SafeConfigParser()
    failLoad = False
    try: 
        # Try to read the version file
        version.read([versionFile])
    except Exception, e:
        __log__.error("An error was occurred when it was loading Version file [%s]. %s" % (versionFile, e))
        failLoad = True

    if (failLoad):
        raise Exception("It could not open version file: %s" % versionFile)
        
    about = gtk.AboutDialog()
    about.set_name(version.get("pycamimg", "name_program"))
    about.set_version(version.get("pycamimg", "version"))
    about.set_destroy_with_parent(True)

    # load GPL text file
    h = None
    s = None
    try:
        h = open(fileLicense, 'r')
        s = h.readlines()
    except IOError, err:
        __log__.error("An IO error was occurred when it was loading License file [%s]. %s" (fileLicense, err))
    except Exception, e:
        __log__.error("An error was occurred when it was loading License file [%s]. %s" (fileLicense, e))
       
    def __closeAbout__(w, res):
        """
        @summary: Handle respsonse of about dialog.
        @param w: GtkDialog that is trying to close.
        @param res: Response of dialog.  
        """
        if ((res == gtk.RESPONSE_CANCEL) 
            or (res == gtk.RESPONSE_DELETE_EVENT)):
            w.hide()
            
    gpl = ""
    if (s != None):
        for line in s:
            gpl += line
    if (h != None):
        h.close()
    if (gpl == ""):
        gpl = version.get("pycamimg", "alt_license")
    about.set_copyright(version.get("pycamimg", "copyright"))
    about.set_license(gpl)
    about.set_website(version.get("pycamimg", "website"))
    about.set_website_label(version.get("pycamimg", "website_label"))
    about.set_authors(version.get("pycamimg", "authors").split(","))
    about.set_artists(version.get("pycamimg", "artists").split(","))
    about.set_documenters(version.get("pycamimg", "documenters").split(","))
    about.set_program_name(version.get("pycamimg", "name_program"))
    about.set_comments(version.get("pycamimg", "short_description"))
    if (parent != None):
        about.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        about.set_transient_for(parent)
    else:
        about.set_position(gtk.WIN_POS_CENTER)
        about.set_transient_for(None)
        
    about.set_icon_name("gtk-about")
    about.connect("response", __closeAbout__)
        
    return about

def getMessage(message,
               title="PyCamimg",
               type=gtk.MESSAGE_INFO,
               show=True,
               parent=None,
               gtkLock=False):
    """
    @summary: Create and show a message dialog.
    @param title: Title of the message box.
    @param type: Type of the message.
    @param show: True if you want to show when it is created.
    @param parent: Parent GtkWindow.
    @return: GtkMessageDialog    
    """
    msg = gtk.MessageDialog(parent,
                            gtk.DIALOG_MODAL,
                            type,
                            gtk.BUTTONS_OK,
                            message)
    msg.set_title(title)

    if (parent != None):
        msg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        msg.set_transient_for(parent)
    else:
        msg.set_position(gtk.WIN_POS_CENTER)
        msg.set_transient_for(None)

    if (show):
        if (gtkLock):
            gtk.gdk.threads_enter()
        try:
            msg.run()
        finally:
            if (gtkLock):
                gtk.gdk.threads_leave()
            msg.destroy()
    return msg

def getConfirmMessage(message,
                      title="PyCamimg",
                      type=gtk.MESSAGE_QUESTION,
                      show=True,
                      parent=None,
                      gtkLock=False,
                      returnBoolean=False):
    """
    @summary: Create and show a confirm message dialog.
    @param title: Title of the confirm box.
    @param type: Type of the message.
    @param show: True if you want to show when it is created.
    @param parent: Parent GtkWindow.
    @return: GtkMessageDialog    
    """
    msg = gtk.MessageDialog(parent,
                            gtk.DIALOG_MODAL,
                            type,
                            gtk.BUTTONS_YES_NO,
                            message)
    msg.set_title(title)

    if (parent != None):
        msg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        msg.set_transient_for(parent)
    else:
        msg.set_position(gtk.WIN_POS_CENTER)
        msg.set_transient_for(None)

    if (show):
        if (gtkLock):
            gtk.gdk.threads_enter()
        try:
            result = msg.run()
        except Exception, ex:
            __log__.error("An error has occurred. %s", ex)
            result = gtk.REPONSE_CANCEL
        finally:
            if (gtkLock):
                gtk.gdk.threads_leave()
            msg.destroy()
        
        if (not returnBoolean):
            return result
        else:
            if (result == gtk.RESPONSE_YES):
                return True
            else:
                return False
    else:
        return msg

def getImageMenuItem(text, imagePath):
    """
    @summary: Gets an ImageMenuItem
    @param text: Text of the menu item.
    @param imagePath: Path of the image of the menu item.
    @return: GtkImageMenuItem
    """
    mi = gtk.ImageMenuItem()
    lbl = gtk.Label(str=text)
    lbl.set_justify(gtk.JUSTIFY_LEFT)
    lbl.set_alignment(0.0, 0.0)
    mi.add(lbl)
    size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
    pbProject = gtk.gdk.pixbuf_new_from_file_at_size(imagePath, size[0], size[1])
    imageProject = gtk.Image()
    imageProject.set_from_pixbuf(pbProject)
    mi.set_image(imageProject)
    
    return mi
