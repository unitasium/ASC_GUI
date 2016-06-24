# -*- coding: utf-8 -*-

#from abaqusConstants import *
from abaqusGui import *
#from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class MacroDB(AFXDataDialog):
    
    [
        ID_Macro1D,
        ID_Macro2D,
        ID_Macro3D,
        ID_AnalysisNonThermal,
        ID_AnalysisThermal,
        ID_LAST
    ] = range(AFXToolsetGui.ID_LAST, AFXToolsetGui.ID_LAST + 6)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Import homogenized properties',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
        self.form = form

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
        
        GroupBox_0 = FXGroupBox(
            p=self, text='SG Model Source', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        hf_source = FXHorizontalFrame(
            p=GroupBox_0, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)

        FXRadioButton(
            p=hf_source, text='CAE', tgt=form.sgmodel_sourceKw, sel=1)
        FXRadioButton(
            p=hf_source, text='SwiftComp homogenized properties file',
            tgt=form.sgmodel_sourceKw, sel=2)

        self.swt_source = FXSwitcher(self, 0, 0,0,0,0, 0,0,0,0)
        
        #--------------------------------------------------------------------
        # if sgmodel_sourceKw==1:  from CAE
        listVf = FXVerticalFrame(
            p=self.swt_source, opts=FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_X, 
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
            
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        listVf.setSelector(99)
        self.List_sg = AFXList(
            p=listVf, nvis=8, tgt=form.sg_nameKw, sel=0,
            opts=HSCROLLING_OFF|LIST_SINGLESELECT|LAYOUT_FILL_X)
        
#        msgCount = 169
#        form.model_nameKw.setTarget(self)
#        form.model_nameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
#        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_1PartsChanged'
#        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )
        
        names = mdb.customData.sgs.keys()
        names.sort()
        for name in names:
            self.List_sg.appendItem(name)
        
        if not form.sg_nameKw.getValue() in names:
            if len(names) != 0:
                form.sg_nameKw.setValue(names[0])
        else:
            form.sg_nameKw.setValue('')
        
        # ------------------------------------------------------------
        # if sgmodel_sourceKw==2:  from SwiftComp Input file
        VFrame_1 = FXVerticalFrame(
            p=self.swt_source, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        VAligner_1 = AFXVerticalAligner(
            p=VFrame_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        fileHandler = MacroDBFileHandler(
            form, 'sc_input_k', 'SC Output (*.sc.k)')
        fileTextHf = FXHorizontalFrame(
            p=VAligner_1, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0,
            hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(
            p=fileTextHf, ncols=32,
            labelText='SwiftComp homogenized properties file: ',
            tgt=form.sc_input_kKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL)
        FXButton(
            p=fileTextHf, text='\tSelect File\nFrom Dialog', ic=icon,
            tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y,
            x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        
        # ----Analysis type--------
        
        ComboBox_4 = AFXComboBox(
            p=VAligner_1, ncols=32, nvis=1, text='Analysis type: ',
            tgt=form.analysisKw, sel=0)
        ComboBox_4.setMaxVisible(10)
        ComboBox_4.appendItem(text='Elastic', sel=0)
        ComboBox_4.appendItem(text='ThermoElastic', sel=1)
        ComboBox_4.appendItem(text='Conduction', sel=2)
        ComboBox_4.appendItem(text='PiezoElectric', sel=3)
        ComboBox_4.appendItem(text='PiezoMagnetic', sel=33)
        ComboBox_4.appendItem(text='ThermoPiezoElectric', sel=4)
        ComboBox_4.appendItem(text='ThermoPiezoMagnetic', sel=44)
        ComboBox_4.appendItem(text='PiezoElectroMagnetic', sel=5)
        ComboBox_4.appendItem(text='ThermoPiezoElectroMagnetic', sel=6)
        #-------------------------------------------------------------
        ComboBox_1 = AFXComboBox(
            p=VAligner_1, ncols=32, nvis=1, text='Macroscopic model: ',
            tgt=form.macro_modelKw, sel=0)
        ComboBox_1.setMaxVisible(10)
        ComboBox_1.appendItem(text='1D (beam)', sel=1)
        ComboBox_1.appendItem(text='2D (shell)', sel=2)
        ComboBox_1.appendItem(text='3D (solid)', sel=3)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):
        
        
        self.swt_source.setCurrent(0)
        AFXDataDialog.show(self)

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def processUpdates(self):
        
        if self.form.sgmodel_sourceKw.getValue() == 1:
            self.swt_source.setCurrent(0)
#            sg_name=self.form.sg_nameKw.getValue()
#            if sg_name !='':
#                macro_model_dimension=mdb.customData.sgs[sg_name].macro_model_dimension
#                macro_model=int(macro_model_dimension.strip('D'))
#                if macro_model==1:
#                    self.swt_drs.setCurrent(0)
#                elif macro_model==2:
#                    self.swt_drs.setCurrent(1)
#                elif macro_model==3:
#                    self.swt_drs.setCurrent(2)
#            else:
#                self.swt_drs.setCurrent(2)
        elif self.form.sgmodel_sourceKw.getValue() == 2:
            self.swt_source.setCurrent(1)
            
###########################################################################
# Class definition
###########################################################################

class MacroDBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, MacroDBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
            
