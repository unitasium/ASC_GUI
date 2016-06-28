# -*- coding: utf-8 -*-

from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class VabsForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='VABSMain',
            objectName='vabsMain', registerQuery=False)

        self.recover_flagKw = AFXIntKeyword(
            self.cmd, 'recover_flag', True, 1)
        self.vabs_inp_nameKw = AFXStringKeyword(
            self.cmd, 'vabs_inp_name', True, '')
        self.abq_inp_nameKw = AFXStringKeyword(
            self.cmd, 'abq_inp_name', True, '')
        self.timoshenko_flagKw = AFXBoolKeyword(
            self.cmd, 'timoshenko_flag',
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.thermal_flagKw = AFXBoolKeyword(
            self.cmd, 'thermal_flag',
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.trapeze_flagKw = AFXBoolKeyword(
            self.cmd, 'trapeze_flag',
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.vlasov_flagKw = AFXBoolKeyword(
            self.cmd, 'vlasov_flag',
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.curve_flagKw = AFXBoolKeyword(
            self.cmd, 'curve_flag',
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.kKw = AFXTableKeyword(self.cmd, 'k', True)
        self.kKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.kKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.kKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.kKw.setRow(0, '0.0, 0.0, 0.0')
        self.oblique_flagKw = AFXBoolKeyword(
            self.cmd, 'oblique_flag',
            AFXBoolKeyword.TRUE_FALSE, True, False)
        self.cosKw = AFXTableKeyword(self.cmd, 'cos', True)
        self.cosKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.cosKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.cosKw.setRow(0, '1.0, 0.0')

        # Recover
        self.model_recoverKw = AFXIntKeyword(
            self.cmd, 'model_recover', True, 1)

        self.vabs_rec_nameKw = AFXStringKeyword(
            self.cmd, 'vabs_rec_name', True, '')
        self.vabs_inp_name2Kw = AFXStringKeyword(
            self.cmd, 'vabs_inp_name2', True, '')

        self.uKw = AFXTableKeyword(self.cmd, 'u', True)
        self.uKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.uKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.uKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.uKw.setRow(0, '0.0, 0.0, 0.0')

        self.cKw = AFXTableKeyword(self.cmd, 'c', True)
        self.cKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.cKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.cKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.cKw.setRow(0, '1.0, 0.0, 0.0')
        self.cKw.setRow(1, '0.0, 1.0, 0.0')
        self.cKw.setRow(2, '0.0, 0.0, 1.0')

        # Sectional forces/moments
        self.sfKw = AFXTableKeyword(self.cmd, 'sf', True)
        self.sfKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.sfKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.sfKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.sfKw.setRow(0, '0.0, 0.0, 0.0')

        self.smKw = AFXTableKeyword(self.cmd, 'sm', True)
        self.smKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.smKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.smKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.smKw.setRow(0, '0.0, 0.0, 0.0')

        # Distributed forces/moments
        self.dfKw = AFXTableKeyword(self.cmd, 'df', True)
        self.dfKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.dfKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.dfKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.dfKw.setRow(0, '0.0, 0.0, 0.0')
        self.dfKw.setRow(1, '0.0, 0.0, 0.0')
        self.dfKw.setRow(2, '0.0, 0.0, 0.0')
        self.dfKw.setRow(3, '0.0, 0.0, 0.0')

        self.dmKw = AFXTableKeyword(self.cmd, 'dm', True)
        self.dmKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.dmKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.dmKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.dmKw.setRow(0, '0.0, 0.0, 0.0')
        self.dmKw.setRow(1, '0.0, 0.0, 0.0')
        self.dmKw.setRow(2, '0.0, 0.0, 0.0')
        self.dmKw.setRow(3, '0.0, 0.0, 0.0')

        # Strains/curvatures
        self.gammaKw = AFXTableKeyword(self.cmd, 'gamma', True)
        self.gammaKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.gammaKw.setRow(0, '0.0')

        self.kappaKw = AFXTableKeyword(self.cmd, 'kappa', True)
        self.kappaKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.kappaKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.kappaKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.kappaKw.setRow(0, '0.0, 0.0, 0.0')

        self.kappa_pKw = AFXTableKeyword(self.cmd, 'kappa_p', True)
        self.kappa_pKw.setColumnType(0, AFXTABLE_TYPE_FLOAT)
        self.kappa_pKw.setColumnType(1, AFXTABLE_TYPE_FLOAT)
        self.kappa_pKw.setColumnType(2, AFXTABLE_TYPE_FLOAT)
        self.kappa_pKw.setRow(0, '0.0, 0.0, 0.0')

        self.gen_inp_onlyKw = AFXBoolKeyword(
            self.cmd, 'gen_inp_only',
            AFXBoolKeyword.TRUE_FALSE, True, False)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import vabsDB
        return vabsDB.VabsDB(self)

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

        mainWindow = getAFXApp().getAFXMainWindow()
        
        if (self.recover_flagKw.getValue() == 1 and
            self.abq_inp_nameKw.getValue() == ''):
            msg = 'Abaqus input file is empty.'
            showAFXErrorDialog(mainWindow, msg)
            return False
        elif (self.recover_flagKw.getValue() == 2 and
              self.vabs_inp_name2Kw.getValue() == ''):
            msg = 'VABS input file is empty.'
            showAFXErrorDialog(mainWindow, msg)
            return False

        cos11 = float(self.cosKw.getValue(0, 0))
        cos21 = float(self.cosKw.getValue(0, 1))
        if cos11 + cos21 > 1.0:
            msg = 'Invalid cosines of oblique angles.'
            showAFXErrorDialog(mainWindow, msg)
            return False

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
# thisPath = os.path.abspath(__file__)
# thisDir = os.path.dirname(thisPath)

# toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
# toolset.registerGuiMenuButton(
    # buttonText='VABS', 
    # object=Vabs_plugin(toolset),
    # messageId=AFXMode.ID_ACTIVATE,
    # icon=None,
    # kernelInitString='import vabsMain',
    # applicableModules=ALL,
    # version='N/A',
    # author='N/A',
    # description='N/A',
    # helpUrl='N/A'
# )
