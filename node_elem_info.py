# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 19:49:33 2016

@author: peng69
"""

def node_info(nSG,line,unit_change_ratio=1.0,Xs=(0.0,0.0,0.0)):

    #nSG=1
    #line=['99', '           0.', '  0.345904797', ' -0.0876004323']
    #unit_change_ratio=2.0
    #Xs=(1.0,0.0,0.0)
    
    nid=int(line[0].strip())
    if nSG==1:
        x3=float(line[3].strip())
        if unit_change_ratio !=1.0:
            x3=    x3*unit_change_ratio
        if Xs !=(0.0,0.0,0.0):
            x3=    x3-    Xs[2]    
        node_info=[nid, x3]
    elif nSG==2:
        x2=float(line[2].strip())
        x3=float(line[3].strip())
        if unit_change_ratio !=1.0:
            x2=    x2*unit_change_ratio
            x3=    x3*unit_change_ratio
        if Xs !=(0.0,0.0,0.0):
            x2=    x2-    Xs[1]
            x3=    x3-    Xs[2]
        node_info=[nid, x2,x3]
    elif nSG==3:
        x1=float(line[1].strip())
        x2=float(line[2].strip())
        x3=float(line[3].strip())
        if unit_change_ratio !=1.0:
            x1=    x1*unit_change_ratio
            x2=    x2*unit_change_ratio
            x3=    x3*unit_change_ratio
        if Xs !=(0.0,0.0,0.0):
            x1=    x1-    Xs[0]
            x2=    x2-    Xs[1]
            x3=    x3-    Xs[2]
        node_info=[nid, x1,x2,x3]

    return node_info

#--------------------------------------------------

def elem_info(nSG,line):

#nSG=2
#line=['42', ' 102', ' 104', '  91', '  90','93','94']

    if nSG==1:
        print 'when nSG=1, other methods to generate the .sc file should be used, please contact the GUI developer.'
    elif nSG==2:
        nMaxnode_elem=9
        nSpecialElem=6
        zeroPosition=3
    elif nSG==3:
        nMaxnode_elem=20
        nSpecialElem=10
        zeroPosition=4
    
    
    eid=line[0].strip()
    ei_connt = [int(v.strip()) for v in line[1:]]    # {'element_id': [n_1, n_2, ...], ...}    
     nsc_connect=len(ei_connt) 

    
    if len(ei_connt)==nSpecialElem:
        ei_connt.insert(zeroPosition, 0)
        nsc_connect=len(ei_connt)
    
    zeros= [0] * (nMaxnode_elem - nsc_connect)
    ei_connt+= zeros
    ei_info=[eid,ei_connt]
    
    return ei_connt
 