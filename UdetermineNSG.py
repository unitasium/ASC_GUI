# -*- coding: utf-8 -*-

from abaqusConstants import *
from textRepr import *
from part import *
from mesh import *
from abaqus import *

def determineNSG(model_name, part_name):
    
    model = mdb.models[model_name]
    part = model.parts[part_name]
    
    meshStats = part.getMeshStats()
    
    eflag_3D = 0
    eflag_2D = 0
    eflag_1D = 0
    
    if meshStats.numHexElems > 0 or meshStats.numTetBoundaryElems > 0 or meshStats.numTetElems > 0:
        eflag_3D = 1
#        print '3D nSG'
    elif meshStats.numWedgeElems > 0:
        raise ValueError('part[%s] contains wedge elements, which is not supported in SwiftComp.' % part_name )
    elif meshStats.numTriElems > 0 or meshStats.numQuadElems> 0:
        eflag_2D = 1
#        print '2D nSG'
    elif meshStats.numLineElems > 0:
        eflag_1D = 1
#        print '1D nSG'
    t = eflag_3D * eflag_2D * eflag_1D
    if t != 0:
        raise ValueError('part[%s] contains elements of the different dimensions, please delete the unwanted elements.' % part_name )
    elif t == 0:
        if eflag_3D == 1:
            nSG = 3
        elif eflag_2D == 1:
            nSG = 2
        elif eflag_1D == 1:
            nSG = 1
    
    return nSG
    