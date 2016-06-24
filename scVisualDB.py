from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class VisualDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(
            self, form, 'Visualization',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            
        VAligner_1 = AFXVerticalAligner(
            p=self, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        ComboBox_1 = AFXComboBox(
            p=VAligner_1, ncols=32, nvis=1, text='Macroscopic model: ',
            tgt=form.macro_modelKw, sel=0)
        ComboBox_1.setMaxVisible(10)
        ComboBox_1.appendItem(text='1D (beam)', sel=1)
        ComboBox_1.appendItem(text='2D (shell)', sel=2)
        ComboBox_1.appendItem(text='3D (block)', sel=3)
        
        fileHandler = Sc_visualDBFileHandler(
            form, 'sc_input', 'SwiftComp input (*.sc,*.sc?)\nAll file (*)')
        fileTextHf = FXHorizontalFrame(
            p=VAligner_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(
            p=fileTextHf, ncols=32, labelText='SwiftComp input: ',
            tgt=form.sc_inputKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL)
        FXButton(
            p=fileTextHf, text='	Select File\nFrom Dialog',
            ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y,
            x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)

        FXCheckButton(
            p=self, text='Aperiodic', tgt=form.ap_flagKw, sel=0)


###########################################################################
# Class definition
###########################################################################

class Sc_visualDBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, Sc_visualDBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
