from abaqusGui import *
from abaqusConstants import ALL
import osutils, os
import scVisualDB


###########################################################################
# Class definition
###########################################################################

class VisualForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='visualization',
            objectName='scVisualMain', registerQuery=False)
        pickedDefault = ''
        self.macro_modelKw = AFXIntKeyword(self.cmd, 'macro_model', True, 3, evalExpression=False)
        self.ap_flagKw = AFXBoolKeyword(self.cmd, 'ap_flag', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.sc_inputKw = AFXStringKeyword(self.cmd, 'sc_input', True, '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        reload(scVisualDB)
        return scVisualDB.VisualDB(self)

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
    def activate(self):
        
        switchModule('Visualization')
        AFXForm.activate(self)
