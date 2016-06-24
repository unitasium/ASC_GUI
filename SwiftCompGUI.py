# -*- coding: utf-8 -*-

# ******************************************************************************
# Custom Beam Frame Analysis GUI Application 
# This script creates and launches the Beam GUI application 
# ******************************************************************************

from abaqusGui import AFXApp
import sys
from scCaeMainWindow import SCCaeMainWindow

# Initialize application object 
# In AFXApp, appName and vendorName are displayed if productName is set to ''
# otherwise productName is displayed. 
app = AFXApp(appName = 'ABAQUS/CAE', 
             vendorName = 'SIMULIA', 
             productName = 'Abaqus-SwiftComp GUI', 
             majorNumber = 1, 
             minorNumber = 1, 
             updateNumber = 1, 
             prerelease = False)

app.init(sys.argv)

# Construct main window
SCCaeMainWindow(app)

# Create application
app.create()

# Run application
app.run()
