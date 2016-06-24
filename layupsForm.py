from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class LayupsForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='addLayups',
            objectName='layupsMain', registerQuery=False)
        pickedDefault = ''
        self.methodKw = AFXIntKeyword(self.cmd, 'method', True, 1)
        self.fg_model_nameKw = AFXStringKeyword(self.cmd, 'fg_model_name', True)
        self.fg_material_nameKw = AFXStringKeyword(self.cmd, 'fg_material_name', True)
        self.fg_section_nameKw = AFXStringKeyword(self.cmd, 'fg_section_name', True)
        self.fg_layupKw = AFXStringKeyword(self.cmd, 'fg_layup', True, '')
        self.fg_ply_thicknessKw = AFXFloatKeyword(self.cmd, 'fg_ply_thickness', True)
        self.rf_model_nameKw = AFXStringKeyword(self.cmd, 'rf_model_name', True)
        self.rf_section_nameKw = AFXStringKeyword(self.cmd, 'rf_section_name', True)
        self.rf_material_fileKw = AFXStringKeyword(self.cmd, 'rf_material_file', True)
        self.rf_layup_fileKw = AFXStringKeyword(self.cmd, 'rf_layup_file', True, '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import layupsDB
        return layupsDB.LayupsDB(self)

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#
#thisPath = os.path.abspath(__file__)
#thisDir = os.path.dirname(thisPath)
#
#toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
#toolset.registerGuiMenuButton(
#    buttonText='Create Layups', 
#    object=Create_layups_plugin(toolset),
#    messageId=AFXMode.ID_ACTIVATE,
#    icon=None,
#    kernelInitString='',
#    applicableModules=ALL,
#    version='N/A',
#    author='N/A',
#    description='N/A',
#    helpUrl='N/A'
#)
