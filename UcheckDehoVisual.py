# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 17:31:30 2016

@author: peng69
"""


import os
import sys

def checkDehoVisual(sc_input_sc, flag):
    # Check if there is a odb file with the destination name have already exist:
    #print 'sc_input_sc%s'%sc_input_sc
    SCfileName=sc_input_sc.split('.')
    SCfileName=SCfileName[0]
    if flag[0]=='D' or flag[0]=='d' or  flag[0]=='V' or flag[0]=='v':
        cwd = os.getcwd()
        destOdbname=cwd + '\\' + SCfileName + '.odb'
        if os.path.exists(destOdbname):
            print 'The odb file %s has existed! The original %s.odb will be overwritten.' % (destOdbname,destOdbname) 
            
    # Check the availability of the homogenization result files
    print '\n'
    print '---->Check the availability of the required homogenization result files.'
    
    cwd = os.getcwd()
    
    isfilesc=os.path.exists(cwd + '\\' + sc_input_sc)
    
    isfilek=os.path.exists(cwd + '\\' + sc_input_sc + '.k')
    isfileopt=os.path.exists(cwd + '\\' + sc_input_sc + '.opt')
    
    if flag[0]=='M' or flag[0]=='m':
        if isfilek==True :
            print 'Pass.'
            print '\n'
        else:
            raise ValueError( '%s.k should be available in the current work directory.' %(sc_input_sc))
            return
            
    elif flag[0]=='D' or flag[0]=='d':
        if isfilek==True and isfilesc==True and isfileopt==True:
            print 'Pass.'
            print '\n'
        else:
            raise ValueError( '%s, %s.k, %s.opt should be available in the current work directory.' %(sc_input_sc,sc_input_sc,sc_input_sc))
            return
    elif flag[0]=='V' or flag[0]=='v':
        if isfilesc==True:
            print 'Pass.'
            print '\n'
        else:
            raise ValueError( '%s should be available in the current work directory.' %(sc_input_sc))
            return
        
        
        