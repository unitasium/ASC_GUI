# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
from utilities import *
import os
from userDataSG import *


def sgmodel_info(sgmodel_source, sg_name, sc_input,  analysis, macro_model, ap_flag):

    if sgmodel_source == 1:  # sgmodel_source==1: sg_name;   sgmodel_source==2: sc_input file path and name
            
        SCfileName  = sg_name
        scinput     = mdb.customData.sgs[sg_name].swiftcomp_filename
        currentpath = os.getcwd()
        sc_input    = currentpath+'\\'+scinput
        
        if debug == 1:
            print '\n'
            print ('--->sc_input corresponding to the sg model is  %s' % sc_input)
            print '\n'
            
    elif sgmodel_source == 2:
        sc_input    = sc_input.replace('/','\\')
        scpath      = os.path.dirname(sc_input)
        currentpath = os.getcwd()
        if debug == 1:
            print '\n'
            print 'when sgmodel_source == 2: ' 
            print 'sc_input %s chosen in dialog box: ' % scpath
            print 'scpath = os.path.dirname(sc_input) : %s' % scpath
            print 'currentpath = os.getcwd() : %s' % currentpath
            print '\n'
        temp_name  = sc_input.rsplit('\\',1)
        temp_name  = temp_name[-1]
        temp_name  = temp_name.split('.')
        SCfileName = temp_name[0]
        if scpath != currentpath:
            raise ValueError('File %s.sc is at %s, \n the work directory is %s. \n File %s.sc and the homogenization output files should be in the work directory.' %(SCfileName, scpath, currentpath, SCfileName))
            return
        
        if debug == 1:
            print '\n'
            print '---> sc_input selected is %s ' % sc_input
            print '\n'
        
    if sgmodel_source == 1:
        sg                    = mdb.customData.sgs[sg_name]
        analysis              = sg.analysis
        macro_model_dimension = sg.macro_model_dimension
        macro_model           = int(macro_model_dimension.strip('D'))
        if hasattr(sg, 'apstr'):
            apstr             = sg.apstr
            if apstr == 'pbc':
            	ap_flag           = False
            else:
            	ap_flag           = True
    elif sgmodel_source == 2:
        macro_model_dimension = str(macro_model) + 'D'
        
    
    
    return SCfileName, sc_input, analysis, macro_model, macro_model_dimension, ap_flag
    