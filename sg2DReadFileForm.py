from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class SG2DReadFileForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='createSGfromFile',
            objectName='sg2DReadFileMain', registerQuery=False)
        pickedDefault = ''
        self.project_nameKw = AFXStringKeyword(self.cmd, 'project_name', True, '')
        self.profile_nameKw = AFXStringKeyword(self.cmd, 'control_file', True, '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import sg2DReadFileDB
        return sg2DReadFileDB.SG2DReadFileDB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Register the plug-in
##
#thisPath = os.path.abspath(__file__)
#thisDir = os.path.dirname(thisPath)
#
#toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
#toolset.registerGuiMenuButton(
#    buttonText='preSC-Airfoil', 
#    object=Psa_plugin(toolset),
#    messageId=AFXMode.ID_ACTIVATE,
#    icon=None,
#    kernelInitString='import psa_one',
#    applicableModules=ALL,
#    version='N/A',
#    author='N/A',
#    description='N/A',
#    helpUrl='N/A'
#)
