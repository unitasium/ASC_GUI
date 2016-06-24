# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
#from sg1DFastGenerate import *
#from sg1DAbaLayupGenerate import *
#from sg1DAbaSections import *
#from sg1DFromInputfile import *
from textRepr import *
from caeModules import *
from math import *
#from yZview import *
from utilities import *
import regionToolset
import os

def create1DSG(method,
               layup_fg='', thickness_fg='1.0', model_name_fg='', material_name='', offset_ratio_fg=0.0,
               model_name_abq='', part_name='', layup_abq='',
               rf_model_name = '', rf_part_name='', rf_section_name='', rf_offset_ratio=0.0,
               file_layup_input='', model_name_file='',
               element_type='five-noded'):
    
#    print """method %s ,
#               layup_fg=%s , thickness_fg=%s , model_name_fg=%s , material_name=%s , offset_ratio_fg= %f ,
#               model_name_abq=%s, part_name=%s, layup_abq=%s,
#               rf_model_name = %s, rf_part_name=%s, rf_section_name = %s, rf_offset_ratio= %f,
#               file_layup_input=%s,model_name_file=%s,
#               element_type=%s""" \
#               % (method,
#                layup_fg, thickness_fg, model_name_fg,material_name, offset_ratio_fg,
#                model_name_abq, part_name, layup_abq,
#                rf_model_name, rf_part_name, rf_section_name, rf_offset_ratio,
#                file_layup_input, model_name_file,
#                element_type)
#    print """method %s' ,
#               'layup_fg=%s , thickness_fg=%s , model_name_fg=%s , material_name=%s , offset_ratio_fg= %f """\
#               % (method, layup_fg, thickness_fg, 
#               model_name_fg, material_name, offset_ratio_fg)
    if method == 1:
#        print 'fastGenerate method'
        
        #fastGenerate(layup_fg, thickness_fg, model_name_fg, material_name, offset_ratio_fg, element_type)
#        print """method %s' ,
#           'layup_fg=%s , thickness_fg=%s , model_name_fg=%s , material_name=%s , offset_ratio_fg= %f, element_type=%s """\
#           % (method, layup_fg, thickness_fg, 
#           model_name_fg, material_name, offset_ratio_fg, element_type)
           
        fastGenerate1D(layup_fg, thickness_fg, model_name_fg, material_name, 
                       offset_ratio_fg, element_type)
        
    elif method == 2:
        #print 'other methods need to be added'
        abaLayupGenerate(model_name_abq, part_name, layup_abq, element_type)

    elif method == 3:
#        print 'abaSection1D method'
        abaSection1D(rf_model_name, rf_part_name, rf_section_name, rf_offset_ratio, element_type)
 
    elif method == 4:
        fromInputfile1D(file_layup_input, model_name_file,  element_type)    
    
    return 1



# ==============================================================================
#
#   Fast Generate
#
# ==============================================================================

def fastGenerate1D(layup, thickness, model_name, material_name, offset_ratio, element_type):
    
    cv = session.viewports[session.currentViewportName]
    part_name = 'Laminate'
    partsobj = mdb.models[model_name].parts
    set_name ='Set_layup'
    lamSecName = part_name+'_section'
    
    if element_type=='five-noded':
        abaEle_edge=4
    
    elif element_type=='four-noded':
        abaEle_edge=3
    
    elif element_type=='three-noded':
        abaEle_edge=2
    
    elif element_type=='two-noded':
        abaEle_edge=1
    
    #### get reduced string without '2s'  
    
    model = mdb.models[model_name]
    
    ##
    mid = layup.find(']')
    rr = layup[:mid]            ## truncated string rr
    
    rr = rr.replace('[',' ')
    rr = rr.replace('/',' ')
    rr = rr.replace('\\',' ')
    #--------------
    
    layup_s = rr.split()   ## list of angles
    
    #### get reduced string without '2s'
    qq = layup[mid+1:]
    s_exist = qq.find('s') 
    S_exist = qq.find('S')
    
    if s_exist != -1:
        symm = True        #symmetric
        try:
            times = int(qq.replace('s',''))
        except ValueError:
            times = 1
    elif S_exist != -1:
        symm = True
        try:
            times = int(qq.replace('S',''))
        except ValueError:
            times = 1
    else:
        symm = False
        try:
            times = int(qq)
        except ValueError:
            times = 1
    
    #### get the complete layup
    layup_ori = []
    
    if symm == False:
        layup_ori = layup_s * times
    if symm == True:
        pp = layup_s * times
        layup_ori = pp[:]
        for i in range(len(pp)):
            layup_ori.append(pp[-i-1])
    
    layuplist = list(set(layup_s))        ## distinct angle list
    lay_id = []
    for i in range(len(layup_ori)):
        id = layuplist.index(layup_ori[i]) + 1
        lay_id.append(id)
    
    ## Y-Z transform
    p = mdb.models[model_name].Part(name=part_name, dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts[part_name]
    
    datumPlaneYZ_id = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0).id
    datumAxisZ_id = p.DatumAxisByPrincipalAxis(principalAxis=ZAXIS).id
    
    #---------------------------------------------------
    YZworkPlaneTransform = (0,1,0,   0,0,1,  1,0,0,   0,0,0) #y-z plane
