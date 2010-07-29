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
    import gtk, gobject, gtk.gdk
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e

import os.path

WAIT_PER_OPERATION = 0.005

def addIter(model, iterParent, dataModel, doGObject = True):
    """
    @summary: Add an iter at last of the iter.
    @param model: Model of a TreeView.
    @param iterParent: Iter where new iter will be added.
    @param dataModel: Data to add.
    @param doGOject: True when lock gtk-loop.    
    """
    iterReturn = None
    
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        iterReturn = model.append(iterParent, dataModel)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
        
        return iterReturn

def addIterListView(model, dataModel, doGObject = True):
    """
    @summary: Add an iter at last of the iter.
    @param model: Model of a ListView.
    @param dataModel: Data to add.
    @param doGOject: True when lock gtk-loop.
    """
    
    iterReturn = None
    
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        iterReturn = model.append(dataModel)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
        
        return iterReturn

def moveIterAtPathPosition(model, iter, iterRef = None,  
                             position=gtk.TREE_VIEW_DROP_BEFORE,
                             doGObject = True):
    """
    @summary: Add data in a treeview at path position.
    @param model: Model of a TreeView.
    @param data: Data to add.
    @param iter: Iter that it will be used as reference.
    @param position: Position from iter of new iter will be added.
    @param doGOject: True when lock gtk-loop.
    """
    
    if (doGObject):
        gtk.gdk.threads_enter()
        
    try:
        if (position == gtk.TREE_VIEW_DROP_AFTER):
            model.move_after(iter, iterRef)
        else:
            model.move_before(iter, iterRef)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
        

