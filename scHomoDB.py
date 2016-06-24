# -*- coding: utf-8 -*-

#from abaqusConstants import *
from abaqusGui import *
#from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)
thisDir = os.path.join(thisDir, 'Image')


###########################################################################
# Class definition
###########################################################################

class HomoDB(AFXDataDialog):
    
    [
        ID_Model, 
        ID_AnalysisNonThermal, 
        ID_AnalysisThermal, 
        ID_LAST
    ] = range(AFXToolsetGui.ID_LAST, AFXToolsetGui.ID_LAST + 4)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Homogenization',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
        
        self.form = form
        w = 80  # width of table columns

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            
        HFrame_1 = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
            
        # ======================================================================
        # Left panel
        # ======================================================================
        
        VFrame_1 = FXVerticalFrame(p=HFrame_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        
        # ----------------------------------------------------------------------
        # New file name
        AFXTextField(p=VFrame_1, ncols=20, labelText='New SwiftComp file name: ', 
                     tgt=form.new_filenameKw, sel=0, opts=AFXTEXTFIELD_CHECKBUTTON)
        
        # ----------------------------------------------------------------------
        # Model source
        GroupBox_1 = FXGroupBox(p=VFrame_1, text='Model source', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        
        HFrame_2 = FXHorizontalFrame(p=GroupBox_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        FXRadioButton(p=HFrame_2, text='CAE', tgt=form.model_sourceKw, sel=1)
        FXRadioButton(p=HFrame_2, text='Input file', tgt=form.model_sourceKw, sel=2)
        
        self.swt_source = FXSwitcher(GroupBox_1, 0, 0,0,0,0, 0,0,0,0)
        
        # From CAE ----------
        frame = FXHorizontalFrame(self.swt_source, 0, 0,0,0,0, 0,0,0,0)
        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Model:', 
                                          tgt=form.model_nameKw, sel=0)
        self.RootComboBox_1.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_1.appendItem(name)
        if not form.model_nameKw.getValue() in names:
            form.model_nameKw.setValue( names[0] )
        form.model_nameKw.setTarget(self)
        form.model_nameKw.setSelector(self.ID_Model)
        msgHandler = str(self.__class__).split('.')[-1] + '.onComboBox_1PartsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, %d, %s)' % (self.ID_Model, msgHandler) )

        # Parts combo
        #
        self.ComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Part:', 
                                      tgt=form.part_nameKw, sel=0)
        self.ComboBox_1.setMaxVisible(10)
        
        # From input file ----------
        fileHandler = HomoDBFileHandler(form, 'abaqus_input', 'Input file (*.inp)')
        fileTextHf = FXHorizontalFrame(p=self.swt_source, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=36, labelText='Abaqus input file: ', tgt=form.abaqus_inputKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL )
        FXButton(p=fileTextHf, text='\tSelect File\nFrom Dialog', ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        
        # ----------------------------------------------------------------------
        # Macro model
        gb_macro = FXGroupBox(p=VFrame_1, text='Macroscopic model', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        hf_macro = FXHorizontalFrame(
            p=gb_macro, opts=LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
                                     
        # ......................................................................
        # Dimension
        gb_dimension = FXGroupBox(
            p=hf_macro, text='Dimension',
            opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        vf_dimension = FXVerticalFrame(
            p=gb_dimension, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        FXRadioButton(p=vf_dimension, text='1D (Beam)', tgt=form.macro_modelKw, sel=1)
        FXRadioButton(p=vf_dimension, text='2D (Shell)', tgt=form.macro_modelKw, sel=2)
        FXRadioButton(p=vf_dimension, text='3D (Solid)', tgt=form.macro_modelKw, sel=3)
        
        # ......................................................................
        # Dimensionally reducible structures
        GroupBox_2 = FXGroupBox(
            p=hf_macro, text='Dimensionally reducible structures',
            opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.gb_DRS = GroupBox_2
        
        self.cb_specificModel = AFXComboBox(
            p=GroupBox_2, ncols=24, nvis=1, text='Specific model: ', 
            tgt=form.specific_modelKw, sel=0)
        self.cb_specificModel.setMaxVisible(10)
        self.cb_specificModel.appendItem(text='Classical', sel=0)
        self.cb_specificModel.appendItem(text='Shear refined', sel=1)
        self.cb_specificModel.appendItem(text='Vlasov', sel=2)
        self.cb_specificModel.appendItem(text='Trapeze', sel=3)

        self.swt_drs = FXSwitcher(GroupBox_2, LAYOUT_FILL_X|LAYOUT_FILL_Y, 0,0,0,0, 0,0,0,0)
        
        # For beam model ----------
        vf = FXVerticalFrame(
            p=self.swt_drs, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        
        gb_bk = FXGroupBox(
            p=vf, text='Initial twist/curvature',
            opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        vf_k = FXVerticalFrame(gb_bk, FRAME_SUNKEN|FRAME_THICK,
                               0, 0, 0, 0, 0, 0, 0, 0)
        self.t_bk = AFXTable(vf_k, 2, 3, 2, 3, form.bkKw, 0,
                             AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_bk.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_bk.setLeadingRows(1)
        self.t_bk.setLeadingRowLabels('k11\tk12\tk13')
        self.t_bk.setColumnWidth(-1, w)
        self.t_bk.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_bk.showHorizontalGrid(True)
        self.t_bk.showVerticalGrid(True)

        gb_cos = FXGroupBox(
            p=vf, text='Oblique cross-section',
            opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        vf_cos = FXVerticalFrame(gb_cos, FRAME_SUNKEN|FRAME_THICK,
                                 0, 0, 0, 0, 0, 0, 0, 0)
        self.t_cos = AFXTable(vf_cos, 2, 2, 2, 2, form.cosKw, 0,
                              AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_cos.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_cos.setLeadingRows(1)
        self.t_cos.setLeadingRowLabels('cos(theta11)\tcos(theta21)')
        self.t_cos.setColumnWidth(-1, w)
        self.t_cos.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_cos.showHorizontalGrid(True)
        self.t_cos.showVerticalGrid(True)
        AFXNote(p=gb_cos, message='cos(theta11) + cos(theta21) <= 1.0')

        # For shell model ----------
        vf = FXVerticalFrame(
            p=self.swt_drs, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        
        gb_sk = FXGroupBox(
            p=vf, text='Initial twist/curvature',
            opts=FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        vf_sk = FXVerticalFrame(gb_sk, FRAME_SUNKEN|FRAME_THICK,
                                0, 0, 0, 0, 0, 0, 0, 0)
        self.t_sk = AFXTable(vf_sk, 2, 2, 2, 2, form.skKw, 0,
                             AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_sk.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_sk.setLeadingRows(1)
        self.t_sk.setLeadingRowLabels('k12\tk21')
        self.t_sk.setColumnWidth(-1, w)
        self.t_sk.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_sk.showHorizontalGrid(True)
        self.t_sk.showVerticalGrid(True)

        # For solids ----------
        VFrame = FXVerticalFrame(p=self.swt_drs, opts=0, x=0, y=0, w=0, h=0, 
                                 pl=0, pr=0, pt=0, pb=0)
        
        # ----------------------------------------------------------------------
        # Omega
        AFXTextField(p=VFrame_1, ncols=16, labelText='Omega: ', 
                     tgt=form.wKw, sel=0, opts=AFXTEXTFIELD_CHECKBUTTON)
        AFXNote(p=VFrame_1, message='Provide omega if the part is not a line, rectangle or cube')
        
        # ----------------------------------------------------------------------
        # Options
        GroupBox_5 = FXGroupBox(p=VFrame_1, text='Options', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        VAligner_1 = AFXVerticalAligner(p=GroupBox_5, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        
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
        
        ComboBox_5 = AFXComboBox(
            p=VAligner_1, ncols=32, nvis=1, text='Element type: ', 
            tgt=form.elem_flagKw, sel=0)
        ComboBox_5.setMaxVisible(10)
        ComboBox_5.appendItem(text='Regular', sel=0)
        ComboBox_5.appendItem(text='1D degenerated', sel=1)
        ComboBox_5.appendItem(text='2D degenerated', sel=2)
        
        ComboBox_6 = AFXComboBox(
            p=VAligner_1, ncols=32, nvis=1, text='Elemental orientation: ', 
            tgt=form.trans_flagKw, sel=0)
        ComboBox_6.setMaxVisible(10)
        ComboBox_6.appendItem(text='Global', sel=0)
        ComboBox_6.appendItem(text='Local', sel=1)
        
        self.cb_tempDistr = AFXComboBox(
            p=VAligner_1, ncols=32, nvis=1, text='Temperature distribution: ',
            tgt=form.temp_flagKw, sel=0)
        self.cb_tempDistr.setMaxVisible(10)
        self.cb_tempDistr.appendItem(text='Uniform', sel=0)
        self.cb_tempDistr.appendItem(text='Non-uniform', sel=1)
        
        gb_ap = FXGroupBox(
            p=VFrame_1, text='Aperiodic', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        hf_ap = FXHorizontalFrame(
            p=gb_ap, opts=LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        FXCheckButton(p=hf_ap, text='y1  ', tgt=form.ap1Kw, sel=0)
        FXCheckButton(p=hf_ap, text='y2  ', tgt=form.ap2Kw, sel=0)
        FXCheckButton(p=hf_ap, text='y3  ', tgt=form.ap3Kw, sel=0)
        
        FXCheckButton(
            p=VFrame_1,
            text='Only generate input file. Do not run SwiftComp.',
            tgt=form.gen_input_onlyKw, sel=0)

        # ----------------------------------------------------------------------
        
        # FXMAPFUNC(self, SEL_COMMAND, self.ID_AnalysisNonThermal,
        #           HomoDB.onAnalysisNonThermal)
        # FXMAPFUNC(self, SEL_COMMAND, self.ID_AnalysisThermal,
        #           HomoDB.onAnalysisThermal)
        # 
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 0, self,
        #     MKUINT(self.ID_AnalysisNonThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 2, self,
        #     MKUINT(self.ID_AnalysisNonThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 3, self,
        #     MKUINT(self.ID_AnalysisNonThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 33, self,
        #     MKUINT(self.ID_AnalysisNonThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 5, self,
        #     MKUINT(self.ID_AnalysisNonThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 1, self,
        #     MKUINT(self.ID_AnalysisThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 4, self,
        #     MKUINT(self.ID_AnalysisThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 44, self,
        #     MKUINT(self.ID_AnalysisThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 6, self,
        #     MKUINT(self.ID_AnalysisThermal, SEL_COMMAND), None)
        
        # ======================================================================
        # Right panel
        # ======================================================================
        
        VFrame_2 = FXVerticalFrame(
            p=HFrame_1, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=0, vs=0, opts=LAYOUT_CENTER_Y)
        self.swt_fig = FXSwitcher(VFrame_2, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        HFrame = FXHorizontalFrame(p=self.swt_fig, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=0, vs=0, opts=LAYOUT_FILL_Y|JUSTIFY_CENTER_Y)
        fileName = os.path.join(thisDir, 'oblique_cs.PNG')
        icon = afxCreateIcon(fileName)
        FXLabel(p=HFrame, text='', ic=icon)
        
        HFrame = FXHorizontalFrame(
            p=self.swt_fig, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=0, vs=0, opts=0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):
        
        self.gb_DRS.disable()
        self.cb_tempDistr.disable()
        self.swt_source.setCurrent(0)
        self.swt_drs.setCurrent(2)
        self.swt_fig.setCurrent(1)

        AFXDataDialog.show(self)

        # Register a query on parts
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.model_nameKw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].parts.registerQuery(self.updateComboBox_1Parts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        mdb.models[self.currentModelName].parts.unregisterQuery(self.updateComboBox_1Parts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def processUpdates(self):
        
        k = self.form.model_sourceKw.getValue()
        self.swt_source.setCurrent(k-1)
            
        if self.form.macro_modelKw.getValue() == 1:
            self.gb_DRS.enable()
            self.cb_specificModel.enable()
            self.swt_drs.setCurrent(0)
            self.swt_fig.setCurrent(0)
            if self.cb_specificModel.getNumItems() == 2:
                self.cb_specificModel.appendItem(text='Vlasov', sel=2)
                self.cb_specificModel.appendItem(text='Trapeze', sel=3)
        elif self.form.macro_modelKw.getValue() == 2:
            self.gb_DRS.enable()
            self.cb_specificModel.enable()
            self.swt_drs.setCurrent(1)
            self.swt_fig.setCurrent(1)
            if self.cb_specificModel.getNumItems() == 4:
                self.cb_specificModel.removeItem(3)
                self.cb_specificModel.removeItem(2)
        elif self.form.macro_modelKw.getValue() == 3:
            self.gb_DRS.disable()
            self.cb_specificModel.disable()
            self.swt_drs.setCurrent(2)
            self.swt_fig.setCurrent(1)

        a = self.form.analysisKw.getValue()
        if a in [0, 2, 3, 33, 5]:
            self.cb_tempDistr.disable()
        elif a in [1, 4, 44, 6]:
            self.cb_tempDistr.enable()
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_1PartsChanged(self, sender, sel, ptr):

        self.updateComboBox_1Parts()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_1Parts(self):

        modelName = self.form.model_nameKw.getValue()

        # Update the names in the Parts combo
        #
        self.ComboBox_1.clearItems()
        names = mdb.models[modelName].parts.keys()
        names.sort()
        for name in names:
            self.ComboBox_1.appendItem(name)
        if names:
            if not self.form.part_nameKw.getValue() in names:
                self.form.part_nameKw.setValue( names[-1] )
        else:
            self.form.part_nameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def onAnalysisNonThermal(self, sender, sel, ptr):
    #     
    #     self.cb_tempDistr.disable()
    #     
    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def onAnalysisThermal(self, sender, sel, ptr):
    #     
    #     self.cb_tempDistr.enable()

###########################################################################
# Class definition
###########################################################################

class HomoDBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, HomoDBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
