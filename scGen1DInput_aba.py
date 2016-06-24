# -*- coding: utf-8 -*-

from abaqusConstants import *
from textRepr import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import os    
import time
from utilities import *
from UwriteMaterials import *
from userDataSG import *

def generate_1DInputFromCAE(model_source, macro_model_dimension, analysis, elem_flag, trans_flag,
                            w, nSG, model_name, part_name, abaqus_input, new_filename, 
                            specific_model, bk, 
                            sk, cos, 
                            temp_flag, nlayer=0):

    # start to write
    startTime = time.clock()
    inst_name = part_name + '-1'
    
    model       = mdb.models[model_name]
    part        = model.parts[part_name]
    nodes       = part.nodes    
    element     = part.elements
    nnode       = len(nodes)
    edge        = part.edges
    nelem       = len(edge)
    nnode       = len(nodes)        
    ntemp       = 1
    temperature = 0.0
    
    if nSG == 1:
        nMaxnode_elem = 5
        nodeinfoFormat='{0[0]:8d}{0[1]:16.6E}'
        eleminfoFormat='{0[0]:8s}{0[1]:8s}{0[2]:8d}{0[3]:8d}{0[4]:8d}{0[5]:8d}{0[6]:8d}'
    
    #---------------------------------------------------------------------
    layup_name = part.compositeLayups.keys()
    n_layup_abq = 0
    for i in range(len(layup_name)):
        if part.compositeLayups[layup_name[i]].suppressed == False:
            n_layup_abq = n_layup_abq + 1
            layup_name_inuse = layup_name[i]
            
    if n_layup_abq == 0:
        raise ValueError('part[%s].compositeLayups contains none composite layup, please first define 1 composite layup.' % part_name )
    elif n_layup_abq >= 2:
        raise ValueError('part[%s].compositeLayups contains more than 1 composite layup, please delete exta composite layup.' % part_name )
        
    layup_abq = part.compositeLayups[layup_name_inuse]
    if layup_abq.offsetType == MIDDLE_SURFACE:
        offsetRatio = 0.0
    elif layup_abq.offsetType == BOTTOM_SURFACE:
        offsetRatio = -0.5
    elif layup_abq.offsetType == TOP_SURFACE:
        offsetRatio = 0.5
    elif layup_abq.offsetType == SINGLE_VALUE:
        offsetRatio = layup_abq.offsetValues[0]
    
    plies_sc = {}
    ply_id_sc = 0
    
    layup_abq = part.compositeLayups[layup_name_inuse]
    for i in range(len(layup_abq.plies)):
        if layup_abq.plies[i].suppressed == False:    # construct plies_sc  {'ply_id_sc':}
            plies_sc[ply_id_sc] = layup_abq.plies[i]  #  the key of plies_sc[ply_id_sc] begin at 0 .
            ply_id_sc = ply_id_sc + 1
    
    n_ply = len(plies_sc)
    
    t_total = 0
    layup_t = []
    
    for ply_id in range(n_ply):
        ply_t = plies_sc[ply_id].thickness
        t_total = t_total+ply_t
        layup_t.append(ply_t)
    
    c = 0
    layup_position = []
    offset = -t_total * (offsetRatio)
    
    matDict = {}
    plies   = {}
    nlayers = {}
    
    for ply_id in range(n_ply):
        mat_name = plies_sc[ply_id].material
        if plies_sc[ply_id].orientationType == SPECIFY_ORIENT:
            theta_i = plies_sc[ply_id].orientationValue
        else:
            theta_i = plies_sc[ply_id].orientationType
            theta_i = float(str(theta_i).rsplit('_')[-1])
        
        if mat_name not in matDict.keys():
            matDict[mat_name] = len(matDict) + 1
        if [mat_name, theta_i] not in nlayers.values():
            nlayer_id = len(nlayers) + 1
            nlayers[nlayer_id] = [mat_name, theta_i]
        
        for nlayer_id, nlayer_values in nlayers.iteritems():
            if nlayer_values == [mat_name, theta_i]:
                plies[ply_id] = nlayer_id
    for nlayer_id, nlayer_values in nlayers.iteritems():
        nlayers[nlayer_id] = [matDict[nlayer_values[0]], nlayer_values[1]]
    
    # check the validity of materials: matDict
    checkMaterials(matDict, analysis, model_name)
    
    #
    edge   = part.edges
    nelem  = len(edge)
    nnode  = len(nodes)
    nmate  = len(matDict)
    nslave = 0
    nlayer = len(nlayers)
    
    nnodes_scelem = len(list(edge[i].getNodes()))
    #### start to write
    if new_filename == '':
        swiftcomp_filename = part_name + '_nSG' + str(nSG) + '_' + macro_model_dimension + '_n' + str(nnodes_scelem)
    else:
        swiftcomp_filename = new_filename
    
    mdb.customData.Repository('sgs', Sg)
    sg_name = swiftcomp_filename
    sg = mdb.customData.Sg(name = sg_name)
    sg.createSg(model_source, model_name, part_name, abaqus_input, swiftcomp_filename,
                macro_model_dimension, w, analysis, elem_flag, trans_flag, temp_flag,
                specific_model, 
                bk, cos,
                sk)
    if info == 1:
        print '---> Create sg model: %s' % sg_name
        print '    mdb.customData.sgs[\'%s\']' % sg_name
        prettyPrint(sg,2)
        print '------------------------------'
    
    file = open(swiftcomp_filename + '.sc','w')    
    if macro_model_dimension != '3D':
        writeFormat(file, 'd', [specific_model])
        file.write('\n')
    
    if macro_model_dimension == '2D':
        writeFormat(file, 'EE', sk)
        file.write('\n')
    elif macro_model_dimension == '1D':
        raise ValueError('1D SG cannot be used for beam model!')
     
    file.write('{0:>10d}{1:>10d}{2:>10d}{3:>10d}'.format(analysis,elem_flag,trans_flag,temp_flag))
    file.write('\n')
    
    #Material control parameters
    file.write('{0:>10d}{1:>10d}{2:>10d}{3:>10d}{4:>10d}{5:>10d}'.format(nSG,nnode,nelem,nmate,nslave,nlayer))
    file.write('   # nSG nnode nelem nmate nslave nlayer')
    file.write('\n')
    file.write('\n')
    # write node info
    #
    for i in range(0,nnode):
        file.write('{0:>10s}'.format(str(nodes[i].label)))
        ndCoords = nodes[i].coordinates
        file.write('{0:>20f}\n'.format(float(ndCoords[2])+offset))        #z-y3, only for plate/shell
    file.write('\n')
    
    # edge should follow the consecutive sequence from 1 ... ###
    for i in range(len(edge)):
        connect_temp = list(edge[i].getNodes())
        abaEle_edge = len(connect_temp) - 1
        connect = [connect_temp[n].label for n in range(abaEle_edge + 1) ]
        if abaEle_edge == 4:
            t4 = connect[4]
            t3 = connect[3]
            connect[3] = t4
            connect[4] = t3
        else:
            n = len(connect)
            zeros = [0] * (nMaxnode_elem - n)
            connect += zeros
        elem_info = [str(i+1),str(plies[i])] + connect
        file.write(eleminfoFormat.format(elem_info)) #edge[i].index + 1, plies[i]=nlayer_id
        file.write('\n')
    
    file.write('\n')
    file.write('\n')
    
    # write layer info 
    for nlayer_id, nlayer_values in nlayers.iteritems():
        file.write('{0:>10d}{1:>10d}{2:>10s}'.format(nlayer_id, nlayer_values[0],str(nlayer_values[1]) ))
        file.write('\n')
    
    file.write('\n')
    
    writeMaterials(matDict, analysis, model_name, file)
    
    file.write('\n')
    file.write('\n')
    file.write('{0:16.6E}'.format(w))
    file.write('\n')
    file.close()
