from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class SG2DLaminateDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):
        
        self.form = form

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Assign Layups',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
        
        layout_m = FXMatrix(p=self, n=2, opts=MATRIX_BY_COLUMNS)
            
        # ----------------------------------------------------------------------
#        pickHf = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
#            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
#        pickHf.setSelector(99)
        label = FXLabel(p=layout_m, text='Pick the layup area: ' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler = Assign_layupsDBPickHandler(form, form.areaKw, 'Pick an entity', FACES, ONE, label)
        icon = afxGetIcon('select', AFX_ICON_SMALL )
        FXButton(p=layout_m, text='\tPick Items in Viewport', ic=icon, tgt=pickHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)

        # ----------------------------------------------------------------------
#        pickHf = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
#            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
#        pickHf.setSelector(99)
        label = FXLabel(p=layout_m, text='Pick a baseline: ' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler = Assign_layupsDBPickHandler(form, form.baselineKw, 'Pick an entity', EDGES, ONE, label)
        icon = afxGetIcon('select', AFX_ICON_SMALL )
        FXButton(p=layout_m, text='\tPick Items in Viewport', ic=icon, tgt=pickHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)
        
        # ----------------------------------------------------------------------
#        pickHf = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
#            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
#        pickHf.setSelector(99)
        label = FXLabel(p=layout_m, text='Pick the opposite boundary: ' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler = Assign_layupsDBPickHandler(form, form.oppositeKw, 'Pick an entity', EDGES, ONE, label)
        icon = afxGetIcon('select', AFX_ICON_SMALL )
        FXButton(p=layout_m, text='\tPick Items in Viewport', ic=icon, tgt=pickHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)
            
        # ----------------------------------------------------------------------
        AFXTextField(p=self, ncols=10, labelText='Number of sampling points: ', 
                     tgt=form.nspKw, sel=0)
            
        # ----------------------------------------------------------------------
        frame = AFXVerticalAligner(self, 0, 0,0,0,0, 0,0,0,0)
        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Model:', tgt=form.model_nameKw, sel=0)
        self.RootComboBox_1.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_1.appendItem(name)
        if not form.model_nameKw.getValue() in names:
            form.model_nameKw.setValue( names[0] )
        msgCount = 7
        form.model_nameKw.setTarget(self)
        form.model_nameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_1SectionsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Sections combo
        #
        self.ComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Section:', tgt=form.section_nameKw, sel=0)
        self.ComboBox_1.setMaxVisible(10)

#        self.form = form

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)
        
#        self.form.oppositeKw.setValueToDefault()

        # Register a query on sections
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.model_nameKw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].sections.registerQuery(self.updateComboBox_1Sections)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        mdb.models[self.currentModelName].sections.unregisterQuery(self.updateComboBox_1Sections)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_1SectionsChanged(self, sender, sel, ptr):

        self.updateComboBox_1Sections()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_1Sections(self):

        modelName = self.form.model_nameKw.getValue()

        # Update the names in the Sections combo
        #
        self.ComboBox_1.clearItems()
#        names = mdb.models[modelName].sections.keys()
        names = []
        for name, section in mdb.models[modelName].sections.items():
#            section = mdb.models[modelName].sections[name]
            if 'Composite' in type(section).__name__:
                names.append(name)
        names.sort()
        for name in names:
            self.ComboBox_1.appendItem(name)
        if names:
            if not self.form.section_nameKw.getValue() in names:
                self.form.section_nameKw.setValue( names[0] )
        else:
            self.form.section_nameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )



###########################################################################
# Class definition
###########################################################################

class Assign_layupsDBPickHandler(AFXProcedure):

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

                Assign_layupsDBPickHandler.count += 1
                self.setModeName('Assign_layupsDBPickHandler%d' % (Assign_layupsDBPickHandler.count) )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getFirstStep(self):

                return  AFXPickStep(self, self.keyword, self.prompt, 
                    self.entitiesToPick, self.numberToPick, sequenceStyle=TUPLE)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getNextStep(self, previousStep):

                self.label.setText( self.labelText.replace('None', 'Picked') )
                return None
