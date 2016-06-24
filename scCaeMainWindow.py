# -*- coding: utf-8 -*-

# ************************************************************************
# This script defines the main window of the custom Abaqus/CAE application
# ************************************************************************
 
from abaqusGui import *
from sessionGui import *
from canvasGui import CanvasToolsetGui
from viewManipGui import ViewManipToolsetGui
from scToolsetGui import SCToolsetGui

# Define the class 
class SCCaeMainWindow(AFXMainWindow): 

    def __init__(self, app, windowTitle = ''):
        
        AFXMainWindow.__init__(self, app, windowTitle)
        
        # Register toolsets 
        self.registerToolset(FileToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBAR) 
        self.registerToolset(ModelToolsetGui(), GUI_IN_MENUBAR) 
        self.registerToolset(ViewManipToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBAR)
        self.registerToolset(CanvasToolsetGui(), GUI_IN_MENUBAR) 
        self.registerHelpToolset(HelpToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBAR) 
        self.registerToolset(AnnotationToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBAR) 
        self.registerToolset(DatumToolsetGui(), GUI_IN_TOOLBOX) 
        self.registerToolset(EditMeshToolsetGui(), GUI_IN_TOOLBOX) 
        self.registerToolset(PartitionToolsetGui(), GUI_IN_TOOLBOX) 
        self.registerToolset(QueryToolsetGui(), GUI_IN_TOOLBOX) 
        self.registerToolset(RepairToolsetGui(), GUI_IN_TOOLBOX) 
        self.registerToolset(SelectionToolsetGui(), GUI_IN_TOOLBAR) 
        self.registerToolset(TreeToolsetGui(), GUI_IN_TOOLBOX|GUI_IN_MENUBAR)
        self.registerToolset(SCToolsetGui(), GUI_IN_TOOLBOX|GUI_IN_TOOLBAR)                 # <----- SwiftComp toolset
        registerPluginToolset()
        
        # Register modules.
        self.registerModule('Part', 'Part') 
        self.registerModule('Property', 'Property') 
        self.registerModule('Assembly', 'Assembly') 
        self.registerModule('Step', 'Step') 
        self.registerModule('Interaction', 'Interaction') 
        self.registerModule('Load', 'Load')
        self.registerModule('Mesh', 'Mesh') 
        self.registerModule('Job', 'Job') 
        self.registerModule('Visualization', 'Visualization') 
        self.registerModule('Sketch', 'Sketch') 
