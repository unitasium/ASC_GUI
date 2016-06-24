# -*- coding: utf-8 -*-

from abaqusGui import *
#from abaqusConstants import *
#import osutils, os
import scHomoDB

###########################################################################
# Class definition
###########################################################################

class HomoForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='homogenization',
            objectName='scHomoMain', registerQuery=False)
        
        self.new_filenameKw = AFXStringKeyword(self.cmd, 'new_filename', True, '')
        
        self.model_sourceKw = AFXIntKeyword(self.cmd, 'model_source', True, 1)
        self.model_nameKw = AFXStringKeyword(self.cmd, 'model_name', True)
        self.part_nameKw = AFXStringKeyword(self.cmd, 'part_name', True)
        self.abaqus_inputKw = AFXStringKeyword(self.cmd, 'abaqus_input', True, '')
        
        self.macro_modelKw = AFXIntKeyword(self.cmd, 'macro_model', True, 3,)
        self.specific_modelKw = AFXIntKeyword(self.cmd, 'specific_model', True, 0, evalExpression=False)

        self.bkKw = AFXTableKeyword(self.cmd, 'bk', True)
        self.bkKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.bkKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.bkKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.bkKw.setRow(0, '0.0, 0.0, 0.0')

        self.skKw = AFXTableKeyword(self.cmd, 'sk', True)
        self.skKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.skKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.skKw.setRow(0, '0.0, 0.0')

        self.cosKw = AFXTableKeyword(self.cmd, 'cos', True)
        self.cosKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.cosKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.cosKw.setRow(0, '1.0, 0.0')
        
        self.wKw = AFXStringKeyword(self.cmd, 'w', True, '')
        
        self.analysisKw = AFXIntKeyword(
            self.cmd, 'analysis', True, 0, evalExpression=False)
        self.elem_flagKw = AFXIntKeyword(
            self.cmd, 'elem_flag', True, 0, evalExpression=False)
        self.trans_flagKw = AFXIntKeyword(
            self.cmd, 'trans_flag', True, 0, evalExpression=False)
        self.temp_flagKw = AFXIntKeyword(
            self.cmd, 'temp_flag', True, 0, evalExpression=False)

        self.ap1Kw = AFXBoolKeyword(
            self.cmd, 'ap1', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.ap2Kw = AFXBoolKeyword(
            self.cmd, 'ap2', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.ap3Kw = AFXBoolKeyword(
            self.cmd, 'ap3', AFXBoolKeyword.TRUE_FALSE, True, False)

        self.gen_input_onlyKw = AFXBoolKeyword(
            self.cmd, 'gen_input_only', AFXBoolKeyword.TRUE_FALSE, True, False)
        
        # self.ap000Kw = AFXBoolKeyword(self.cmd, 'ap000', AFXBoolKeyword.TRUE_FALSE, True, False) 
        # self.ap100Kw = AFXBoolKeyword(self.cmd, 'ap100', AFXBoolKeyword.TRUE_FALSE, True, False) 
        # self.ap010Kw = AFXBoolKeyword(self.cmd, 'ap010', AFXBoolKeyword.TRUE_FALSE, True, False) 
        # self.ap001Kw = AFXBoolKeyword(self.cmd, 'ap001', AFXBoolKeyword.TRUE_FALSE, True, False) 
        # 
        # self.ap111Kw = AFXBoolKeyword(self.cmd, 'ap111', AFXBoolKeyword.TRUE_FALSE, True, False) 
        # self.ap110Kw = AFXBoolKeyword(self.cmd, 'ap110', AFXBoolKeyword.TRUE_FALSE, True, False) 
        # self.ap101Kw = AFXBoolKeyword(self.cmd, 'ap101', AFXBoolKeyword.TRUE_FALSE, True, False) 
        # self.ap011Kw = AFXBoolKeyword(self.cmd, 'ap011', AFXBoolKeyword.TRUE_FALSE, True, False) 
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import scHomoDB
        reload(scHomoDB)
        return scHomoDB.HomoDB(self)

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