def insertIterAtPathPosition(model, data, iter, 
                             position=gtk.TREE_VIEW_DROP_AFTER,
                             doGObject = True):
    """
    @summary: Add data in a treeview at path position.
    @param model: Model of a TreeView.
    @param data: Data to add.
    @param iter: Iter that it will be used as reference.
    @param position: Position from iter of new iter will be added.
    @param doGOject: True when lock gtk-loop.
    """
    
    iterReturn = None
    
    if (doGObject):
        gtk.gdk.threads_enter()
        
    try:
        if (iter != None):
            if (position == gtk.TREE_VIEW_DROP_BEFORE or
                position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                iterReturn = model.insert_before(iter, data)
            else:
                iterReturn = model.insert_after(iter, data)
        else:
            iterReturn = model.append(data)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
        
        return iterReturn

def insertIter(model, iterParent, dataModel, fieldIndex, callbackComparer, compareUnicode = True, doGObject = True):
    """
    @summary: Insert an iter in sorted model.param
    @param model: Model of a TreeView.
    @param iterParent: Iter that it will be parent of new iter.
    @param dataModel: Data to add.
    @param fieldIndex: Field that it will be used to sort iters.
    @param callbackComparer: Funtion reference used to compare iters.
    @param compareUnicode: True to compare as unicode characters.   
    @param doGOject: True when lock gtk-loop.
    """
    
    iterReturn = None
    
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        itemCompare = dataModel[fieldIndex]
        currNode = model.iter_children(iterParent)
        while (currNode != None):
            currValue = model.get_value(currNode, fieldIndex)
            if (compareUnicode):
                currValue = unicode(currValue)
            if (callbackComparer(currValue, itemCompare) > 0):
                break
            
            currNode = model.iter_next(currNode)
            
        if (currNode != None):
            iterReturn = model.insert_before(iterParent, currNode, dataModel)
        else:
            iterReturn = model.append(iterParent, dataModel)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
        
        return iterReturn

def insertIterListStore(model, iterParent, dataModel, fieldIndex, callbackComparer, compareUnicode = True, doGObject = True):
    """
    @summary: Insert an iter in sorted model.
    @param model: Model of a TreeView.
    @param iterParent: Iter that it will be parent of new iter.
    @param dataModel: Data to add.
    @param fieldIndex: Field that it will be used to sort iters.
    @param callbackComparer: Funtion reference used to compare iters.
    @param compareUnicode: True to compare as unicode characters.   
    @param doGOject: True when lock gtk-loop.
    """
    
    iterReturn = None
    
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        itemCompare = dataModel[fieldIndex]
        currNode = model.get_iter_first()
        while (currNode != None):
            currValue = model.get_value(currNode, fieldIndex)
            if (compareUnicode):
                currValue = unicode(currValue)
            if (callbackComparer(currValue, itemCompare) > 0):
                break
            
            currNode = model.iter_next(currNode)
        try:    
            if (currNode != None):
                iterReturn = model.insert_before(currNode, dataModel)
            else:
                iterReturn =  model.append(dataModel)
        except Exception, e:
            __log__.error("An error occurred when it was inserting a new item (%s). %s", (dataModel[2], e))
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
        
        return iterReturn

def setIterData(model, iter, index, data, doGObject = True):
    """
    @summary: Set data at index position in iter of the model.
    @param model: Model of the TreeView.
    @param index: Index of the value into data.
    @param data: New value.
    @param doGObject: True when lock gtk-loop.   
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        model.set_value(iter, index, data)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()

def deleteIter(model, iter, doGObject = True):
    """
    @summary: Remove a iter from a model.
    @param model: Model of the TreeView.
    @param iter: TreeIter to delete.
    @param doGObject: True when lock gtk-loop.
    """
    if (iter != None):
        if (doGObject):
            gtk.gdk.threads_enter()
        try:
            model.remove(iter)
            del iter
        finally:
            if (doGObject):
                gtk.gdk.threads_leave()

def setColumnOrder(model, indexColumn, order = gtk.SORT_ASCENDING, doGObject = True):
    """
    @summary: Remove a iter from a model.
    @param model: Model of the TreeView.
    @param iter: TreeIter to delete.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        model.set_sort_column_id(indexColumn, order)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()

def setModelTreeview(treeview, model, doGObject = True):
    """
    @summary: Sets model to a TreeView.
    @param model: Model of the TreeView.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        treeview.set_model(model)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()

def clearModelTreeview(model, doGObject = True):
    """
    @summary: Clear model of a TreeView.
    @param model: Model of the TreeView.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        model.clear()
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()

def scrollTreeviewToPath(treeview, path, doGObject = True):
    """
    @summary: Do visible a iter in a TreeView.
    @param path: TreePath where scroll will be moved.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        if ((treeview != None) and (path != None)):
            treeview.scroll_to_cell(path)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()

def enabledWidget(widget, enabled, doGObject = True):
    """
    @summary: Set enabled or disabled a GtkWidget.
    @param enabled: True to enabled GtkWidget.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        if (widget != None):
            widget.set_sensitive(enabled)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()

def expandTreeview(treeview, treepath, doGObject = True):
    """
    @summary: Expand row at path, expanding any ancestors as needed.
    @param treeview: GtkTreeView where iter to expand is.
    @param treepath: TreePath that will be expanded.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        for i in range(len(treepath)):
            treeview.expand_row(treepath[:i+1], open_all=False)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
            
def selectPath(selection, treepath, doGObject = True):
    """
    @summary: Select path in treeview.
    @param selection: Selection that will use to select a TreePath.
    @param treepath: TreePath to select.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        selection.select_path(treepath)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
            
def setActiveIter(widget, iter, doGObject = True):
    """
    @summary: Set iter as active iter.
    @param widget: Widget where iter is.
    @param iter: iter to active.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        widget.set_active_iter(iter)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
    
def addTab(notebook, child, text, doGObject = True):
    """
    @summary: Add new tab on notebook.
    @param notebook: GtkNotebook where tab will be added.
    @param child: GtkWidget to add into body.
    @param text: Text on the tab. 
    @param doGObject: True when lock gtk-loop. 
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        notebook.append_page(child)
        notebook.set_tab_label_text(child, text)
        child.show_all()
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
            
def addTabControl(notebook, child, tabWidget, doGObject = True):
    """
    @summary: Add new tab on notebook.
    @param notebook: GtkNotebook where tab will be added.
    @param child: GtkWidget to add into body.
    @param tabWidget: Widget on the tab. 
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        tabWidget.resize_children()
        notebook.append_page(child, tabWidget)
        child.show_all()
        tabWidget.show_all()
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
            
def removeTab(notebook, child, doGObject=True):
    """
    @summary: Remove tab from notebook.
    @param notebook: GtkNotebook where tab will be removed.
    @param child: GtkWidget to remove.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        notebook.remove_page(notebook.page_num(child))
        del child
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
            
def setTitleWindow(window, title, doGObject=True):
    """
    @summary: Set a title for a window.
    @param window: GtkWindow to put on a title.
    @param title: Title to put on window.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        window.set_title(title)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave() 
            
def setNotifyChildTreeview(treeview, notify, doGObject=True):
    """
    @summary: Set if treeview child attend notifies.
    @param treeview: GtkTreeview to modify.
    @param nofity: True to attend notifies.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        if (notify):
            treeview.thaw_child_notify()
        else:
            treeview.freeze_child_notify()
    finally:
        if (doGObject):
            gtk.gdk.threads_leave() 
            
def setAnimation(imageControl, file, doGObject=True):
    """
    @summary: Set animation to image control.
    @param imageControl: GtkImage to modify.
    @param file: Filepath to apply.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        imageControl.set_from_animation(gtk.gdk.PixbufAnimation(file))
    finally:
        if (doGObject):
            gtk.gdk.threads_leave() 
            
def clearImage(imageControl, doGObject=True):
    """
    @summary: Clear an image control.
    @param imageControl: GtkImage to clear.
    @param doGObject: True when lock gtk-loop.
    """
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        imageControl.set_from_file(None)
    finally:
        if (doGObject):
            gtk.gdk.threads_leave() 
            
def setImageToMenuItem(mi, imagePath, doGObject=True):
    """
    @summary: Sets an image in MenuItem.
    @param mi: GtkMenuItem where it will add image.
    @param imagePath: Path of the image of the menu item.
    @param doGObject: True when lock gtk-loop.
    """
    size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
    pbProject = gtk.gdk.pixbuf_new_from_file_at_size(imagePath, size[0], size[1])
    imageProject = gtk.Image()
    imageProject.set_from_pixbuf(pbProject)
    imageProject.show_all()
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        mi.set_image(imageProject)
        mi.show_all()
    except Exception, e:
        __log__.error("It can not set image %s. %e" % (imagePath, e))
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
            
def setImageToToolItem(ti, imagePath, size=gtk.ICON_SIZE_LARGE_TOOLBAR,doGObject=True):
    """
    @summary: Sets an image in ToolItem.
    @param ti: GtkToolItem where it will add image.
    @param imagePath: Path of the image of the toolitem.
    @param size: Size of image for toolitem 
    @param doGObject: True when lock gtk-loop.
    """
    tSize = gtk.icon_size_lookup(size)
    pb = gtk.gdk.pixbuf_new_from_file_at_size(imagePath, tSize[0], tSize[1])
    image = gtk.Image()
    image.set_from_pixbuf(pb)
    image.show_all()
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        ti.set_icon_widget(image)
        ti.show_all()
    except Exception, e:
        __log__.error("It can not set image %s. %e" % (imagePath, e))
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()
            
def setImageToButton(bt, imagePath, size=gtk.ICON_SIZE_BUTTON, doGObject=True):
    """
    @summary: Sets an image in button.
    @param bt: GtkButton where it will add image.
    @param imagePath: Path of the image of the button.
    @param size: Size of image for button 
    @param doGObject: True when lock gtk-loop.
    """
    tSize = gtk.icon_size_lookup(size)
    pb = gtk.gdk.pixbuf_new_from_file_at_size(imagePath, tSize[0], tSize[1])
    image = gtk.Image()
    image.set_from_pixbuf(pb)
    image.show_all()
    if (doGObject):
        gtk.gdk.threads_enter()
    try:
        bt.set_image(image)
        bt.show_all()
    except Exception, e:
        __log__.error("It can not set image %s. %e" % (imagePath, e))
    finally:
        if (doGObject):
            gtk.gdk.threads_leave()