from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class SG2DLaminateEraseDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):
        
        self.form = form

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Erase Layups',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
        
#        layout_m = FXMatrix(p=self, n=2, opts=MATRIX_BY_COLUMNS)

        # ----------------------------------------------------------------------
        pickHf = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        pickHf.setSelector(99)
        label = FXLabel(p=pickHf, text='Pick a baseline: ' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler = Erase_layupsDBPickHandler(form, form.baselineKw, 'Pick an entity', EDGES, ONE, label)
        icon = afxGetIcon('select', AFX_ICON_SMALL )
        FXButton(p=pickHf, text='\tPick Items in Viewport', ic=icon, tgt=pickHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)

        # Register a query on sections
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.model_nameKw.setValue(self.currentModelName)
#        mdb.models[self.currentModelName].sections.registerQuery(self.updateComboBox_1Sections)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

#        mdb.models[self.currentModelName].sections.unregisterQuery(self.updateComboBox_1Sections)



###########################################################################
# Class definition
###########################################################################

class Erase_layupsDBPickHandler(AFXProcedure):

    count = 0
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, prompt, entitiesToPick, numberToPick, label):
    
            self.form = form
            self.keyword = keyword
            self.prompt = prompt
            self.entitiesToPick = entitiesToPick # Enum value
            self.numberToPick = numberToPick # Enum value
            self.label = label
            self.labelText = label.getText()
    
            AFXProcedure.__init__(self, form.getOwner())
    
            Erase_layupsDBPickHandler.count += 1
            self.setModeName('Erase_layupsDBPickHandler%d' % (Erase_layupsDBPickHandler.count) )
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstStep(self):
    
            return  AFXPickStep(self, self.keyword, self.prompt, 
                self.entitiesToPick, self.numberToPick, sequenceStyle=TUPLE)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getNextStep(self, previousStep):
    
            self.label.setText( self.labelText.replace('None', 'Picked') )
            return None
