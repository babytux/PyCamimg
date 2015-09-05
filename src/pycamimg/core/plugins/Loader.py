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
import imp
import logging
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

try:
    import plugins
except ImportError, ie:
    __log__.error("It could not import plugins. %s" % ie)

import ICamimgPlugin
from pycamimg.util.IOUtils import IOUtils

__classplugin__ = "camimgplugin"
__package__ = "pycamimg"
__plugindir__ = "plugins"
pluginsLoaded = {}
pluginsLoadedArray = []
pluginDepsWait = []

INDEX_PLUGIN = 0
INDEX_PLUGIN_INSTANCE = 1

def load(dictPaths={}):
    """
    @summary: Load plugins
    """
    pluginsLoaded.clear()
    while (len(pluginsLoadedArray) > 0):
        pluginsLoadedArray.pop()
    while (len(pluginDepsWait) > 0):
        pluginDepsWait.pop()
    pathPluginsTypes = None
    
    iou = IOUtils()
    if (len(dictPaths) == 0):
        try:
            pluginsLoad = sys.modules[__package__]
        except Exception, ex:
            __log__.error("It has not find plugins package. %s" % ex)
            pluginsLoad = None
        
        if (pluginsLoad != None):
            pathPluginsTypes, importFile = os.path.split(pluginsLoad.__file__)
            pathPluginsTypes, dirImport = os.path.split(pathPluginsTypes)
            pathPluginsTypes = os.path.join(pathPluginsTypes, __plugindir__)
            
            dictPaths[__plugindir__] = pathPluginsTypes
    
    for key, path in dictPaths.iteritems():
        __loadDirPlugin__(key, path, iou)
        
        
    toTry = len(pluginDepsWait)
    if (toTry > 0):
        attempt = -1
        while ((attempt != 0) and (attempt != toTry)):
            curr = 0
            attempt = len(pluginDepsWait)
            while (curr < attempt):
                pathPluginsTypes, plugin, key = pluginDepsWait.pop(curr)
                if (__loadPlugin__(pathPluginsTypes, plugin, key, iou) == 1):
                    pluginDepsWait.append((pathPluginsTypes, plugin, key))
                curr += 1
            attempt = len(pluginDepsWait)
    del iou
    
def __loadDirPlugin__(key, path, iou=None):
    """
    @summary: Load plugins from a directory.
    @param key: Name of directory where plugins are.
    @param path: Parent where directory is.
    @param iou: IOUtils object. 
    """
    delIou = False
    if iou == None:
        delIou = True
        iou = IOUtils()
    
    pathPluginsTypes = os.path.join(path, key)
    sys.path.append(pathPluginsTypes)
    next = True
    # import plugin module to set plugin reference. 
    try:
        imp.load_source(key, os.path.join(pathPluginsTypes, "__init__.py"))
    except Exception, ex:
        __log__.error("It could not load %s. Skip it" % pathPluginsTypes)
        next = False
        
    if (next):
        import plugins
        
        plugins = iou.getDirectories(pathPluginsTypes)
        if (plugins != None):
            for plugin in plugins:
                if (__loadPlugin__(pathPluginsTypes, plugin, key, iou) == 1):
                    pluginDepsWait.append((pathPluginsTypes, plugin, key))
        else:
            __log__.warning("There aren't plugins in %s" % pathPluginsTypes)
    
    if (delIou):
        del iou
    
