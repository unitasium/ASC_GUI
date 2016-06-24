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

class LocalDB(AFXDataDialog):
    
    # [
    #     ID_Macro1D, 
    #     ID_Macro2D, 
    #     ID_Macro3D, 
    #     ID_AnalysisNonThermal, 
    #     ID_AnalysisThermal, 
    #     ID_LAST
    # ] = range(AFXToolsetGui.ID_LAST, AFXToolsetGui.ID_LAST + 6)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Dehomogenization',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
        self.form = form
        w = 100  # width of table columns

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
        
        GroupBox_0 = FXGroupBox(p=self, text='SG Model Source',
                                opts=FRAME_GROOVE|LAYOUT_FILL_X)
        hf_source = FXHorizontalFrame(p=GroupBox_0, opts=0, x=0, y=0, w=0, h=0,
                                      pl=0, pr=0, pt=0, pb=0)
        
        FXRadioButton(p=hf_source, text='CAE',
                      tgt=form.sgmodel_sourceKw, sel=1)
        FXRadioButton(p=hf_source, text='SwiftComp Input file',
                      tgt=form.sgmodel_sourceKw, sel=2)
        
        
        self.swt_source = FXSwitcher(self, LAYOUT_FILL_X,
                                     0, 0, 0, 0, 0, 0, 0, 0)
        
        #--------------------------------------------------------------------
        # if sgmodel_sourceKw==1:  from CAE
        listVf = FXVerticalFrame(
            p=self.swt_source,
            opts=FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_X, 
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
            if len(names) !=0:
                form.sg_nameKw.setValue( names[0] )
        else:
            form.sg_nameKw.setValue('')
        
        
        
        #----------------------------------------------------------------------
        # if sgmodel_sourceKw==2:  from SwiftComp Input file
        VFrame_1 = FXVerticalFrame(
            p=self.swt_source,
            opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        VAligner_1 = AFXVerticalAligner(
            p=VFrame_1,
            opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        fileHandler = LocalDBFileHandler(form, 'sc_input', 'SC Input (*.sc)')
        fileTextHf = FXHorizontalFrame(
            p=VAligner_1,
            opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0,
            hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(
            p=fileTextHf, ncols=26, labelText='SwiftComp input file: ',
            tgt=form.sc_inputKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL)
        FXButton(p=fileTextHf, text='\tSelect File\nFrom Dialog',
                 ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
                 opts=BUTTON_NORMAL|LAYOUT_CENTER_Y,
                 x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)

        # ----Analysis type--------
        ComboBox_4 = AFXComboBox(
            p=VAligner_1, ncols=28, nvis=1, text='Analysis type: ', 
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
        # ------------------------------------------------------------
        ComboBox_1 = AFXComboBox(
            p=VAligner_1, ncols=28, nvis=1, text='Macroscopic model: ',
            tgt=form.macro_modelKw, sel=0)
        ComboBox_1.setMaxVisible(10)
        ComboBox_1.appendItem(text='1D (beam)', sel=1)
        ComboBox_1.appendItem(text='2D (shell)', sel=2)
        ComboBox_1.appendItem(text='3D (solid)', sel=3)

        FXCheckButton(p=VFrame_1, text='Aperiodic',
                      tgt=form.ap_flagKw, sel=0)

        FXHorizontalSeparator(p=self, x=0, y=0, w=0, h=0,
                              pl=2, pr=2, pt=2, pb=2)
        
        # -------------------------------------------------------------------
        # Macroscopic results -----------------------------------------------
        l = FXLabel(p=self, text='Macroscopic analysis results', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) )
        
        # Displacements......................................................
        gb_v = FXGroupBox(
            p=self, text='Displacements',
            opts=FRAME_GROOVE|LAYOUT_FILL_X)
        vf_v = FXVerticalFrame(
            gb_v, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_v = AFXTable(vf_v, 2, 3, 2, 3, form.vKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_v.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_v.setLeadingRows(1)
        t_v.setLeadingRowLabels('v1\tv2\tv3')
        t_v.setColumnWidth(-1, w)
        t_v.setColumnJustify(-1, AFXTable.RIGHT)
        t_v.showHorizontalGrid(True)
        t_v.showVerticalGrid(True)
        
        # Rotations..........................................................
        gb_c = FXGroupBox(p=self, text='Rotations', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        vf_c = FXVerticalFrame(
            gb_c, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_c = AFXTable(vf_c, 3, 3, 2, 3, form.cKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_c.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_c.setColumnWidth(-1, w)
        t_c.setColumnJustify(-1, AFXTable.RIGHT)
        t_c.showHorizontalGrid(True)
        t_c.showVerticalGrid(True)
        
        # Generalized strains................................................
        gb_e = FXGroupBox(p=self, text='Generalized strains',
                          opts=FRAME_GROOVE|LAYOUT_FILL_X)
        self.swt_drs = FXSwitcher(gb_e, 0, 0,0,0,0, 0,0,0,0)
        # 1D........
        vf_1d = FXVerticalFrame(self.swt_drs, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        vf_be = FXVerticalFrame(
            vf_1d, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_be = AFXTable(vf_be, 2, 1, 2, 1, form.beKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_be.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_be.setLeadingRows(1)
        t_be.setLeadingRowLabels('epsilon11')
        t_be.setColumnWidth(-1, w)
        t_be.setColumnJustify(-1, AFXTable.RIGHT)
        t_be.showHorizontalGrid(True)
        t_be.showVerticalGrid(True)

        vf_bk = FXVerticalFrame(
            vf_1d, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_bk = AFXTable(vf_bk, 2, 3, 2, 3, form.bkKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_bk.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_bk.setLeadingRows(1)
        t_bk.setLeadingRowLabels('kappa11\tkappa12\tkappa13')
        t_bk.setColumnWidth(-1, w)
        t_bk.setColumnJustify(-1, AFXTable.RIGHT)
        t_bk.showHorizontalGrid(True)
        t_bk.showVerticalGrid(True)
        
        # 2D........
        vf_2d = FXVerticalFrame(self.swt_drs, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        vf_se = FXVerticalFrame(
            vf_2d, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_se = AFXTable(vf_se, 2, 3, 2, 3, form.seKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_se.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_se.setLeadingRows(1)
        t_se.setLeadingRowLabels('epsilon11\t2epsilon12\tepsilon22')
        t_se.setColumnWidth(-1, w)
        t_se.setColumnJustify(-1, AFXTable.RIGHT)
        t_se.showHorizontalGrid(True)
        t_se.showVerticalGrid(True)

        vf_sk = FXVerticalFrame(
            vf_2d, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_sk = AFXTable(vf_sk, 2, 3, 2, 3, form.skKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_sk.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_sk.setLeadingRows(1)
        t_sk.setLeadingRowLabels('kappa11\tkappa12+21\tkappa22')
        t_sk.setColumnWidth(-1, w)
        t_sk.setColumnJustify(-1, AFXTable.RIGHT)
        t_sk.showHorizontalGrid(True)
        t_sk.showVerticalGrid(True)
        
        # 3D........
        vf_3d = FXVerticalFrame(self.swt_drs, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        vf_en = FXVerticalFrame(
            vf_3d, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_en = AFXTable(vf_en, 2, 3, 2, 3, form.enKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_en.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_en.setLeadingRows(1)
        t_en.setLeadingRowLabels('epsilon11\tepsilon22\tepsilon33')
        t_en.setColumnWidth(-1, w)
        t_en.setColumnJustify(-1, AFXTable.RIGHT)
        t_en.showHorizontalGrid(True)
        t_en.showVerticalGrid(True)

        vf_es = FXVerticalFrame(
            vf_3d, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        t_es = AFXTable(vf_es, 2, 3, 2, 3, form.esKw, 0,
                       AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        t_es.setPopupOptions(
            AFXTable.POPUP_COPY|AFXTable.POPUP_CUT|AFXTable.POPUP_PASTE)
        t_es.setLeadingRows(1)
        t_es.setLeadingRowLabels('2epsilon23\t2epsilon13\t2epsilon12')
        t_es.setColumnWidth(-1, w)
        t_es.setColumnJustify(-1, AFXTable.RIGHT)
        t_es.showHorizontalGrid(True)
        t_es.showVerticalGrid(True)
        
        # Additional inputs................................................
        GroupBox_4 = FXGroupBox(p=self, text='Additional inputs',
                                opts=FRAME_GROOVE|LAYOUT_FILL_X)
        
        # temperature........
        HFrame_6=FXHorizontalFrame(p=GroupBox_4, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        VAligner_14 = AFXVerticalAligner(p=HFrame_6, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        self.tempdiff = AFXTextField(
            p=VAligner_14, ncols=12, labelText='temperature increment',
            tgt=form.tmKw, sel=0)

        
        #---------------------------------------------------------------------
        
        # FXMAPFUNC(self, SEL_COMMAND, self.ID_Macro1D, LocalDB.onMacro1D)
        # FXMAPFUNC(self, SEL_COMMAND, self.ID_Macro2D, LocalDB.onMacro2D)
        # FXMAPFUNC(self, SEL_COMMAND, self.ID_Macro3D, LocalDB.onMacro3D)
        
        # FXMAPFUNC(self, SEL_COMMAND, self.ID_AnalysisNonThermal,
        #           LocalDB.onAnalysisNonThermal)
        # FXMAPFUNC(self, SEL_COMMAND, self.ID_AnalysisThermal,
        #           LocalDB.onAnalysisThermal)
        
        # self.addTransition(
        #     form.macro_modelKw, AFXTransition.EQ, 1, self,
        #     MKUINT(self.ID_Macro1D, SEL_COMMAND), None)
        # self.addTransition(
        #     form.macro_modelKw, AFXTransition.EQ, 2, self,
        #     MKUINT(self.ID_Macro2D, SEL_COMMAND), None)
        # self.addTransition(
        #     form.macro_modelKw, AFXTransition.EQ, 3, self,
        #     MKUINT(self.ID_Macro3D, SEL_COMMAND), None)
                           
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
        #     form.analysisKw, AFXTransition.EQ, 5, self,
        #     MKUINT(self.ID_AnalysisNonThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 1, self,
        #     MKUINT(self.ID_AnalysisThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 4, self,
        #     MKUINT(self.ID_AnalysisThermal, SEL_COMMAND), None)
        # self.addTransition(
        #     form.analysisKw, AFXTransition.EQ, 6, self,
        #     MKUINT(self.ID_AnalysisThermal, SEL_COMMAND), None)

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):
        
        self.tempdiff.disable()
        self.swt_source.setCurrent(0)
        AFXDataDialog.show(self)

        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def processUpdates(self):
        
        if self.form.sgmodel_sourceKw.getValue() == 1:
            self.swt_source.setCurrent(0)
            sg_name = self.form.sg_nameKw.getValue()
            if sg_name != '':
                macro_model_d = mdb.customData.sgs[sg_name].macro_model_dimension
                macro_model = int(macro_model_d.strip('D'))
                self.swt_drs.setCurrent(macro_model-1)
                # if macro_model == 1:
                #     self.swt_drs.setCurrent(0)
                # elif macro_model == 2:
                #     self.swt_drs.setCurrent(1)
                # elif macro_model == 3:
                #     self.swt_drs.setCurrent(2)

                analysis = mdb.customData.sgs[sg_name].analysis
                if analysis in [0, 2, 3, 5]:
                    self.tempdiff.disable()
                elif analysis in [1, 4, 6]:
                    self.tempdiff.enable()
            else:
                self.swt_drs.setCurrent(2)
        elif self.form.sgmodel_sourceKw.getValue() == 2:
            self.swt_source.setCurrent(1)
            macro_model = self.form.macro_modelKw.getValue()
            self.swt_drs.setCurrent(macro_model-1)

            analysis = self.form.analysisKw.getValue()
            if analysis in [0, 2, 3, 33, 5]:
                self.tempdiff.disable()
            elif analysis in [1, 4, 44, 6]:
                self.tempdiff.enable()
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    def updateComboBox_1Parts(self):
#
#        modelName = self.form.model_nameKw.getValue()
#
#        # Update the names in the Parts combo
#        #
#        self.ComboBox_1.clearItems()
#        names = mdb.models[modelName].parts.keys()
#        names.sort()
#        for name in names:
#            self.ComboBox_1.appendItem(name)
#        if names:
#            if not self.form.part_nameKw.getValue() in names:
#                self.form.part_nameKw.setValue( names[0] )
#        else:
#            self.form.part_nameKw.setValue('')
#
#        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )
    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def onMacro1D(self, sender, sel, ptr):
    #     
    #     self.swt_drs.setCurrent(0)
    #     
    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def onMacro2D(self, sender, sel, ptr):
    #     
    #     self.swt_drs.setCurrent(1)
    #     
    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def onMacro3D(self, sender, sel, ptr):
    #     
    #     self.swt_drs.setCurrent(2)
    # 
    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def onAnalysisNonThermal(self, sender, sel, ptr):
    #     
    #     self.tempdiff.disable()
    #     
    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def onAnalysisThermal(self, sender, sel, ptr):
    #     
    #     self.tempdiff.enable()
        
    
###########################################################################
# Class definition
###########################################################################

class LocalDBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, LocalDBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
