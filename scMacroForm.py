# -*- coding: utf-8 -*-
"""
Created on Wed May  4 21:03:49 2016

@author: peng69
"""

# -*- coding: utf-8 -*-

from abaqusGui import *
#from abaqusConstants import *
#import osutils, os
import scMacroDB


###########################################################################
# Class definition
###########################################################################

class MacroForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}
        
        self.cmd = AFXGuiCommand(mode=self, method='importSCmat',
            objectName='scMacroMat', registerQuery=False)
        pickedDefault = ''
        self.sgmodel_sourceKw = AFXIntKeyword(self.cmd, 'sgmodel_source', True, 1)
        self.sg_nameKw = AFXStringKeyword(self.cmd, 'sg_name', True)
        self.sc_input_kKw = AFXStringKeyword(self.cmd, 'sc_input_k', True, '')
        self.macro_modelKw = AFXIntKeyword(self.cmd, 'macro_model', True, 3, evalExpression=False)
        self.analysisKw = AFXIntKeyword(self.cmd, 'analysis', True, 0, evalExpression=False)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

#        import scMacroDB
        reload(scMacroDB)
        return scMacroDB.MacroDB(self)

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
        