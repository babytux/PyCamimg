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

class OperationPlugin:
    """
    @summary: Defines an interface to implement any type of project.
    """
    
    def __init__(self):
        """
        @summary: Create new operation plugin.
        """
        return
    
    def callbackAction(self, action, currentTab, userData = None):
        """
        @summary: Callback that will be thrown when any action is actived.
        @param action: gtk.Action activated.
        @param currentTab: Current Tab. pycamimg.ui.TabProject.TabProject
        @param userData: User data
        """
        return
        
    
    def getIconName(self):
        """
        @summary: Gets name of icon that represents this project type.
        @return: String with icon name
        """
        return ""
    
    def getIconsActions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {}
    
    def getXmlLocation(self):
        """
        @summary: Gets xml file that contains XmlMenu and its options.
        @return: String with path 
        """
        return ""
    
    def getActions(self):
        """
        @summary: Gets a list of gtk.Action.
        @return: List of gtk.Action with actions of operations. 
        """
        return []
    