#    try:
#        scTimestart=time.clock()
#        
#        os.system('Swiftcomp '+ swiftcomp_filename+'.sc ' + macro_model_dimension + ' H')
#        scTimeEnd=time.clock()
#        scTime=scTimeEnd-scTimestart
#        #print 'Time for homogenization %s:' %str(scTime)
# 
#        PadTimeStart=time.clock()
#        os.system('Notepad '+swiftcomp_filename+'.sc.k')
#        PadTimeEnd=time.clock()
#        PadTime=PadTimeEnd-PadTimeStart
#        #print 'Time for open notePad %s:' %str(PadTime)
#    except WindowsError:
#        raise TypeError( 'Unexpected error happened. Please check if the "structure genome dimension" is correct.')
#        return
#    
#    print 'nnode:  %s' %str(nnode)
#    print 'nelem:  %s' %str(nelem)
#    print 'writeNodeTime:  %s' %str(writeNodetime)
#    print 'writeElemTime:  %s' %str(writeElemtime)
#    print 'calculateWtime:  %s' % str(WTime)
#    print 'writeSCTime:  %s' %str(timeWritefile)
#    print 'scTime: %s' %str(scTime)
#    print 'openPadTime: %s' %str(PadTime)    
    swiftcomp_filename += '.sc'
    
    return [swiftcomp_filename, macro_model_dimension]