#    YZviewVector = (1.0, 0.0, 0.0)
#    YZcameraUpVector = (0.0, 0.0, 1.0)
    
    #--------------------------------------------------
    # create 3D beam model
    #
    s = mdb.models[model_name].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0,transform=YZworkPlaneTransform)
    
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    cv.view.setValues(session.views['Left'])
    
    p = mdb.models[model_name].parts[part_name]
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    
    t_total = thickness*len(layup_ori)
    sp = -t_total/2.0
    
    
    for i in range(len(layup_ori)):
        s.Line(point1=(0., sp), point2=(0., sp+thickness))
        sp += thickness
        
    e1, d2 = p.edges, p.datums
    p.Wire(sketchPlane=d2[datumPlaneYZ_id], sketchUpEdge=d2[datumAxisZ_id], sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s)
    s.unsetPrimaryObject()
    cv.setValues(displayedObject=p)
    del mdb.models[model_name].sketches['__profile__']    
    
    # mesh
    #
    e = p.edges
    p.seedEdgeByNumber(edges=e, number=abaEle_edge, constraint=FINER)
    p.generateMesh()
    
    p = mdb.models[model_name].parts[part_name]
    e = p.edges
    edges = e
    p.Set(edges=edges, name=set_name)
    
    region1 = p.sets[set_name]
    
    compositeLayup = p.CompositeLayup(
        name='CompositeLayup-1', description='', elementType=SHELL, 
        offsetType=SINGLE_VALUE, offsetValues=(offset_ratio, ), symmetric=False, 
        thicknessAssignment=FROM_SECTION)        
        
    compositeLayup.Section(preIntegrate=OFF, integrationRule=SIMPSON, 
        thicknessType=UNIFORM, poissonDefinition=DEFAULT, temperature=GRADIENT, 
        useDensity=OFF)
    compositeLayup.ReferenceOrientation(orientationType=GLOBAL, localCsys=None, 
        fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3)
    
    for i in range(len(layup_ori)):
        compositeLayup.CompositePly(suppressed=False, plyName='Ply-'+str(i+1), region=region1,
                                    material=material_name, thicknessType=SPECIFY_THICKNESS, thickness=thickness,
                                    orientationType=SPECIFY_ORIENT, orientationValue=float(layup_ori[i]),
                                    additionalRotationType=ROTATION_NONE, additionalRotationField='',
                                    axis=AXIS_3, angle=0.0, numIntPoints=3)
        
    setViewYZ(nsg=1, obj=p)
    
    return 1
    


# ==============================================================================
#
#   Composite Layups
#
# ==============================================================================

