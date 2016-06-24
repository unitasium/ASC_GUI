from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os
import re

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)
thisDir = os.path.join(thisDir, 'Icon')


###########################################################################
# Class definition
###########################################################################

class WorkplaneV5DB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):
        
        self.form = form

        # Construct the base class.
        #

        AFXDataDialog.__init__(
            self, form, 'Set sketch plane',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            
        va = AFXVerticalAligner(self)

        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_1 = AFXComboBox(
            p=va, ncols=32, nvis=1, text='Model:',
            tgt=form.model_nameKw, sel=0)
        self.RootComboBox_1.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_1.appendItem(name)
        if not form.model_nameKw.getValue() in names:
            form.model_nameKw.setValue(names[0])
        
        AFXTextField(p=va, ncols=32, labelText='New Part Name: ',
                     tgt=form.part_nameKw, sel=0)
        
        # ----------------------------------------------------------------------
        GroupBox_3 = FXGroupBox(p=self, text='SG Dimension', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        
        HFrame_1 = FXHorizontalFrame(p=GroupBox_3, opts=0, x=0, y=0, w=0, h=0,
                                     pl=0, pr=0, pt=0, pb=0)
        FXRadioButton(p=HFrame_1, text='1D', tgt=form.nsgKw, sel=1)
        FXRadioButton(p=HFrame_1, text='2D', tgt=form.nsgKw, sel=2)
        
        self.swt_source = FXSwitcher(GroupBox_3, 0, 0,0,0,0, 0,0,0,0)
        
        # ......................................................................
        vf = FXVerticalFrame(p=self.swt_source, opts=0, x=0, y=0, w=0, h=0,
                             pl=0, pr=0, pt=0, pb=0) 
        AFXNote(vf, 'The next step to create the 1D customized SG part, use:')
        hf = FXHorizontalFrame(p=vf, opts=0, x=0, y=0, w=0, h=0,
                               pl=0, pr=0, pt=0, pb=0) 
        l = FXLabel(p=hf, text='1D SG', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) )
        fileName = os.path.join(thisDir, 'sg_1d_small.png')
        iconWire = afxCreatePNGIcon(fileName)
        FXLabel(p=hf, text='', ic=iconWire)
        
        # ......................................................................
        vf = FXVerticalFrame(p=self.swt_source, opts=0, x=0, y=0, w=0, h=0,
                             pl=0, pr=0, pt=0, pb=0) 
        AFXNote(vf, 'The next step to create the 2D customized SG part, use:')
        hf = FXHorizontalFrame(p=vf, opts=0, x=0, y=0, w=0, h=0,
                                     pl=0, pr=0, pt=0, pb=0)
        l = FXLabel(p=hf, text='Create Shell : Planar', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) )
        fileName = os.path.join(thisDir, 'icoR_partShellPlanar.png')
        iconShell = afxCreatePNGIcon(fileName)
        FXLabel(p=hf, text='', ic=iconShell)        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)
        
        self.swt_source.setCurrent(0)
        
        self.currentModelName = getCurrentContext()['modelName']
        self.form.model_nameKw.setValue(self.currentModelName)
        
        reg_exp = r'Part-\d{1,}'
        pi = 0
        pns = mdb.models[self.currentModelName].parts.keys()
        for pn in pns:
            match_obj = re.match(reg_exp, pn)
            if match_obj:
                i = int(pn.split('-')[-1])
                if i > pi:
                    pi = i
        pn_new = 'Part-' + str(pi+1)
        self.form.part_nameKw.setValue(pn_new)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def processUpdates(self):
        
        if self.form.nsgKw.getValue() == 1:
            self.swt_source.setCurrent(0)
        elif self.form.nsgKw.getValue() == 2:
            self.swt_source.setCurrent(1)
