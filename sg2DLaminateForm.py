from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class SG2DLaminateForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='assignLayups',
            objectName='sg2DLaminateMain', registerQuery=False)
        pickedDefault = ''
        self.areaKw = AFXObjectKeyword(self.cmd, 'area', TRUE, pickedDefault)
        self.baselineKw = AFXObjectKeyword(self.cmd, 'baseline', TRUE, pickedDefault)
        self.oppositeKw = AFXObjectKeyword(self.cmd, 'opposite', True, pickedDefault)
        self.nspKw = AFXIntKeyword(self.cmd, 'nsp', True, 20)
        self.model_nameKw = AFXStringKeyword(self.cmd, 'model_name', True)
        self.section_nameKw = AFXStringKeyword(self.cmd, 'section_name', True)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import sg2DLaminateDB
        return sg2DLaminateDB.SG2DLaminateDB(self)

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
    def deactivate(self):
        
        self.oppositeKw.setValueToDefault()
        
        AFXForm.deactivate(self)