def abaLayupGenerate(model_name_abq, part_name,layup_abq, element_type):

    cv = session.viewports[session.currentViewportName]
    
    model_name = model_name_abq

    model = mdb.models[model_name]
    part  = model.parts[part_name]
    cv.setValues(displayedObject=part)
    
    set_name = 'Set_layup'
    
    layup_name_inuse = layup_abq

    if element_type == 'five-noded':
        abaEle_edge = 4
    elif element_type == 'four-noded':
        abaEle_edge = 3
    elif element_type == 'three-noded':
        abaEle_edge = 2
    elif element_type == 'two-noded':
        abaEle_edge = 1
    
    plies_sc = {}
    ply_id_sc = 0
    
    layup_abq = part.compositeLayups[layup_name_inuse]
    for i in range(len(layup_abq.plies)):
        if layup_abq.plies[i].suppressed == False:    # construct plies_sc  {'ply_id_sc':}
            plies_sc[ply_id_sc] = layup_abq.plies[i]  #  the key of plies_sc[ply_id_sc] begin at 0 .
            ply_id_sc = ply_id_sc + 1
    
    n_ply = len(plies_sc)
    
    layup_t = []
    t_total = 0.0
    
    for ply_id in range(n_ply):
        ply_t = plies_sc[ply_id].thickness
        t_total = t_total + ply_t
        layup_t.append(ply_t)
    
    ep = []
    sp = []
    ep_i = 0
    for i in range(n_ply):
        ep_i = layup_t[i] + ep_i
        ep.append(ep_i - t_total/2)
        sp.append(ep_i - t_total/2 - layup_t[i])
    
    #--------------------------------------------------
    # create 3D beam model
    #
    #
    p = mdb.models[model_name].parts[part_name]
    wire_key = p.features.keys()[-1]
    s1 = p.features[wire_key].sketch
    mdb.models[model_name].ConstrainedSketch(name='__edit__', objectToCopy=s1)
    s2 = mdb.models[model_name].sketches['__edit__']
    g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
    s2.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s2, upToFeature=p.features[wire_key], 
        filter=COPLANAR_EDGES)
    t5 = g.values()    
    s2.delete(objectList=tuple(t5))
    
    for i in range(len(layup_t)):
        s2.Line(point1=(0., sp[i]), point2=(0., ep[i]))
    
    s2.unsetPrimaryObject()
    p = mdb.models[model_name].parts[part_name]
    p.features[wire_key].setValues(sketch=s2)
    del mdb.models[model_name].sketches['__edit__']
    p = mdb.models[model_name].parts[part_name]
    p.regenerate()
    
    p = mdb.models[model_name].parts[part_name]
    e = p.edges

    p.Set(edges=e, name=set_name)

    #-----------------------------------
    # mesh
    #
    e = p.edges
    p.seedEdgeByNumber(edges=e, number=abaEle_edge, constraint=FINER)
    p.generateMesh()
    setYZview()
    
    return 1



# ==============================================================================
#
#   Composite Sections
#
# ==============================================================================

