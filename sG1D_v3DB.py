from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class SG1D_v3DB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, '1D Structure Genome',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
        
        self.form = form
        
        GroupBox_1 = FXGroupBox(p=self, text='Select a method', opts=FRAME_GROOVE|LAYOUT_FILL_X)

        FXRadioButton(p=GroupBox_1, text='Fast Generate', tgt=form.methodKw, sel=1)
        FXRadioButton(p=GroupBox_1, text='Composite Layup', tgt=form.methodKw, sel=2)
        FXRadioButton(p=GroupBox_1, text='Composite Section', tgt=form.methodKw, sel=3)
        FXRadioButton(p=GroupBox_1, text='Read from file', tgt=form.methodKw, sel=4)
        
        self.swt_source = FXSwitcher(self, 0, 0,0,0,0, 0,0,0,0)
        
        # ----------------------------------------------------------------------
        # Fast Generate
        VFrame_2 = FXVerticalFrame(p=self.swt_source, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)
        
        GroupBox_5 = FXGroupBox(p=VFrame_2, text='Layup information', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        VAligner_2 = AFXVerticalAligner(p=GroupBox_5, opts=0, x=0, y=0, w=0, h=0,
                                        pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=VAligner_2, ncols=32, labelText='Layup:', tgt=form.layup_fgKw, sel=0)
        AFXTextField(p=VAligner_2, ncols=12, labelText='Ply thickness:', tgt=form.thickness_fgKw, sel=0)
        AFXTextField(p=VAligner_2, ncols=12, labelText='Offset ratio', tgt=form.offset_ratio_fgKw, sel=0)
        AFXNote(p=GroupBox_5, message='[45/-45]2s means [45/-45/45/-45/-45/45/-45/45]')
        
        GroupBox_4 = FXGroupBox(p=VFrame_2, text='Material', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        va = AFXVerticalAligner(p=GroupBox_4, opts=0, x=0, y=0, w=0, h=0,
                                pl=0, pr=0, pt=0, pb=0)
        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_1 = AFXComboBox(p=va, ncols=0, nvis=1, text='Model:', tgt=form.model_name_fgKw, sel=0)
        self.RootComboBox_1.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_1.appendItem(name)
        if not form.model_name_fgKw.getValue() in names:
            form.model_name_fgKw.setValue( names[0] )
        msgCount = 294
        form.model_name_fgKw.setTarget(self)
        form.model_name_fgKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_1MaterialsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Materials combo
        #
        self.ComboBox_1 = AFXComboBox(p=va, ncols=0, nvis=1, text='Material:', tgt=form.material_nameKw, sel=0)
        self.ComboBox_1.setMaxVisible(10)
        
        # ----------------------------------------------------------------------
        # Abaqus Composite Layup
        self.form = form
        VFrame_3 = FXVerticalFrame(p=self.swt_source, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)
        
        GroupBox_2 = FXGroupBox(p=VFrame_3, text='Layup infomation', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        VAligner_1 = AFXVerticalAligner(p=GroupBox_2, opts=0, x=0, y=0, w=0, h=0,
                                        pl=0, pr=0, pt=0, pb=0)
        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_3 = AFXComboBox(p=VAligner_1, ncols=0, nvis=1, text='Model:', tgt=form.model_name_abqKw, sel=0)
        self.RootComboBox_3.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_3.appendItem(name)
        if not form.model_name_abqKw.getValue() in names:
            form.model_name_abqKw.setValue( names[0] )
        msgCount = 295
        form.model_name_abqKw.setTarget(self)
        form.model_name_abqKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_3PartsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Parts combo
        #
        self.ComboBox_3 = AFXComboBox(p=VAligner_1, ncols=0, nvis=1, text='Part:', tgt=form.partNameKw, sel=0)
        self.ComboBox_3.setMaxVisible(10)
        msgCount = 512
        form.partNameKw.setTarget(self)
        form.partNameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_4LayupsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler))

        # Layups combo
        #
        self.ComboBox_4 = AFXComboBox(p=VAligner_1, ncols=0, nvis=1, text='Layup:', tgt=form.layup_abqKw, sel=0)
        self.ComboBox_4.setMaxVisible(10)
        
        # ----------------------------------------------------------------------
        # Abaqus Composite section
        VFrame_s = FXVerticalFrame(p=self.swt_source, opts=LAYOUT_FILL_X, 
                                   x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        
        GroupBox_s = FXGroupBox(p=VFrame_s, text='Layup infomation', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        VAligner_s = AFXVerticalAligner(p=GroupBox_s, opts=0, x=0, y=0, w=0, h=0,
                                        pl=0, pr=0, pt=0, pb=0)
        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_2 = AFXComboBox(p=VAligner_s, ncols=0, nvis=1, text='Model:', tgt=form.rf_model_nameKw, sel=0)
        self.RootComboBox_2.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_2.appendItem(name)
        if not form.rf_model_nameKw.getValue() in names:
            form.rf_model_nameKw.setValue( names[0] )
        msgCount = 7
        form.rf_model_nameKw.setTarget(self)
        form.rf_model_nameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_sSectionsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Sections combo
        #
        self.ComboBox_s = AFXComboBox(p=VAligner_s, ncols=0, nvis=1, text='Section:', tgt=form.rf_section_nameKw, sel=0)
        self.ComboBox_s.setMaxVisible(10)
        AFXTextField(p=VAligner_s, ncols=12, labelText='Part name:', tgt=form.rf_part_nameKw, sel=0)
        AFXTextField(p=VAligner_s, ncols=12, labelText='Offset ratio:', tgt=form.rf_offset_ratioKw, sel=0)
        
        # ----------------------------------------------------------------------
        # Read from file
        VFrame_4 = FXVerticalFrame(p=self.swt_source, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)
        va_rf = AFXVerticalAligner(p=VFrame_4, opts=0, x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)
        
        self.RootComboBox_8 = AFXComboBox(p=va_rf, ncols=0, nvis=1, text='Import layup to:', tgt=form.model_name_fileKw, sel=0)
        self.RootComboBox_8.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_8.appendItem(name)
        if not form.model_name_fileKw.getValue() in names:
            form.model_name_fileKw.setValue( names[0] )
        
        fileHandler = SG1D_v2DBFileHandler(form, 'file_layup_input', 'All files (*)')
        fileTextHf = FXHorizontalFrame(p=va_rf, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=32, labelText='Layup data file: ', tgt=form.file_layup_inputKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL )
        FXButton(p=fileTextHf, text='\tSelect File\nFrom Dialog', ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        GroupBox_3 = FXGroupBox(p=self, text='Mesh', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        ComboBox_2 = AFXComboBox(p=GroupBox_3, ncols=0, nvis=1, text='Element type:', tgt=form.element_typeKw, sel=0)
        ComboBox_2.setMaxVisible(10)
        ComboBox_2.appendItem(text='two-noded')
        ComboBox_2.appendItem(text='three-noded')
        ComboBox_2.appendItem(text='four-noded')
        ComboBox_2.appendItem(text='five-noded')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)
        self.currentModelName_aba=''
        self.currentModelName_rf=''
        self.currentModelName=''
        # Register a query on materials
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.model_name_fgKw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].materials.registerQuery(self.updateComboBox_1Materials)

        # Register a query on parts
        #
        self.currentModelName_aba = getCurrentContext()['modelName']
        self.form.model_name_abqKw.setValue(self.currentModelName_aba)
        mdb.models[self.currentModelName_aba].parts.registerQuery(self.updateComboBox_3Parts)
        
        partName = self.form.partNameKw.getValue()
        if not partName == '':
            mdb.models[self.currentModelName_aba].parts[partName].compositeLayups.registerQuery(self.updateComboBox_4Layups)
        
        # Register a query on Sections
        self.currentModelName_rf = getCurrentContext()['modelName']
        self.form.rf_model_nameKw.setValue(self.currentModelName_rf)
        mdb.models[self.currentModelName_rf].sections.registerQuery(self.updateComboBox_sSections)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)
        if self.currentModelName !='':
            mdb.models[self.currentModelName].materials.unregisterQuery(self.updateComboBox_1Materials)
        if self.currentModelName_aba !='':
            mdb.models[self.currentModelName_aba].parts.unregisterQuery(self.updateComboBox_3Parts)
        if self.currentModelName_rf !='':
            mdb.models[self.currentModelName_rf].sections.unregisterQuery(self.updateComboBox_sSections) 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def processUpdates(self):
        
        if self.form.methodKw.getValue() == 1:
            self.swt_source.setCurrent(0)
        elif self.form.methodKw.getValue() == 2:
            self.swt_source.setCurrent(1)
        elif self.form.methodKw.getValue() == 3:
            self.swt_source.setCurrent(2)
        elif self.form.methodKw.getValue() == 4:
            self.swt_source.setCurrent(3)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_1MaterialsChanged(self, sender, sel, ptr):

        self.updateComboBox_1Materials()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_1Materials(self):

        modelName = self.form.model_name_fgKw.getValue()

        # Update the names in the Materials combo
        #
        self.ComboBox_1.clearItems()
        names = mdb.models[modelName].materials.keys()
        names.sort()
        for name in names:
            self.ComboBox_1.appendItem(name)
        if names:
            if not self.form.material_nameKw.getValue() in names:
                self.form.material_nameKw.setValue( names[0] )
        else:
            self.form.material_nameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_3PartsChanged(self, sender, sel, ptr):

        self.updateComboBox_3Parts()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_3Parts(self):

        modelName = self.form.model_name_abqKw.getValue()

        # Update the names in the Parts combo
        #
        self.ComboBox_3.clearItems()
        names = mdb.models[modelName].parts.keys()
        names.sort()
        for name in names:
            self.ComboBox_3.appendItem(name)
        if names:
            if not self.form.partNameKw.getValue() in names:
                self.form.partNameKw.setValue( names[0] )
            self.updateComboBox_4Layups()
        else:
            self.form.partNameKw.setValue('')
            self.form.layup_abqKw.setValue('')
            self.ComboBox_4.clearItems()

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_4LayupsChanged(self, sender, sel, ptr):

        self.updateComboBox_4Layups()
        return 1
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_4Layups(self):


        modelName = self.form.model_name_abqKw.getValue()
        partName = self.form.partNameKw.getValue()

        # Update the names in the Parts combo
        #
        self.ComboBox_4.clearItems()
        names = mdb.models[modelName].parts[partName].compositeLayups.keys()
        names.sort()
        for name in names:
            self.ComboBox_4.appendItem(name)
        if names:
            if not self.form.layup_abqKw.getValue() in names:
                self.form.layup_abqKw.setValue( names[0] )
        else:
            self.form.layup_abqKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_sSectionsChanged(self, sender, sel, ptr):

        self.updateComboBox_sSections()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_sSections(self):

        modelName = self.form.rf_model_nameKw.getValue()
        
        # Update the names in the Sections combo
        #
        self.ComboBox_s.clearItems()
        names = []
        for name, section in mdb.models[modelName].sections.items():
            if 'Composite' in type(section).__name__:
                names.append(name)
        names.sort()
        for name in names:
            self.ComboBox_s.appendItem(name)
        if names:
            if not self.form.rf_section_nameKw.getValue() in names:
                self.form.rf_section_nameKw.setValue( names[0] )
        else:
            self.form.rf_section_nameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )



###########################################################################
# Class definition
###########################################################################

class SG1D_v2DBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, SG1D_v2DBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
