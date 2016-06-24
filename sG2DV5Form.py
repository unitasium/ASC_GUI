from abaqusGui import *
#from abaqusConstants import ALL
#import osutils, os
import sG2DV5DB


###########################################################################
# Class definition
#profile,vf_f,interface_flag,t_interface,modelName,fiber_matname,matrix_matname,mesh_size,elem_type
###########################################################################

class SG2DV5Form(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='create2DV5SG',
            objectName='sg2DV5Main', registerQuery=False)
  
        self.profileKw = AFXIntKeyword(self.cmd, 'profile', True, 1,evalExpression=False)

        
        self.fiber_flagKw = AFXIntKeyword(self.cmd, 'fiber_flag', True, 1,evalExpression=False)
        self.vf_fKw = AFXFloatKeyword(self.cmd, 'vf_f', True)#, 0.4)  
        
        self.interface_flagKw = AFXIntKeyword(self.cmd, 'interface_flag', True, 1,evalExpression=False)
        self.t_interfaceKw = AFXFloatKeyword(self.cmd, 't_interface', True, 0.0)
        
        self.model_nameKw = AFXStringKeyword(self.cmd, 'model_name', True, '')
        self.fiber_matnameKw = AFXStringKeyword(self.cmd, 'fiber_matname', True, '')
        self.matrix_matnameKw = AFXStringKeyword(self.cmd, 'matrix_matname', True, '')
        self.interface_matnameKw = AFXStringKeyword(self.cmd, 'interface_matname', True, '')

        self.mesh_sizeKw = AFXFloatKeyword(self.cmd, 'mesh_size', True, 0.1)
        self.elem_typeKw = AFXStringKeyword(self.cmd, 'elem_type', True, 'Linear')
        
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import sG2DV5DB
        reload(sG2DV5DB)
        return sG2DV5DB.SG2DV5DB(self)

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
#    buttonText='SG2DV5Button', 
#    object=SG2DV5_plugin(toolset),
#    messageId=AFXMode.ID_ACTIVATE,
#    icon=None,
#    kernelInitString='import sg2DMain',
#    applicableModules=ALL,
#    version='N/A',
#    author='N/A',
#    description='N/A',
#    helpUrl='N/A'
#)