def abaSection1D(model_name = '', part_name = '', section_name = '', offset_ratio = 0.0, element_type = 'five-noded'):

    model = mdb.models[model_name]
    set_name='Set_layup'
    cv = session.viewports['Viewport: 1']
    
    if element_type=='five-noded':
        abaEle_edge=4
    elif element_type=='four-noded':
        abaEle_edge=3
    elif element_type=='three-noded':
        abaEle_edge=2
    elif element_type=='two-noded':
        abaEle_edge=1
        
    plies_sc = {}
    n_ply = len(plies_sc)
    layup_t = []
    t_total = 0.0
    layup_ori = []
    layup_mat = []

    layup_sec = model.sections[section_name].layup
    for ply_id in range(len(layup_sec)) :
        plies_sc[ply_id] = layup_sec[ply_id]  #  the key of plies_sc[ply_id_sc] begin at 0 .
        
        ply_t = plies_sc[ply_id].thickness
        t_total = t_total+ply_t
        layup_t.append(ply_t)
        
        ply_ori = plies_sc[ply_id].orientAngle
        layup_ori.append(ply_ori)
        
        ply_mat = plies_sc[ply_id].material
        layup_mat.append(ply_mat) 

    n_ply = len(plies_sc)
        
    ep = []
    sp = []
    ep_i = 0
    for i in range(n_ply):
        ep_i = layup_t[i] + ep_i
        ep.append(ep_i - t_total/2)
        sp.append(ep_i - t_total/2 - layup_t[i])   

    ## Y-Z transform
    p = mdb.models[model_name].Part(name=part_name, dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts[part_name]
    
    datumPlaneYZ_id = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0).id
    datumAxisZ_id = p.DatumAxisByPrincipalAxis(principalAxis=ZAXIS).id
    
    #---------------------------------------------------
    YZworkPlaneTransform = (0,1,0,   0,0,1,  1,0,0,   0,0,0) #y-z plane
    YZviewVector = (1.0, 0.0, 0.0)
    YZcameraUpVector = (0.0, 0.0, 1.0)
    
    #--------------------------------------------------
    # create 3D beam model
    #
    s = mdb.models[model_name].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0,transform=YZworkPlaneTransform)
    
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    cv.view.setValues(session.views['Left'])
    
    p = mdb.models[model_name].parts[part_name]
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    
    for i in range(len(layup_t)):
        s.Line(point1=(0., sp[i]), point2=(0., ep[i]))
    
    e1, d2 = p.edges, p.datums
    p.Wire(sketchPlane=d2[datumPlaneYZ_id], sketchUpEdge=d2[datumAxisZ_id], sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s)
    s.unsetPrimaryObject()
    cv.setValues(displayedObject=p)
    del mdb.models[model_name].sketches['__profile__']    
    
    # mesh
    #
    e = p.edges
    p.seedEdgeByNumber(edges=e, number=abaEle_edge, constraint=FINER)
    p.generateMesh()
    
    p = mdb.models[model_name].parts[part_name]
    e = p.edges
    edges = e
    p.Set(edges=edges, name=set_name)
    
    region1 = p.sets[set_name]
    
    compositeLayup = p.CompositeLayup(
        name='CompositeLayup-1', description='', elementType=SHELL, 
        offsetType=SINGLE_VALUE, offsetValues=(offset_ratio, ), symmetric=False, 
        thicknessAssignment=FROM_SECTION)        
        
    compositeLayup.Section(preIntegrate=OFF, integrationRule=SIMPSON, 
        thicknessType=UNIFORM, poissonDefinition=DEFAULT, temperature=GRADIENT, 
        useDensity=OFF)
    compositeLayup.ReferenceOrientation(orientationType=GLOBAL, localCsys=None, 
        fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3)
    
    for i in range(n_ply):
        compositeLayup.CompositePly(suppressed=False, plyName='Ply-'+str(i+1), region=region1,
                                    material=layup_mat[i], thicknessType=SPECIFY_THICKNESS, thickness=layup_t[i],
                                    orientationType=SPECIFY_ORIENT, orientationValue=float(layup_ori[i]),
                                    additionalRotationType=ROTATION_NONE, additionalRotationField='',
                                    axis=AXIS_3, angle=0.0, numIntPoints=3)
        
    setYZview()
    return 1



# ==============================================================================
#
#   Read File
#
# ==============================================================================

def fromInputfile1D(file_layup_input, model_name, element_type):

    model = mdb.models[model_name_file]
    mat_abq = model.materials.keys()
    set_name = 'Set_layup'
    cv = session.viewports['Viewport: 1']
    
    layup_input = file_layup_input.replace('\\','/')
    temp = layup_input.rsplit('/')
    temp = temp[-1]
    part_name = temp.rsplit('.')[0]
    
    if element_type == 'five-noded':
        abaEle_edge = 4
    elif element_type == 'four-noded':
        abaEle_edge = 3
    elif element_type == 'three-noded':
        abaEle_edge = 2
    elif element_type == 'two-noded':
        abaEle_edge = 1

    # ------------------------------------
    # Read layup data from layup input file
    plies_sc = {}
    mat_dict = {}
    parameter_line = [1]
    sym_flag = 'n'
    offset_ratio = 0.0
    i = 1
    j = 0
