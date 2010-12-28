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

class Project:
    """
    @summary: Defines an interface to implement any type of project.
    """
    
    def __init__(self):
        return
    
    def setBlockWindow(self, window):
        """
        @summary: Sets window as parent window.
        """
        return
        
    def getIconName(self):
        """
        @summary: Gets name of icon that represents this project type.
        @return: String with icon name
        """
        return ""
    
    def getXmlLocation(self):
        """
        @summary: Gets xml file that contains XmlMenu and its options.
        @return: String with path 
        """
        return ""
    
    def getGtkAction(self):
        """
        Gets gtk.Action of project
        """
        return None
    
    def getTypeName(self):
        """
        @summary: Gets name of this project type.
        @return: String with type name.
        """
        return ""
    
    def hasOptions(self):
        """
        @summary: Gets if the type of project has any option.
        @return: True when it has any option.
        """
        return False
    
    def getStringUIManager(self):
        """
        @summary: Gets string to add to UIManager.
        @return: str with menus.
        """
        return ""
    
    def getOptions(self):
        """
        @summary: Gets options of the project.
        @return: List of gtk.Actin. None if there are not options 
        """
        return None
    
    def getIconsOptions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {}
    
    def PreDoProject(self, core, blockWindow=None):
        """
        @summary: Execute before items of project process.
        @param core: CamCore to execute.
        @param blockWindow: GtkWindow to block by any dialog.
        @return: True if all is right.
        """
        return True
    
    def PostDoProject(self, core, blockWindow=None):
        """
        @summary: Execute after items of project process.
        @param core: CamCore to execute.
        @param blockWindow: GtkWindow to block by any dialog.
        @return: True if all is right.
        """
        return True
    
    def PreDoItem(self, source):
        """
        @summary: Execute before operations.
        @param source: source file.
        @return: True if it is all right 
        """
        return True
    
    def PostDoItem(self, source):
        """
        @summary: Execute after operations.
        @param source: source file.
        @return: True if it is all right 
        """
        return True
    