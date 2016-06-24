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
from utilities import *
from UwriteMaterials import *
from userDataSG import *

def generateInputFromCAE(model_source, macro_model_dimension, analysis, elem_flag, trans_flag,
                         w, nSG, model_name, part_name, abaqus_input, new_filename, 
                         specific_model, bk, 
                         sk, cos, 
                         temp_flag, apvector, nlayer=0):

    startTime = time.clock()

    model    = mdb.models[model_name]
    part     = model.parts[part_name]
    nodes    = part.nodes    
    elements = part.elements
    
    if nSG == 2:
        nMaxnode_elem  = 9
        nodeinfoFormat = strFormat('dFF') #'{0[0]:8d}{0[1]:16.6E}{0[2]:16.6E}}\n'
        eleminfoFormat = eleFormat('dd','d'*9)
    elif nSG == 3:
        nMaxnode_elem  = 20
        nodeinfoFormat = strFormat('dFFF') #'{0[0]:8d}{1[0]:16.6E}{1[1]:16.6E}{2[2]:16.6E}\n'
        eleminfoFormat = eleFormat('dd','d'*20)

    #### start to write
    
    if new_filename == '':
        swiftcomp_filename = part_name + '_nSG' + str(nSG) + '_' + macro_model_dimension + '_' + str(elements[0].type)
    else:
        swiftcomp_filename = new_filename
    
    print apvector
    
    if apvector == [0,0,0]:
        apstr = 'pbc'
    else:
        apstr = ''.join(map(str, apvector))
        apstr = 'MIX'+apstr
    swiftcomp_filename = swiftcomp_filename+apstr
    
    mdb.customData.Repository('sgs', Sg)
    sg_name = swiftcomp_filename
    
    sg = mdb.customData.Sg(name = sg_name)
    sg.createSg(model_source, model_name, part_name, abaqus_input, swiftcomp_filename,
                macro_model_dimension, w, analysis, elem_flag, trans_flag, temp_flag,
                specific_model, 
                bk, cos,
                sk, 
                apstr)
    if info == 1:
        print '--> Create sg model: %s' % sg_name
        print '    mdb.customData.sgs[\'%s\']' %sg_name
        prettyPrint(sg, 2)
        print '------------------------------'
    
    print swiftcomp_filename + '.sc'
    file = open(swiftcomp_filename + '.sc', 'w')
    
    if macro_model_dimension != '3D':
        writeFormat(file, 'd', [specific_model])
        file.write('\n')
    
    if macro_model_dimension == '2D':
        writeFormat(file, 'EE', sk)
        file.write('\n')
    elif macro_model_dimension == '1D':
        writeFormat(file, 'EEE', bk)
        file.write('\n')
        writeFormat(file, 'EE', cos)
        file.write('\n')  
        
    writeFormat(file, 'd'*4, [analysis,elem_flag,trans_flag,temp_flag])
    file.write('\n')
    
    if apvector != [0,0,0]:
        writeFormat(file, 'ddd', [apvector[0], apvector[1], apvector[2]])
        file.write('\n')
    
    nnode = len(nodes)
    nelem = len(elements)
    
    #read number of exploited materials
    matSections = part.sectionAssignments
    
    matDict = {}
    for sec in matSections:
        if sec.suppressed == False:
            #regionName = sec.region[0]
            secName = sec.sectionName
            matName = model.sections[secName].material
            
            if matName not in matDict:
                matDict[matName] = len(matDict) + 1
    
    # check the validity of materials: matDict
    checkMaterials(matDict, analysis, model_name)
                
    nmate  = len(matDict)
    nslave = 0
    nlayer = 0
    
    #Material control parameters
    ntemp = 1
    temperature = 0
    
    writeFormat(file, 'd'*6, [nSG,nnode,nelem,nmate,nslave,nlayer])
    file.write('\n')
        
    # write node info
    #==============================================================================
    nodeStartTime = time.clock()

    if nSG == 3:
         for i in range(0, nnode):
             ndCoords = nodes[i].coordinates
             file.write(nodeinfoFormat.format([nodes[i].label, ndCoords[0], ndCoords[1], ndCoords[2]]))
    elif nSG == 2:    
         for i in range(0, nnode):
             ndCoords = nodes[i].coordinates    
             file.write(nodeinfoFormat.format([nodes[i].label,ndCoords[1], ndCoords[2]]))
             
    nodeEndTime   = time.clock()
    writeNodetime = nodeEndTime - nodeStartTime
    
    file.write('\n')    
    #==============================================================================
    
    elemStartTime = time.clock()

    #record element info
    labellist   = []
    matIDlist   = []
    connectlist = []
    
    matSections = part.sectionAssignments
    for sec in matSections:
        if not sec.suppressed:
            regionName = sec.region[0]
            secName = sec.sectionName
        
        matID = matDict[model.sections[secName].material]
        
        setElem = part.sets[regionName].elements
        
        for elem in setElem:
            connect = elem.connectivity
            n_connect = len(connect)
            labellist.append(elem.label)
            matIDlist.append(matID)
            ele_connectlist = []
            
            if nSG == 3:
                nsc_connect = n_connect
                for n in range(n_connect): 
                    ele_connectlist.append(nodes[connect[n]].label)
                    
                if  n_connect == 10:  #if element type is C3D10M, insert a '0' before the 5th node in the element
                    ele_connectlist.insert(4, 0)
                    nsc_connect = 11
                zeros = [0]*(nMaxnode_elem - nsc_connect)
                ele_connectlist += zeros

                connectlist.append(ele_connectlist)
                    
            elif nSG == 2:
                nsc_connect = n_connect
                for n in range(n_connect): 
                    ele_connectlist.append(nodes[connect[n]].label)
                    
                if  n_connect == 6:  #if element type is STRI65 or CPS6M etc. with 6 nodes, insert a '0' before the 4th node in the element
                    ele_connectlist.insert(3, 0)
                    nsc_connect = 7
                zeros = [0]*(nMaxnode_elem - nsc_connect)
                ele_connectlist += zeros

                connectlist.append(ele_connectlist)
                
    # sort and write element info
    combinedList = zip(labellist, matIDlist, connectlist)
    combinedList.sort()
    for elem_info in combinedList:
        file.write(eleminfoFormat.format(elem_info))
    
    elemEndTime   = time.clock()
    writeElemtime = elemEndTime - elemStartTime

    file.write('\n')
    
    writeMaterials(matDict, analysis, model_name, file)
    
    file.write('{0:16.6E}'.format(w))
    file.write('\n')
    file.write('\n')        
    
    file.close()
    endTime       = time.clock()
    timeWritefile = endTime - startTime
    
    swiftcomp_filename += '.sc'
    
    return [swiftcomp_filename, macro_model_dimension]