#    print '--> Reading Layup input file...'
    
    with open(layup_input, 'r') as fin:
        for line in fin:
            line = line.strip()
            if line == '\n' or line == '':
                continue
            else:
                line = line.split()
                if i == parameter_line[-1]:
                    n_ply = int(line[0])              # Read the number of plies
                    nmat = int(line[1])            # Read the number of materials
                    if len(line) <= 4:
                        sym_flag = str(line[2])             # Read if the layup should be symmetrical or antisymmetric ( n, sym, antisym)
                    if len(line) == 4:
                        offset_ratio = float(line[3])            # Read the offset_ratio
                    i += 1
                elif j <= (n_ply-1):                    # construct plies_sc  {'ply_id_sc':}
                    ply_id_sc = j        #  the key of plies_sc[ply_id_sc] begin at 0.
                    plies_sc[ply_id_sc] = (float(line[0]), float(line[1]), int(line[2]))   # thickness, orientation, mat_id
                    if sym_flag[0] == 's':
                        ply_id_sc_s = 2*n_ply - 1 - ply_id_sc
                        plies_sc[ply_id_sc_s] = plies_sc[ply_id_sc]
                    elif sym_flag[0] == 'a' and ply_id_sc != (n_ply-1):
                        ply_id_sc_a = 2*(n_ply-1) - ply_id_sc
                        plies_sc[ply_id_sc_a] = plies_sc[ply_id_sc]
                    j += 1
                elif j <= (n_ply - 1 + nmat):          # Read element connectivities
                    mat_id = int(line[0])
                    mat_name = str(line[1])
                    mat_dict[mat_id] = mat_name
                    if mat_name not in mat_abq:
                        raise ValueError('material \'%s \' is not existed in model \'%s\'.' %(mat_name, model_name))
                    j += 1
    
    if len(mat_dict) != nmat:
        raise ValueError('The material types existed in the layup is not equal to the number of materials specified!')
    
    n_ply = len(plies_sc)
    
    layup_t = []
    layup_ori = []
    t_total = 0.0
    layup_mat = []
    for ply_id in range(n_ply) :
        ply_t = plies_sc[ply_id][0]
        t_total = t_total + ply_t
        layup_t.append(ply_t)
        layup_ori.append(plies_sc[ply_id][1])
        mat_id = plies_sc[ply_id][2]
        mat_name = mat_dict[mat_id]
        layup_mat.append(mat_name)
    
    ep = []
    sp = []
    ep_i = 0
    for i in range(n_ply):
        ep_i = layup_t[i] + ep_i
        ep.append(ep_i - t_total/2)
        sp.append(ep_i - t_total/2 - layup_t[i])
    
    ## Y-Z transform
    p = mdb.models[model_name].Part(name=part_name, dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts[part_name]
    
    datumPlaneYZ_id = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0).id
    datumAxisZ_id = p.DatumAxisByPrincipalAxis(principalAxis=ZAXIS).id
    
    #---------------------------------------------------
    YZworkPlaneTransform = (0,1,0, 0,0,1, 1,0,0, 0,0,0) #y-z plane
    YZviewVector = (1.0, 0.0, 0.0)
    YZcameraUpVector = (0.0, 0.0, 1.0)
    
    #--------------------------------------------------
    # create 3D beam model
    #
    s = mdb.models[model_name].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0,transform=YZworkPlaneTransform)
    
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    cv.view.setValues(session.views['Left'])
    
    p = mdb.models[model_name].parts[part_name]
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    
    for i in range(len(layup_t)):
        s.Line(point1=(0., sp[i]), point2=(0., ep[i]))
    
    e1, d2 = p.edges, p.datums
    p.Wire(sketchPlane=d2[datumPlaneYZ_id], sketchUpEdge=d2[datumAxisZ_id], sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s)
    s.unsetPrimaryObject()
    cv.setValues(displayedObject=p)
    del mdb.models[model_name].sketches['__profile__']    
    
    # mesh
    #
    e = p.edges
    p.seedEdgeByNumber(edges=e, number=abaEle_edge, constraint=FINER)
    p.generateMesh()
    
    p = mdb.models[model_name].parts[part_name]
    e = p.edges
    edges = e
    p.Set(edges=edges, name=set_name)
    
    region1 = p.sets[set_name]
    
    compositeLayup = p.CompositeLayup(
        name='CompositeLayup-1', description='', elementType=SHELL, 
        offsetType=SINGLE_VALUE, offsetValues=(offset_ratio, ), symmetric=False, 
        thicknessAssignment=FROM_SECTION)        
        
    compositeLayup.Section(preIntegrate=OFF, integrationRule=SIMPSON, 
        thicknessType=UNIFORM, poissonDefinition=DEFAULT, temperature=GRADIENT, 
        useDensity=OFF)
    compositeLayup.ReferenceOrientation(orientationType=GLOBAL, localCsys=None, 
        fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3)
    
    for i in range(n_ply):
        compositeLayup.CompositePly(suppressed=False, plyName='Ply-'+str(i+1), region=region1,
                                    material=layup_mat[i], thicknessType=SPECIFY_THICKNESS, thickness=layup_t[i],
                                    orientationType=SPECIFY_ORIENT, orientationValue=float(layup_ori[i]),
                                    additionalRotationType=ROTATION_NONE, additionalRotationField='',
                                    axis=AXIS_3, angle=0.0, numIntPoints=3)
        
    setYZview()
    
    return 1