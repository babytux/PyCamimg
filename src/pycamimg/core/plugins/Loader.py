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

def load(dictPaths={}):
    """
    @summary: Load plugins
    """
    pluginsLoaded.clear()
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
        pathPluginsTypes = os.path.join(path, __plugindir__);
        sys.path.append(pathPluginsTypes)
        
        # import plugin module to set plugin reference. 
        try:
            imp.load_source(key, os.path.join(pathPluginsTypes, "__init__.py"))
        except Exception, ex:
            __log__.error("It could not load %s. Skip it" % pathPluginsTypes)
            continue
        import plugins
        
        plugins = iou.getDirectories(pathPluginsTypes)
        if (plugins != None):
            for plugin in plugins:
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
                    
                    sys.path.append(filesPluginPath)
            
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
                    if __classplugin__ in dir(py_mod):
                        __log__.debug("Loading %s..." % pluginPath)
                        plugin = py_mod.camimgplugin()
                        if (plugin.getType() != None):
                            if (plugin.isCompiled()):
                                __log__.debug("\t%s is compiled plugin." % pluginPath)
                                
                                pluginPath = os.path.join(filesPluginPath, "%s.pyc" % plugin.getPluginModule())
                                pluginModName = "%s.%s" % (pluginModAccess, plugin.getPluginModule())
                                try:
                                    py_mod_class = imp.load_compiled(pluginModName, pluginPath)
                                except ImportError, ie:
                                    __log__.error("It could not load %s from %s. %s" % (pluginModName, pluginPath, ie))
                                    continue
                            else:
                                __log__.debug("\t%s is source plugin." % pluginPath)
                                
                                pluginPath = os.path.join(filesPluginPath, "%s.py" % plugin.getPluginModule())
                                pluginModName = "%s.%s" % (pluginModAccess, plugin.getPluginModule())
                                try:
                                    py_mod_class = imp.load_source(pluginModName, pluginPath)
                                except ImportError, ie:
                                    __log__.error("It could not load %s from %s. %s" % (pluginModName, pluginPath, ie))
                                    continue
                                
                            if (pluginsLoaded.has_key(plugin.getType())):
                                pluginsLoaded[plugin.getType()].append((plugin.getName(), py_mod_class.CamimgPlugin))
                            else:
                                pluginsLoaded[plugin.getType()] = [(plugin.getName(), py_mod_class.CamimgPlugin)]
                                
                            plugin.initialize()
                        else:
                            __log__.warning("It can not determinate type of the plugin %s" % pluginPath)
                else:
                    __log__.warning("It did not set py_mod variable.")
        else:
            __log__.warning("There aren't plugins in %s" % pathPluginsTypes)
    del iou
    
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