def __loadPlugin__(pathPluginsTypes, plugin, key, iou=None):
    """
    @summary: Load a plugin.
    @param pathPluginsTypes: Path of directory where plugin is.
    @param key: Name of directory parent.
    @param plugin: Name of plugin.
    @param iou: IOUtils object. 
    @return: Int with value of op.
        0 - Ok
        1 - No deps
        2 - Fail
    """
    iRes = 0
    delIou = False
    if iou == None:
        delIou = True
        iou = IOUtils()
    
    py_mod = None
    filesPluginPath = os.path.join(pathPluginsTypes, plugin)
    files = iou.getFiles(filesPluginPath)
    isPlugin = False
    isCompilled = False
    
    if ((files.count("camimgplugin.py") > 0) and (files.count("__init__.py") > 0)):
        isCompilled = False
        isPlugin = True
    """
    if ((files.count("camimgplugin.pyc") > 0) and (files.count("__init__.pyc") > 0)):
        isCompilled = True
        isPlugin = True
    """
    if (isPlugin):
        pluginPath = os.path.join(filesPluginPath, "camimgplugin.pyc" if isCompilled else "camimgplugin.py")
        pluginModAccess = ("%s.%s" % (key, plugin))
        
        if (not isCompilled):
            pluginPackagePath = os.path.join(filesPluginPath, "__init__.py")
            imp.load_source(pluginModAccess, pluginPackagePath)
            __log__.debug("__init__.py imported from package %s", filesPluginPath)
            py_mod = imp.load_source("%s.cammingplugin" % pluginModAccess, pluginPath)
        else:
            pluginPackagePath = os.path.join(filesPluginPath, "__init__.pyc")
            imp.load_compiled(pluginModAccess, pluginPackagePath)
            __log__.debug("__init__.pyc imported from package %s", filesPluginPath)
            py_mod = imp.load_compiled("%s.cammingplugin" % pluginModAccess, pluginPath)
            
        __log__.info("It detected a plugin in %s" % pluginPath)

    if (isPlugin and (py_mod != None)):
        
        sys.path.append(filesPluginPath)
        if __classplugin__ in dir(py_mod):
            __log__.debug("Loading %s..." % pluginPath)
            plugin = py_mod.camimgplugin()
            if (plugin.getType() != None):
                py_mod_class = None
                if (plugin.isNeedLoad()):
                    if ((plugin.getPluginDependecies() != None) and (len(plugin.getPluginDependecies()) > 0)):
                        for dep in plugin.getPluginDependecies():
                            if not (dep in pluginsLoadedArray):
                                iRes = 1
                                __log__.info("\t%s deps no satisfied." % pluginPath)
                                break
                    if (iRes == 0):
                        if (plugin.isCompiled()):
                            __log__.debug("\t%s is compiled plugin." % pluginPath)
                            
                            pluginPath = os.path.join(filesPluginPath, "%s.pyc" % plugin.getPluginModule())
                            pluginModName = "%s.%s" % (pluginModAccess, plugin.getPluginModule())
                            try:
                                py_mod_class = imp.load_compiled(pluginModName, pluginPath)
                            except ImportError, ie:
                                __log__.error("It could not load %s from %s. %s" % (pluginModName, pluginPath, ie))
                                iRes = 2
                        else:
                            __log__.debug("\t%s is source plugin." % pluginPath)
                            
                            pluginPath = os.path.join(filesPluginPath, "%s.py" % plugin.getPluginModule())
                            pluginModName = "%s.%s" % (pluginModAccess, plugin.getPluginModule())
                            try:
                                py_mod_class = imp.load_source(pluginModName, pluginPath)
                            except ImportError, ie:
                                __log__.error("It could not load %s from %s. %s" % (pluginModName, pluginPath, ie))
                                iRes = 2
                else:
                    __log__.debug("\t%s is need load." % pluginPath)
                
                if (iRes == 0):
                    if (pluginsLoaded.has_key(plugin.getType())):
                        pluginsLoaded[plugin.getType()].append((plugin, (py_mod_class.CamimgPlugin if py_mod_class else None)))
                    else:
                        pluginsLoaded[plugin.getType()] = [(plugin, (py_mod_class.CamimgPlugin if py_mod_class else None))]
                        
                    pluginsLoadedArray.append(plugin.getId())
                        
                    plugin.initialize()
            else:
                __log__.warning("It can not determinate type of the plugin %s" % pluginPath)
    else:
        __log__.warning("It did not set py_mod variable.")
        
    if (delIou):
        del iou
    return iRes

def getPluginsType(type):
    """
    @summary: Gets a list with the plugins of a type.
    @param type: ICamimgPlugin.PLUGIN_TYPE
    @return: List with tuples (name, plugin)
    """             
    if (pluginsLoaded.has_key(type)):
        return pluginsLoaded[type]
    return None

def getPluginClass(type, name):
    """
    @summary: Gets project from project type.
    @param type: Type of plugin to load.
    @param name: Name of the plugin.  
    """             
    if (pluginsLoaded.has_key(type)):
        for plugin in pluginsLoaded[type]:
            if (plugin[0] == name):
                return plugin[1]
    return None
