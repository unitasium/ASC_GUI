# -*- coding: utf-8 -*-

from abaqusGui import *
#from abaqusConstants import *
#import osutils, os
import scLocalDB


###########################################################################
# Class definition
###########################################################################

class LocalForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(
            mode=self, method='localization',
            objectName='scLocalMain', registerQuery=False)
        pickedDefault = ''
        self.sgmodel_sourceKw = AFXIntKeyword(
            self.cmd, 'sgmodel_source', True, 1)
        self.sg_nameKw = AFXStringKeyword(self.cmd, 'sg_name', True)
        self.sc_inputKw = AFXStringKeyword(self.cmd, 'sc_input', True, '')
        self.ap_flagKw = AFXBoolKeyword(
            self.cmd, 'ap_flag', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.macro_modelKw = AFXIntKeyword(
            self.cmd, 'macro_model', True, 3, evalExpression=False)
        self.analysisKw = AFXIntKeyword(
            self.cmd, 'analysis', True, 0, evalExpression=False)

        # Displacements
        self.vKw = AFXTableKeyword(self.cmd, 'v', True)
        self.vKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.vKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.vKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.vKw.setRow(0, '0.0, 0.0, 0.0')

        # Rotations
        self.cKw = AFXTableKeyword(self.cmd, 'c', True)
        self.cKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.cKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.cKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.cKw.setRow(0, '1.0, 0.0, 0.0')
        self.cKw.setRow(1, '0.0, 1.0, 0.0')
        self.cKw.setRow(2, '0.0, 0.0, 1.0')

        # Strains
        # 1D
        self.beKw = AFXTableKeyword(self.cmd, 'be', True)
        self.beKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.beKw.setRow(0, '0.0')

        self.bkKw = AFXTableKeyword(self.cmd, 'bk', True)
        self.bkKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.bkKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.bkKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.bkKw.setRow(0, '0.0, 0.0, 0.0')

        # 2D
        self.seKw = AFXTableKeyword(self.cmd, 'se', True)
        self.seKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.seKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.seKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.seKw.setRow(0, '0.0, 0.0, 0.0')

        self.skKw = AFXTableKeyword(self.cmd, 'sk', True)
        self.skKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.skKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.skKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.skKw.setRow(0, '0.0, 0.0, 0.0')

        # 3D
        self.enKw = AFXTableKeyword(self.cmd, 'en', True)
        self.enKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.enKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.enKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.enKw.setRow(0, '0.0, 0.0, 0.0')

        self.esKw = AFXTableKeyword(self.cmd, 'es', True)
        self.esKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.esKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.esKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.esKw.setRow(0, '0.0, 0.0, 0.0')

        self.tmKw = AFXFloatKeyword(self.cmd, 'tm', True, 0.0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

#        import scLocalDB
        reload(scLocalDB)
        return scLocalDB.LocalDB(self)

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

