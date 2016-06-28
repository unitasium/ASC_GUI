from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class VabsDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'VABS',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)

        self.form = form
        w = 80  # Column width of tables

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')

        GroupBox_2 = FXGroupBox(p=self, text='Analysis',
                                opts=FRAME_GROOVE|LAYOUT_FILL_X)
        FXRadioButton(p=GroupBox_2,
                      text='Carry out constitutive modeling',
                      tgt=form.recover_flagKw, sel=1)
        FXRadioButton(p=GroupBox_2, text='Recover',
                      tgt=form.recover_flagKw, sel=2)

        self.swt_analysis = FXSwitcher(self, 0,
                                       0, 0, 0, 0, 0, 0, 0, 0)

        FXCheckButton(p=self,
                      text='Only generate input file. Do not run VABS.',
                      tgt=form.gen_inp_onlyKw, sel=0)

        # ============================================================
        # Homogenization
        # ============================================================

        VFrame_3 = FXVerticalFrame(p=self.swt_analysis,
                                   opts=LAYOUT_FILL_X,
                                   x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)
        
        VAligner_1 = AFXVerticalAligner(p=VFrame_3, opts=0,
                                        x=0, y=0, w=0, h=0,
                                        pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=VAligner_1, ncols=40, labelText='New VABS file name: ',
                     tgt=form.vabs_inp_nameKw, sel=0,
                     opts=0)
        fileHandler = VabsDBFileHandler(
            form, 'abq_inp_name', 'Abaqus input files (*.inp)')
        fileTextHf = FXHorizontalFrame(p=VAligner_1, opts=0,
                                       x=0, y=0, w=0, h=0,
                                       pl=0, pr=0, pt=0, pb=0,
                                       hs=DEFAULT_SPACING,
                                       vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=40, labelText='Abaqus input file: ',
                     tgt=form.abq_inp_nameKw, sel=0,
                     opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL)
        FXButton(p=fileTextHf, text='	Select File\nFrom Dialog',
                 ic=icon,
                 tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
                 opts=BUTTON_NORMAL|LAYOUT_CENTER_Y,
                 x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        
        GroupBox_3 = FXGroupBox(p=VFrame_3, text='Options',
                                opts=FRAME_GROOVE|LAYOUT_FILL_X)
        FXCheckButton(p=GroupBox_3,
                      text='Include generalized Timoshenko model',
                      tgt=form.timoshenko_flagKw, sel=0)
        FXCheckButton(p=GroupBox_3,
                      text='Thermalelastic analysis',
                      tgt=form.thermal_flagKw, sel=0)
        FXCheckButton(p=GroupBox_3,
                      text='Obtain Trapeze effect',
                      tgt=form.trapeze_flagKw, sel=0)
        self.cb_vlasov = FXCheckButton(
            p=GroupBox_3,
            text='Obtain generalized Vlasov model',
            tgt=form.vlasov_flagKw, sel=0)

        self.cb_k = FXCheckButton(
            p=GroupBox_3,
            text='Initial twist/curvature',
            tgt=form.curve_flagKw, sel=0)
        vf_k = FXVerticalFrame(GroupBox_3, FRAME_SUNKEN|FRAME_THICK,
                               0, 0, 0, 0, 0, 0, 0, 0)
        self.t_k = AFXTable(vf_k, 2, 3, 2, 3, form.kKw, 0,
                            AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_k.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_k.setLeadingRows(1)
        self.t_k.setLeadingRowLabels('k1\tk2\tk3')
        self.t_k.setColumnWidth(-1, w)
        self.t_k.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_k.showHorizontalGrid(True)
        self.t_k.showVerticalGrid(True)

        self.cb_oblique = FXCheckButton(
            p=GroupBox_3, text='Oblique cross-section',
            tgt=form.oblique_flagKw, sel=0)
        vf_cos = FXVerticalFrame(GroupBox_3, FRAME_SUNKEN|FRAME_THICK,
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
        AFXNote(p=GroupBox_3,
                message='cos(theta11) + cos(theta21) <= 1.0')

        # ============================================================
        # Dehomogenization
        # ============================================================

        VFrame_4 = FXVerticalFrame(p=self.swt_analysis,
                                   opts=LAYOUT_FILL_X,
                                   x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)

        VAligner_2 = AFXVerticalAligner(p=VFrame_4, opts=0,
                                        x=0, y=0, w=0, h=0,
                                        pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=VAligner_2, ncols=40,
                     labelText='New VABS recover file name: ',
                     tgt=form.vabs_rec_nameKw, sel=0,
                     opts=0)
        fileHandler = VabsDBFileHandler(
            form, 'vabs_inp_name2', 'VABS input files (*.dat)')
        fileTextHf = FXHorizontalFrame(
            p=VAligner_2, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0,
            hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=40, labelText='VABS input file: ',
                     tgt=form.vabs_inp_name2Kw, sel=0,
                     opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL)
        FXButton(p=fileTextHf, text='	Select File\nFrom Dialog',
                 ic=icon,
                 tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
                 opts=BUTTON_NORMAL|LAYOUT_CENTER_Y,
                 x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        
        # ------------------------------------------------------------
        # Model
        GroupBox_9 = FXGroupBox(p=VFrame_4,
                                text='Base on',
                                opts=FRAME_GROOVE|LAYOUT_FILL_X)
        FXRadioButton(p=GroupBox_9,
                      text='Classical model',
                      tgt=form.model_recoverKw, sel=1)
        FXRadioButton(p=GroupBox_9,
                      text='Generalized Timoshenko model',
                      tgt=form.model_recoverKw, sel=2)
        FXRadioButton(p=GroupBox_9,
                      text='Generalized Vlasov model',
                      tgt=form.model_recoverKw, sel=3)

        hf_data = FXHorizontalFrame(p=VFrame_4,
                                    opts=LAYOUT_FILL_X,
                                    x=0, y=0, w=0, h=0,
                                    pl=0, pr=0, pt=0, pb=0)
        vf_data1 = FXVerticalFrame(p=hf_data,
                                   opts=LAYOUT_FILL_X,
                                   x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)

        # ------------------------------------------------------------
        # Displacements
        gb_u = FXGroupBox(p=vf_data1,
                          text='Displacements',
                          opts=FRAME_GROOVE|LAYOUT_FILL_X)
        vf_u = FXVerticalFrame(
            gb_u, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_u = AFXTable(vf_u, 2, 3, 2, 3, form.uKw, 0,
                            AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_u.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_u.setLeadingRows(1)
        self.t_u.setLeadingRowLabels('u1\tu2\tu3')
        self.t_u.setColumnWidth(-1, w)
        self.t_u.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_u.showHorizontalGrid(True)
        self.t_u.showVerticalGrid(True)

        # ------------------------------------------------------------
        # Direction cosines
        gb_c = FXGroupBox(p=vf_data1,
                          text='Direction cosines',
                          opts=FRAME_GROOVE|LAYOUT_FILL_X)
        vf_c = FXVerticalFrame(
            gb_c, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_c = AFXTable(vf_c, 3, 3, 3, 3, form.cKw, 0,
                            AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_c.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_c.setColumnWidth(-1, w)
        self.t_c.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_c.showHorizontalGrid(True)
        self.t_c.showVerticalGrid(True)

        # ------------------------------------------------------------
        # Sectional forces/moments
        gb_sfm = FXGroupBox(p=vf_data1,
                            text='Sectional forces/moments',
                            opts=FRAME_GROOVE|LAYOUT_FILL_X)
        vf_sf = FXVerticalFrame(
            gb_sfm, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_sf = AFXTable(vf_sf, 2, 3, 2, 3, form.sfKw, 0,
                             AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_sf.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_sf.setLeadingRows(1)
        self.t_sf.setLeadingRowLabels('F1\tF2\tF3')
        self.t_sf.setColumnWidth(-1, w)
        self.t_sf.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_sf.showHorizontalGrid(True)
        self.t_sf.showVerticalGrid(True)

        vf_sm = FXVerticalFrame(
            gb_sfm, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_sm = AFXTable(vf_sm, 2, 3, 2, 3, form.smKw, 0,
                             AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_sm.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_sm.setLeadingRows(1)
        self.t_sm.setLeadingRowLabels('M1\tM2\tM3')
        self.t_sm.setColumnWidth(-1, w)
        self.t_sm.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_sm.showHorizontalGrid(True)
        self.t_sm.showVerticalGrid(True)

        vf_data2 = FXVerticalFrame(p=hf_data,
                                   opts=LAYOUT_FILL_X,
                                   x=0, y=0, w=0, h=0,
                                   pl=0, pr=0, pt=0, pb=0)

        # ------------------------------------------------------------
        # Distributed forces/moments
        gb_dfm = FXGroupBox(p=vf_data2,
                            text='Distributed forces/moments',
                            opts=FRAME_GROOVE|LAYOUT_FILL_X)
        vf_df = FXVerticalFrame(
            gb_dfm, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_df = AFXTable(vf_df, 5, 3, 5, 3, form.dfKw, 0,
                             AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_df.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_df.setLeadingRows(1)
        self.t_df.setLeadingRowLabels('f1\tf2\tf3')
        self.t_df.setColumnWidth(-1, w)
        self.t_df.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_df.showHorizontalGrid(True)
        self.t_df.showVerticalGrid(True)

        vf_dm = FXVerticalFrame(
            gb_dfm, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_dm = AFXTable(vf_dm, 5, 3, 5, 3, form.dmKw, 0,
                             AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_dm.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_dm.setLeadingRows(1)
        self.t_dm.setLeadingRowLabels('m1\tm2\tm3')
        self.t_dm.setColumnWidth(-1, w)
        self.t_dm.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_dm.showHorizontalGrid(True)
        self.t_dm.showVerticalGrid(True)

        # ------------------------------------------------------------
        # Strains/curvatures
        gb_gk = FXGroupBox(p=vf_data2,
                           text='Strains/twists/curvatures',
                           opts=FRAME_GROOVE|LAYOUT_FILL_X)
        vf_gamma = FXVerticalFrame(
            gb_gk, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_gamma = AFXTable(vf_gamma, 2, 1, 2, 1, form.gammaKw, 0,
                                AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_gamma.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_gamma.setLeadingRows(1)
        self.t_gamma.setLeadingRowLabels('gamma11')
        self.t_gamma.setColumnWidth(-1, w)
        self.t_gamma.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_gamma.showHorizontalGrid(True)
        self.t_gamma.showVerticalGrid(True)

        vf_kappa = FXVerticalFrame(
            gb_gk, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_kappa = AFXTable(vf_kappa, 2, 3, 2, 3, form.kappaKw, 0,
                                AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_kappa.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_kappa.setLeadingRows(1)
        self.t_kappa.setLeadingRowLabels('kappa1\tkappa2\tkappa3')
        self.t_kappa.setColumnWidth(-1, w)
        self.t_kappa.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_kappa.showHorizontalGrid(True)
        self.t_kappa.showVerticalGrid(True)

        vf_kappa_p = FXVerticalFrame(
            gb_gk, FRAME_SUNKEN|FRAME_THICK,
            0, 0, 0, 0, 0, 0, 0, 0)
        self.t_kappa_p = AFXTable(vf_kappa_p, 2, 3, 2, 3, form.kappa_pKw, 0,
                                  AFXTABLE_EDITABLE|LAYOUT_FILL_X)
        self.t_kappa_p.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
        self.t_kappa_p.setLeadingRows(1)
        self.t_kappa_p.setLeadingRowLabels('kappa1\'\tkappa1\'\'\tkappa1\'\'\'')
        self.t_kappa_p.setColumnWidth(-1, w)
        self.t_kappa_p.setColumnJustify(-1, AFXTable.RIGHT)
        self.t_kappa_p.showHorizontalGrid(True)
        self.t_kappa_p.showVerticalGrid(True)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):
        self.swt_analysis.setCurrent(0)
        self.cb_vlasov.disable()
        self.t_sf.setColumnEditable(1, False)
        self.t_sf.setColumnEditable(2, False)
        self.t_df.disable()
        self.t_dm.disable()
        self.t_gamma.disable()
        self.t_kappa.disable()
        self.t_kappa_p.disable()
        AFXDataDialog.show(self)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def processUpdates(self):
        a = self.form.recover_flagKw.getValue()
        self.swt_analysis.setCurrent(a-1)

        t = self.form.timoshenko_flagKw.getValue()
        k = self.form.curve_flagKw.getValue()
        o = self.form.oblique_flagKw.getValue()

        if k:
            self.t_k.enable()
        else:
            self.t_k.disable()
        
        if t:
            self.cb_vlasov.enable()
            self.cb_oblique.disable()
            self.t_cos.disable()
        else:
            self.cb_vlasov.disable()
            self.cb_oblique.enable()
            if o:
                self.t_cos.enable()
            else:
                self.t_cos.disable()

        m = self.form.model_recoverKw.getValue()
        if m == 1:
            self.t_sf.enable()
            self.t_sm.enable()
            self.t_sf.setColumnEditable(1, False)
            self.t_sf.setColumnEditable(2, False)
            self.t_df.disable()
            self.t_dm.disable()
            self.t_gamma.disable()
            self.t_kappa.disable()
            self.t_kappa_p.disable()
        elif m == 2:
            self.t_sf.enable()
            self.t_sm.enable()
            self.t_sf.setColumnEditable(1, True)
            self.t_sf.setColumnEditable(2, True)
            self.t_df.enable()
            self.t_dm.enable()
            self.t_gamma.disable()
            self.t_kappa.disable()
            self.t_kappa_p.disable()
        elif m == 3:
            self.t_sf.disable()
            self.t_sm.disable()
            self.t_sf.setColumnEditable(1, False)
            self.t_sf.setColumnEditable(2, False)
            self.t_df.disable()
            self.t_dm.disable()
            self.t_gamma.enable()
            self.t_kappa.enable()
            self.t_kappa_p.enable()

###########################################################################
# Class definition
###########################################################################

class VabsDBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, VabsDBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
