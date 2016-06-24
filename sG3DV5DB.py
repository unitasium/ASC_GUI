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

class SG3DV5DB(AFXDataDialog):



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, '3D Structure Genome',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            
        self.form = form
        
        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            

        applyBtn = self.getActionButton(self.ID_CLICKED_APPLY)
        applyBtn.setText('Apply')
        
        # upper   
        GroupBox_1 = FXGroupBox(p=self, text='Select a profile', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        
        HFrame_2 = FXHorizontalFrame(p=GroupBox_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        FXRadioButton(p=HFrame_2, text='Spherical Inclusion', tgt=form.profileKw, sel=1)
        #FXRadioButton(p=HFrame_2, text='Cubic inclusion', tgt=form.profileKw, sel=2)
        
        # lower
       
        #
        HFrame_1 = FXHorizontalFrame(p=self, opts=LAYOUT_FILL_X, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
            
        # Left Panel
        VFrame_2 = FXVerticalFrame(p=HFrame_1, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        #----Geometry--------------    
        GroupBox_2 = FXGroupBox(p=VFrame_2, text='Geometry', opts=FRAME_GROOVE)
        HFrame_6 = FXHorizontalFrame(p=GroupBox_2, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
            
        GroupBox_5 = FXGroupBox(p=HFrame_6, text='Inclusion', opts=FRAME_GROOVE)
        VFrame_5 = FXVerticalFrame(p=GroupBox_5, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
            
            
        FXRadioButton(p=VFrame_5, text='Volume fraction (vf_f)', tgt=form.fiber_flagKw, sel=1)
        FXRadioButton(p=VFrame_5, text='Radius (r)', tgt=form.fiber_flagKw, sel=2)
        AFXTextField(p=VFrame_5, ncols=12, labelText='', tgt=form.vf_fKw, sel=0)
        
        #----interface--------------
        GroupBox_6 = FXGroupBox(p=HFrame_6, text='Interphase', opts=FRAME_GROOVE)
        VFrame_6 = FXVerticalFrame(p=GroupBox_6, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
        FXRadioButton(p=VFrame_6, text='Volume fraction (vf_i)', tgt=form.interface_flagKw, sel=1)
        FXRadioButton(p=VFrame_6, text='Thickness (t)', tgt=form.interface_flagKw, sel=2)
        
        AFXTextField(p=VFrame_6, ncols=12, labelText='', tgt=form.t_interfaceKw, sel=0)
        
        #self.swt_vf = FXSwitcher(GroupBox_2, 0, 0,0,0,0, 0,0,0,0)
#        l1=FXLabel(p=GroupBox_2, text='Note: 0 < vf_f+vf_i <= 0.52', opts=JUSTIFY_LEFT)
        AFXNote(p=GroupBox_2, message='0 < vf_f+vf_i <= 0.52')
        #l2=FXLabel(p=self.swt_vf, text='Note: 0 < vf_f+vf_i <  1.0' , opts=JUSTIFY_LEFT)
        
#        l1.setFont( getAFXFont(FONT_BOLD) )
        #l2.setFont( getAFXFont(FONT_BOLD) )
        
        #----Material--------------
        GroupBox_3 = FXGroupBox(p=VFrame_2, text='Material', opts=FRAME_GROOVE|LAYOUT_FILL_X)
#        VFrame_4 = FXVerticalFrame(p=GroupBox_3, opts=0, x=0, y=0, w=0, h=0,
#            pl=0, pr=0, pt=0, pb=0)
        VAligner_3 = AFXVerticalAligner(p=GroupBox_3, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
#        frame = AFXVerticalAligner(VAligner_3, 0, 0,0,0,0, 0,0,0,0)

        # Model combo
        # Since all forms will be canceled if the  model changes,
        # we do not need to register a query on the model.
        #
        self.RootComboBox_8 = AFXComboBox(p=VAligner_3, ncols=0, nvis=1, text='Model: ', tgt=form.modelNameKw, sel=0)
        self.RootComboBox_8.setMaxVisible(10)

        names = mdb.models.keys()
        names.sort()
        for name in names:
            self.RootComboBox_8.appendItem(name)
        if not form.modelNameKw.getValue() in names:
            form.modelNameKw.setValue( names[0] )
        msgCount = 151
        form.modelNameKw.setTarget(self)
        form.modelNameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler8 = str(self.__class__).split('.')[-1] + '.onComboBox_8MaterialsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler8) )

        msgHandler6 = str(self.__class__).split('.')[-1] + '.onComboBox_6MaterialsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount+1, msgHandler6) )

        msgHandler5 = str(self.__class__).split('.')[-1] + '.onComboBox_5MaterialsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount+2, msgHandler5) )

        # Materials combo
        #
        self.ComboBox_8 = AFXComboBox(p=VAligner_3, ncols=0, nvis=1, text='Inclusion: ', tgt=form.fiber_matnameKw, sel=0)
        self.ComboBox_8.setMaxVisible(10)

        #self.form = form     #VAligner_3
        self.ComboBox_6 = AFXComboBox(p=VAligner_3, ncols=0, nvis=1, text='Matrix: ', tgt=form.matrix_matnameKw, sel=0)
        self.ComboBox_6.setMaxVisible(10)

        #self.form = form     #VAligner_3
        self.ComboBox_5 = AFXComboBox(p=VAligner_3, ncols=0, nvis=1, text='Interface: ', tgt=form.interface_matnameKw, sel=0)
        self.ComboBox_5.setMaxVisible(10)        
        
        #----Mesh--------------
        GroupBox_4 = FXGroupBox(p=VFrame_2, text='Mesh', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        va = AFXVerticalAligner(p=GroupBox_4, opts=0, x=0, y=0, w=0, h=0,
                                pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=va, ncols=10, labelText='Approximate global mesh size: ', tgt=form.mesh_sizeKw, sel=0)
        ComboBox_7 = AFXComboBox(p=va, ncols=0, nvis=1, text='Element type: ', tgt=form.elem_typeKw, sel=0)
        ComboBox_7.setMaxVisible(10)
        ComboBox_7.appendItem(text='Linear')
        ComboBox_7.appendItem(text='Quadratic')
            
        # Right Panel    
        VFrame_1 = FXVerticalFrame(p=HFrame_1, opts=LAYOUT_CENTER_Y, 
                                   x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        #self.swt_fig = FXSwitcher(VFrame_1, 0, 0,0,0,0, 0,0,0,0)
            
        fileName = os.path.join(thisDir, 'Spherical.png')
        self.icon_sqr = afxCreatePNGIcon(fileName)
        FXLabel(p=VFrame_1, text='', ic=self.icon_sqr)
        #FXLabel(p=self.swt_fig, text='', ic=self.icon_sqr)
        
        
#        fileName = os.path.join(thisDir, 'Cubic.png')
#        self.icon_hex = afxCreatePNGIcon(fileName)
#        FXLabel(p=self.swt_fig, text='', ic=self.icon_hex)
        
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)

        # Register a query on materials
        #
        self.currentModelName = getCurrentContext()['modelName']
        self.form.modelNameKw.setValue(self.currentModelName)
        mdb.models[self.currentModelName].materials.registerQuery(self.updateComboBox_8Materials)
        mdb.models[self.currentModelName].materials.registerQuery(self.updateComboBox_6Materials)
        mdb.models[self.currentModelName].materials.registerQuery(self.updateComboBox_5Materials)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        mdb.models[self.currentModelName].materials.unregisterQuery(self.updateComboBox_8Materials)
        mdb.models[self.currentModelName].materials.unregisterQuery(self.updateComboBox_6Materials)
        mdb.models[self.currentModelName].materials.unregisterQuery(self.updateComboBox_5Materials)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def onComboBox_8MaterialsChanged(self, sender, sel, ptr):

        self.updateComboBox_8Materials()
        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_6MaterialsChanged(self, sender, sel, ptr):

        self.updateComboBox_6Materials()
        return 1
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onComboBox_5MaterialsChanged(self, sender, sel, ptr):

        self.updateComboBox_5Materials()
        return 1        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_8Materials(self):

        modelName = self.form.modelNameKw.getValue()

        # Update the names in the Materials combo
        #
        self.ComboBox_8.clearItems()
        names = mdb.models[modelName].materials.keys()
        names.sort()
        for name in names:
            self.ComboBox_8.appendItem(name)
        if names:
            if not self.form.fiber_matnameKw.getValue() in names:
                self.form.fiber_matnameKw.setValue( names[0] )
        else:
            self.form.fiber_matnameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_6Materials(self):

        modelName = self.form.modelNameKw.getValue()

        # Update the names in the Materials combo
        #
        self.ComboBox_6.clearItems()
        names = mdb.models[modelName].materials.keys()
        names.sort()
        for name in names:
            self.ComboBox_6.appendItem(name)
        if names:
            if not self.form.matrix_matnameKw.getValue() in names:
                self.form.matrix_matnameKw.setValue( names[0] )
        else:
            self.form.matrix_matnameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_5Materials(self):

        modelName = self.form.modelNameKw.getValue()


        # Update the names in the Materials combo
        #
        
        self.ComboBox_5.clearItems()
        names = mdb.models[modelName].materials.keys()
        names.sort()
        for name in names:
            self.ComboBox_5.appendItem(name)
        if names:
            if not self.form.interface_matnameKw.getValue() in names:
                self.form.interface_matnameKw.setValue( names[0] )
        else:
            self.form.interface_matnameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #def processUpdates(self):
    #    
    #    if self.form.profileKw.getValue() == 1:
    #        self.swt_fig.setCurrent(0)
    #        self.swt_vf.setCurrent(0)
    #    elif self.form.profileKw.getValue() == 2:
    #        self.swt_fig.setCurrent(1)
    #        self.swt_vf.setCurrent(1)