# -*- coding: utf-8 -*-

from abaqusConstants import * 
from abaqus import *
from customKernel import CommandRegister, RegisteredList , RegisteredTuple#, RepositorySupport
from UdetermineNSG import determineNSG
import textRepr as tr
import os

class Sg(CommandRegister):
    
    def __init__(self, name):
        
        CommandRegister.__init__(self)
        
    def createSg(self, model_source,model_name, part_name,abaqus_input, swiftcomp_filename,
                 macro_model_dimension, w, analysis, elem_flag, trans_flag, temp_flag,
                 specific_model, 
                 bk, cos,
                 sk,
                 apstr='pbc'):
        
        if model_source == 1:
            
            self.modelfromSource = 'fromCAE'
            self.part_name       = part_name
            self.model_name      = model_name
            self.nSG             = determineNSG(model_name,part_name)
            
        elif model_source == 2:
            self.modelfromSource = 'fromInputfile'
            self.abaqus_input    = abaqus_input
        
        self.swiftcomp_filename    = swiftcomp_filename+'.sc'
        self.macro_model_dimension = macro_model_dimension
        self.volume                = w
        self.analysis              = analysis
        self.elem_flag             = elem_flag
        self.trans_flag            = trans_flag
        self.temp_flag             = temp_flag
        self.apstr                 = apstr
        
        if macro_model_dimension == '1D':
            self.specific_model     = specific_model
            self.bk                 = bk
            self.initialObliqueness = cos
            
        elif macro_model_dimension == '2D':
            self.specific_model = specific_model
            self.sk             = sk
        
        return

            
class SgDehomoData(CommandRegister):
    
    def __init__(self, name):
        
        CommandRegister.__init__(self)
        
    def createSgDehomoData(self, debug, sgmodel_source, sg_name, sc_input, 
                           analysis, macro_model, macro_displacement, 
                           macro_roatation, beam_strain, shell_strain, 
                           solid_strain, tm=0.0):
        
        if sgmodel_source == 1:
            self.sgmodel_source = 'fromSGmodel'
            self.sg_name        = sg_name
            try: 
                sg                         = mdb.customData.sgs[sg_name]
                self.macro_model_dimension = sg.macro_model_dimension
                self.analysis              = sg.analysis
            except:
                raise ValueError('Check and update the data in sg[\' %s \']' % sg_name)
                
        elif sgmodel_source == 2:
            self.sgmodel_source = 'fromSwiftCompInputFile'
            path                = os.path.dirname(sc_input)
            
            if debug == 1:
                print ('in userDataSG, initailly: sc_input= %s' % sc_input)
                print ('in userDataSG, path= %s' % path)
            temp_name   = sc_input.rsplit('\\',1)
            temp_name   = temp_name[-1]
            temp_name   = temp_name.split('.')
            sc_filename = temp_name[0]
            if debug == 1:
                print ('in userDataSG, sgdehomo, self.sc_filename= %s' % sc_filename)
            self.sc_filepath = path
            self.sc_filename = sc_filename
            
            self.macro_model_dimension = str(macro_model) + 'D'
            self.analysis              = analysis
            
        self.macro_displacement = macro_displacement #RegisteredTuple(macro_displacement)
        self.macro_roatation    = macro_roatation #RegisteredTuple(macro_roatation)
        macro_model_dimension   = self.macro_model_dimension
        if macro_model_dimension == '1D':
            self.macro_strain = beam_strain #RegisteredTuple(beam_strain)
        elif macro_model_dimension == '2D':
            self.macro_strain = shell_strain #RegisteredTuple(shell_strain)
        elif macro_model_dimension == '3D':
            self.macro_strain = solid_strain #RegisteredTuple(solid_strain)
        
        if self.analysis == 1:
            self.temperature_increment = tm
            
        return
    
mdb.customData.Repository('sgs', Sg)
mdb.customData.Repository('sgDehomoDataSets', SgDehomoData)            
        