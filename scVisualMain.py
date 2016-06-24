# -*- coding: utf-8 -*-

from odbAccess import *
from odbMaterial import *
from odbSection import *
from abaqus import *
from abaqusConstants import *
#from scVisual2D import *
#from scVisual3D import *
#from scVisual1D import *
from utilities import *
from textRepr import *
from UcheckDehoVisual import *
import os.path

# ==============================================================================
#
#   Main
#
# ==============================================================================

def visualization(macro_model, ap_flag, sc_input):

#    sc_input = sc_input.replace('\\','/')

    # =======================================================================
    # Read data from files
    # =======================================================================
    sc_input=sc_input.replace('\\','/')
#    debug = open(sc_input + '.debug', 'w')
#    print sc_input
    # =======================================================================
    # Read data from files
    # =======================================================================
    
    
    u_filename   = sc_input + r'.u'
    sg_filename  = sc_input + r'.sg'
    sn_filename  = sc_input + r'.sn'
    sgm_filename = sc_input + r'.sgm'
    snm_filename = sc_input + r'.snm'
    
#    sc_input_temp = sc_input.split('/')
#    project_path  = '/'.join(sc_input_temp[:-1])
    project_path = os.path.dirname(sc_input)
#    project_name  = sc_input_temp[-1]
    sc_input_sc = os.path.basename(sc_input)
    checkDehoVisual(sc_input_sc, 'visual')
    #print 'sc_input_sc %s' %sc_input_sc
    project_name = sc_input_sc.split('.')
    project_name = project_name[0]
    #print 'project_name %s' %project_name
    # check if the odb has already exist, and check if the file .sc exist or not.
    checkDehoVisual(sc_input_sc, 'visual')
    
    
    macro_model_dimension=str(macro_model)+'D'
    
    if ap_flag==False:
        if macro_model_dimension == '1D':            # Beam
            skip_line = [1, 2, 3, 4]
        elif macro_model_dimension == '2D':          # Plate/Shell
            skip_line = [1, 2, 3]
        elif macro_model_dimension == '3D':          # Solid/Block
            skip_line = [1]
    else:
        if macro_model_dimension == '1D':            # Beam
            skip_line = [1, 2, 3, 4, 5]
        elif macro_model_dimension == '2D':          # Plate/Shell
            skip_line = [1, 2, 3, 4]
        elif macro_model_dimension == '3D':          # Solid/Block
            skip_line = [1, 2 ]
            
    i = 1
    j = 1
    
    # ------------------------------------
    # Read model data from VABS input file
    
    node_coord = []  # Nodal coordinates      [(n1, x1, x2, x3), ...]
    elem_connt = []  # Element connectivities [(e1, n1, n2, n3, n4, ...), ...]
    elem_sectn = {}  # Material sections      {'s1': [e1, e2, e3, ...], ...}
    elem_label = []  # Element labels         [e1, e2, e3, ...]
    
    elem_connt_s3 = []
    elem_connt_s6 = []
    elem_connt_s4 = []
    elem_connt_s8 = []
    elem_connt_s9 = []
    
    elem_connt_c4  = []
    elem_connt_c10 = []
    elem_connt_c8  = []
    elem_connt_c20 = []
    
    elem_connt_b31_temp=[]
    elem_connt_b31 = []
    
    print '--> Reading SwiftComp input file...'
    
    with open(sc_input, 'r') as fin:
        for line in fin:
            line = line.strip()
            if line == '\n' or line == '':
                continue
            else:
                line = line.split()
                if i in skip_line:
                    i += 1
                    continue
                elif i == skip_line[-1] + 1:
                    nsg = int(line[0])              # Read the dimension of SG
                    nnode = int(line[1])            # Read the number of nodes
                    nelem = int(line[2])            # Read the number of elements
                    
                    print 'nsg %d'%nsg
                    print 'nnode %d'%nnode 
                    print 'nelem %d'%nelem
                    i += 1
                elif j <= nnode:                    # Read nodal coordinates
                    if nsg == 1:
                        node_coord.append((int(line[0]), 0.0, 0.0, float(line[1])))
                    elif nsg == 2:
                        node_coord.append((int(line[0]), 0.0, float(line[1]), float(line[2])))
                    elif nsg == 3:
                        node_coord.append((int(line[0]), float(line[1]), float(line[2]), float(line[3])))
                    j += 1
                elif j <= (nnode + nelem):          # Read element connectivities
                    elem_label.append(int(line[0]))
                    temp = line[2:]
                    temp = [int(i) for i in temp if i != '0']
                    temp = [int(line[0])] + temp
                    elem_connt.append(tuple(temp))
                    
                    if len(line) == 7:       # 1D element
                        elem_connt_b31_temp.append(tuple(temp))
                    elif len(line) == 11:       # 2D element
                        if len(temp) == 4:
                            elem_connt_s3.append(tuple(temp))
                        elif len(temp) == 7:
                            elem_connt_s6.append(tuple(temp))
                        elif len(temp) == 5:
                            elem_connt_s4.append(tuple(temp))
                        elif len(temp) == 9:
                            elem_connt_s8.append(tuple(temp))
                        elif len(temp) == 10:
                            elem_connt_s9.append(tuple(temp))
                    elif len(line) >= 22:       # 3D element
                        if len(temp) == 5:
                            elem_connt_c4.append(tuple(temp))
                        elif len(temp) == 11:
                            elem_connt_c10.append(tuple(temp))
                        elif len(temp) == 9:
                            elem_connt_c8.append(tuple(temp))
                        elif len(temp) == 21:
                            elem_connt_c20.append(tuple(temp))
                    sect = line[1]                  # Read material sections
                    if sect not in elem_sectn.keys():
                        elem_sectn[sect] = []
                    elem_sectn[sect].append(int(line[0]))
                    j += 1
    
    elem_connt_s3.sort()
    elem_connt_s6.sort()
    elem_connt_s4.sort()
    elem_connt_s8.sort()
    elem_connt_c4.sort()
    elem_connt_c10.sort()
    elem_connt_c8.sort()
    elem_connt_c20.sort()
    
    # 1D 
    elem_connt_b31_temp.sort()
    print '    Done.'

    # -----------------------------------------
    # Read nodal displacement data from .U file
    
    print '--> Reading result files...'
    node_label = []  # Node labels         [n1, n2, n3, ...]
    u_data     = []  # Nodal displacements [(u1, u2, u3), ...]
    
    try:
        with open(u_filename, 'r') as fin:
            for line in fin:
                line = line.strip()
                if line == '\n' or line == '':
                    continue
                else:
                    line = line.split()
                    node_label.append(int(line[0]))
                    u_data.append((float(line[1]), float(line[2]), float(line[3])))
    except:
        print '--! Cannot find .u file.'
                
    #print len(u_data)
    
    # ------------------------------------------------------
    # Read integration point strain/stress data from .sg file
    
    sg_strain = []  # Integration point strains  [(e11,  e22,  e33, 2e23, 2e13, 2e12), ...]
    sg_stress = []  # Integration point stresses [(s11,  s22,  s33,  s23,  s13,  s12), ...]
    
    try:
        with open(sg_filename, 'r') as fin:
            for line in fin:
                line = line.strip()
                if line == '\n' or line == '':
                    continue
                else:
                    line = line.split()
                    temp_e = [float(i) for i in line[nsg:nsg+6]]
                    temp_s = [float(i) for i in line[nsg+6:nsg+12]]
                    sg_strain.append(tuple(temp_e))
                    sg_stress.append(tuple(temp_s))
    except:
        print '--! Cannot find .sg file.'
    
    # --------------------------------------------
    # Read element nodal strain data from .sn file
    
    sn_strain = []  # Element nodal strains  [(en11,  en22,  en33, 2en23, 2en13, 2en12), ...]
    sn_stress = []  # Element nodal stresses [(sn11,  sn22,  sn33,  sn23,  sn13,  sn12), ...]
    
    try:
        with open(sn_filename, 'r') as fin:
            for line in fin:
                line = line.strip()
                if line == '\n' or line == '':
                    continue
                else:
                    line = line.split()
                    temp_e = [float(i) for i in line[nsg:nsg+6]]
                    temp_s = [float(i) for i in line[nsg+6:nsg+12]]
                    sn_strain.append(tuple(temp_e))
                    sn_stress.append(tuple(temp_s))
    except:
        print '--! Cannot find .sn file.'
        
    # ------------------------------------------------------
    # Read integration point strain/stress data under material frame from .sgm file
    
    sgm_strain = []  # Integration point strains  [(e11,  e22,  e33, 2e23, 2e13, 2e12), ...]
    sgm_stress = []  # Integration point stresses [(s11,  s22,  s33,  s23,  s13,  s12), ...]
    
    try:
        with open(sgm_filename, 'r') as fin:
            for line in fin:
                line = line.strip()
                if line == '\n' or line == '':
                    continue
                else:
                    line = line.split()
                    temp_e = [float(i) for i in line[nsg:nsg+6]]
                    temp_s = [float(i) for i in line[nsg+6:nsg+12]]
                    sgm_strain.append(tuple(temp_e))
                    sgm_stress.append(tuple(temp_s))
    except:
        print '--! Cannot find .sgm file.'
    
    # --------------------------------------------
    # Read element nodal strain data under material frame from .snm file
    
    snm_strain = []  # Element nodal strains  [(en11,  en22,  en33, 2en23, 2en13, 2en12), ...]
    snm_stress = []  # Element nodal stresses [(sn11,  sn22,  sn33,  sn23,  sn13,  sn12), ...]
    
    try:
        with open(snm_filename, 'r') as fin:
            for line in fin:
                line = line.strip()
                if line == '\n' or line == '':
                    continue
                else:
                    line = line.split()
                    temp_e = [float(i) for i in line[nsg:nsg+6]]
                    temp_s = [float(i) for i in line[nsg+6:nsg+12]]
                    snm_strain.append(tuple(temp_e))
                    snm_stress.append(tuple(temp_s))
    except:
        print '--! Cannot find .snm file.'
    
    print '    Done.'
    
    #=========================================================
    # tranfer sn data for nsg==1:  only work for cases that each edge contains the same number of B31 elements!
    #=========================================================
    new_conn = []
    if nsg == 1:
        print '--> Convert beam element infomation...'
        
#        elem_connt_b31_temp : element_id_aba,  element connectivity                           
        nelem_edge=len(elem_connt_b31_temp[0]) -2  # nelem_edge per edge/(element of swiftcomp)
        
        if nelem_edge == 1:
            elem_connt_b31= elem_connt_b31_temp
            print '--> Two noded beam element are implemented, no convertion is necessary. '
    
            
        else:
            elem_label = []
            for item in elem_connt_b31_temp:
                elabel = (item[0] - 1) * nelem_edge + 1
                for i in range(nelem_edge):
                    elem_label.append(elabel + i)
                if nelem_edge == 4:
                    new_conn.append((elabel, item[1], item[3]))
                    new_conn.append((elabel + 1, item[3], item[5]))
                    new_conn.append((elabel + 2, item[5], item[4]))
                    new_conn.append((elabel + 3, item[4], item[2]))
                elif nelem_edge == 3:
                    new_conn.append((elabel, item[1], item[3]))
                    new_conn.append((elabel + 1, item[3], item[4]))
                    new_conn.append((elabel + 2, item[4], item[2]))
                elif nelem_edge == 2:
                    new_conn.append((elabel, item[1], item[3]))
                    new_conn.append((elabel + 1, item[3], item[2]))
                
            elem_connt_b31 = new_conn
         
            elem_sectn_new = {}
            for sect, elems in elem_sectn.iteritems():
                elem_sectn_new[sect] = []
                for i in range(len(elems)):
                    temp_i = [(elems[i]-1) * nelem_edge + 1 + j for j in range(nelem_edge)]
                    elem_sectn_new[sect] = elem_sectn_new[sect] + temp_i
            elem_sectn = elem_sectn_new
            new_strain = []
            new_stress = []
                
            nedge = len(elem_label) / nelem_edge
            print 'number of beam elements in the 1D SG model: '
            print nedge
                
            if nelem_edge == 4:
                nodes_edge = [0,2,2,4,4,3,3,1]
            elif nelem_edge == 3:
                nodes_edge = [0,2,2,3,3,1]
            elif nelem_edge == 2:
                nodes_edge = [0,2,2,1]
    
            for edge_i in range(nedge):
                for j in range(len(nodes_edge)):
                    new_strain.append(sn_strain[nodes_edge[j] + (nelem_edge+1) * edge_i])
                    new_stress.append(sn_stress[nodes_edge[j] + (nelem_edge+1) * edge_i])
            sn_strain = new_strain
            sn_stress = new_stress

    # =======================================================================
    # Create odb file and import data
    # =======================================================================
    
    # ---------------------
    # Create a new odb file
    print '--> Creating ODB file...'
    odb_name = project_name
    odb_title = project_name
    odb_file_name = os.path.join(project_path, project_name + '.odb')

    odb = Odb(name = odb_name, 
              analysisTitle = odb_title, 
              description = 'SwiftComp Dehomogenization', 
              path = odb_file_name)
    
    if nsg == 2:
        visualization2D(odb, project_name, node_coord, elem_connt_s3, elem_connt_s6, 
                        elem_connt_s4, elem_connt_s8, elem_connt_s9, elem_sectn, node_label, elem_label, 
                        u_data, sg_strain, sg_stress, sn_strain, sn_stress, 
                        sgm_strain, sgm_stress, snm_strain, snm_stress)
    elif nsg == 3:
        visualization3D(odb, project_name, node_coord, elem_connt_c4, elem_connt_c10, 
                        elem_connt_c8, elem_connt_c20, elem_sectn, node_label, elem_label, 
                        u_data, sg_strain, sg_stress, sn_strain, sn_stress, 
                        sgm_strain, sgm_stress, snm_strain, snm_stress)
    elif nsg == 1:
        visualization1D(odb, project_name, node_coord, elem_connt_b31, elem_sectn, node_label, elem_label, 
                        u_data, sg_strain, sg_stress, sn_strain, sn_stress)
                        
    print '    Done.'
    
    session.odbs[odb_name].close()
    odb = openOdb(odb_file_name)
    
    # Customize the viewport
    da = session.drawingArea
    da_width = da.width
    da_height = da.height
    da_origin = da.origin
    
    vp1 = session.viewports[session.currentViewportName]
    vp1.setValues(origin = da_origin, width = da_width / 2.0, height = da_height)
    da_origin = (da_origin[0] + da_width / 2.0, da_origin[1])
    setViewYZ(vp=vp1, nsg=nsg, obj=odb)
    vp1.odbDisplay.setPrimaryVariable(variableLabel = 'EN', 
                                      outputPosition = ELEMENT_NODAL, 
                                      refinement = (COMPONENT, 'EN11'))
    vp1.restore()
    
    font_family = 'consolas'
    font_style  = 'medium'
    font_size   = 140
    view_font = '-*-' + font_family + '-' + font_style + '-r-normal-*-*-' + str(font_size) + '-*-*-m-*-*-*'
    vp1.viewportAnnotationOptions.setValues(
        triadFont = view_font, 
        legendFont = view_font, 
        titleFont = view_font, 
        stateFont = view_font, 
        legendMinMax = ON, 
        legendDecimalPlaces = 6, 
        legendBackgroundStyle = TRANSPARENT)
    vp1.odbDisplay.display.setValues(plotState = CONTOURS_ON_DEF)
    
    vp2 = session.Viewport(name = 'Viewport: 2', 
                           origin = da_origin, width = da_width / 2.0, height = da_height)
    setViewYZ(vp=vp2, nsg=nsg, obj=odb)
    vp2.odbDisplay.setPrimaryVariable(variableLabel = 'SN', 
                                     outputPosition = ELEMENT_NODAL, 
                                     refinement = (COMPONENT, 'SN11'))

    vp1.makeCurrent()
                                     
    session.linkedViewportCommands.setValues(linkViewports = True)

    return 1



# ==============================================================================
#
#   Visualization of 1D SG
#
# ==============================================================================

def visualization1D(odb_vis, project_name, node_coord, elem_connt_b31, 
                    elem_sectn, node_label, elem_label, 
                    u_data, sg_strain, sg_stress, sn_strain, sn_stress):
                    

    # -----------------------
    # Create a dummy material

    material_name = 'Elastic material'
    material_1 = odb_vis.Material(name = material_name)
    material_1.Elastic(type = ISOTROPIC, 
                       temperatureDependency = OFF, 
                       dependencies = 0, 
                       noCompression = OFF, 
                       noTension = OFF, 
                       moduli = LONG_TERM, 
                       table = ((12000, 0.3), ))
    
    # -------------------------
    # Create different sections
    section_name_g = 'nLayer'
    abq_section = {}
    for k in elem_sectn.keys():
        section_name = section_name_g + '-' + k
        abq_section[k] = odb_vis.HomogeneousSolidSection(
            name = section_name, material = material_name
            )
    
    # -----------------
    # Create a new part
    
    part_1 = odb_vis.Part(name = 'Part-1', embeddedSpace = THREE_D, type = DEFORMABLE_BODY)
    node_coord = tuple(node_coord)
    # Import nodes
    part_1.addNodes(nodeData = node_coord, nodeSetName = 'nSet-1')
    odb_vis.save()
     
    # Import elements
    if elem_connt_b31 != []:
        elem_connt_b31 = tuple(elem_connt_b31)
        part_1.addElements(elementData = elem_connt_b31, type = 'B31', elementSetName = 'eSet-b31')
    odb_vis.save()
    
    # ---------------------
    # Create a new instance
    
    instance_1 = odb_vis.rootAssembly.Instance(name = 'Part-1-1', object = part_1)
    for k in elem_sectn.keys():  # Assign sections to element sets
        section_name = section_name_g + ' - ' + k
        elem_sectn_label = tuple(elem_sectn[k])
        elem_set = odb_vis.rootAssembly.instances['Part-1-1'].\
            ElementSetFromElementLabels(name = section_name, elementLabels = elem_sectn_label)
        instance_1.assignSection(region = elem_set, section = abq_section[k])
    odb_vis.save()
    
    # ---------------------------
    # Create a new step and frame
    
    step_1 = odb_vis.Step(name = 'Step-1', description = '', domain = TIME, timePeriod = 1.0)
    analysis_time = 0.1
    frame_1 = step_1.Frame(incrementNumber = 1, frameValue = analysis_time, description = '')
    
    # ------------------------
    # Import displacement data
    
    if u_data != []:
        u_data = tuple(u_data)
        u_field = frame_1.FieldOutput(name = 'U', description = 'Displacements.', type = VECTOR,
                                      validInvariants=(MAGNITUDE,),
                                      )
        u_field.addData(position = NODAL, 
                        instance = instance_1, 
                        labels = node_label, 
                        data = u_data)
        step_1.setDefaultDeformedField(u_field)
        odb_vis.save()
    
    elem_label = tuple(elem_label)
    
    
    
    # Strains at integration points
    if sg_strain != []:
        sg_strain = tuple(sg_strain)
        s_field = frame_1.FieldOutput(
            name = 'EG', 
            description = 'Strains at Gaussian points.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EG11', 'EG22', 'EG33', '2EG23', '2EG13', '2EG12'),
            validInvariants=(MISES,TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL,),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            instance = instance_1, 
            labels = elem_label, 
            data = sg_strain
            )
        odb_vis.save()
    
    # Stresses at integration points
    if sg_stress != []:
        sg_stress = tuple(sg_stress)
        s_field = frame_1.FieldOutput(
            name = 'SG', 
            description = 'Stresses at Gaussian points.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SG11', 'SG22', 'SG33', 'SG23', 'SG13', 'SG12'),
            validInvariants=(MISES,TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL,),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            instance = instance_1, 
            labels = elem_label, 
            data = sg_stress
            )
        odb_vis.save()
    
    # Strains at elemental nodes
    if sn_strain != []:
        en_field = frame_1.FieldOutput(
            name = 'EN', 
            description = 'Strains at nodes.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EN11', 'EN22', 'EN33', '2EN23', '2EN13', '2EN12'),
            validInvariants=(MISES,TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL,),
            )
        en_field.addData(
            position = ELEMENT_NODAL,  
            instance = instance_1, 
            labels = elem_label, 
            data = sn_strain
            )
    
#        step_1.setDefaultField(en_field)
        odb_vis.save()
    
    # Stresses at elemental nodes
    if sn_stress != []:
        sn_stress = tuple(sn_stress)
        sn_field = frame_1.FieldOutput(
            name = 'SN', 
            description = 'Stresses at nodes.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SN11', 'SN22', 'SN33', 'SN23', 'SN13', 'SN12'),
            validInvariants=(MISES,TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL,),
            )
        sn_field.addData(
            position = ELEMENT_NODAL,  
            instance = instance_1, 
            labels = elem_label, 
            data = sn_stress
            )
        odb_vis.save()
        
    return 1
    


# ==============================================================================
#
#   Visualization of 2D SG
#
# ==============================================================================

def visualization2D(odb_vis, project_name, node_coord, elem_connt_s3, elem_connt_s6, 
                    elem_connt_s4, elem_connt_s8, elem_connt_s9, elem_sectn, node_label, elem_label, 
                    u_data, sg_strain, sg_stress, sn_strain, sn_stress, 
                    sgm_strain, sgm_stress, snm_strain, snm_stress):

    # -----------------------
    # Create a dummy material
    
    material_name = 'Elastic material'
    material_1 = odb_vis.Material(name = material_name)
    material_1.Elastic(type = ISOTROPIC, 
                       temperatureDependency = OFF, 
                       dependencies = 0, 
                       noCompression = OFF, 
                       noTension = OFF, 
                       moduli = LONG_TERM, 
                       table = ((12000, 0.3), ))
                       
    # -------------------------
    # Create different sections
    section_name_g = 'Homogeneous shell section'
    abq_section = {}
    for k in elem_sectn.keys():
        section_name = section_name_g + '-' + k
        abq_section[k] = odb_vis.HomogeneousShellSection(
            name = section_name, material = material_name, thickness = 0.1
            )
    s_cat = odb_vis.SectionCategory(name = 'S5', description = '')
    sp_bot = s_cat.SectionPoint(number = 1, description = 'Bottom')
    
    # -----------------
    # Create a new part
    
    part_1 = odb_vis.Part(name = 'Part-1', embeddedSpace = THREE_D, type = DEFORMABLE_BODY)
    node_coord = tuple(node_coord)
    # Import nodes
    part_1.addNodes(nodeData = node_coord, nodeSetName = 'nSet-1')
    odb_vis.save()
    
#    elem_connt = tuple(elem_connt)
    # Import elements
    if elem_connt_s3 != []:
        elem_connt_s3 = tuple(elem_connt_s3)
        part_1.addElements(elementData = elem_connt_s3, type = 'S3', elementSetName = 'eSet-s3', sectionCategory = s_cat)
    if elem_connt_s6 != []:
        elem_connt_s6 = tuple(elem_connt_s6)
        part_1.addElements(elementData = elem_connt_s6, type = 'DS6', elementSetName = 'eSet-s6', sectionCategory = s_cat)
    if elem_connt_s4 != []:
        elem_connt_s4 = tuple(elem_connt_s4)
        part_1.addElements(elementData = elem_connt_s4, type = 'S4', elementSetName = 'eSet-s4', sectionCategory = s_cat)
    if elem_connt_s8 != []:
        elem_connt_s8 = tuple(elem_connt_s8)
        part_1.addElements(elementData = elem_connt_s8, type = 'DS8', elementSetName = 'eSet-s8', sectionCategory = s_cat)
    if elem_connt_s9 != []:
        elem_connt_s9 = tuple(elem_connt_s9)
        part_1.addElements(elementData = elem_connt_s9, type = 'M3D9', elementSetName = 'eSet-s9', sectionCategory = s_cat)
    odb_vis.save()
    
    # ---------------------
    # Create a new instance
    
    instance_1 = odb_vis.rootAssembly.Instance(name = 'Part-1-1', object = part_1)
    for k in elem_sectn.keys():  # Assign sections to element sets
        section_name = section_name_g + ' - ' + k
        elem_sectn_label = tuple(elem_sectn[k])
        elem_set = odb_vis.rootAssembly.instances['Part-1-1'].\
            ElementSetFromElementLabels(name = section_name, elementLabels = elem_sectn_label)
        instance_1.assignSection(region = elem_set, section = abq_section[k])
    odb_vis.save()
    
    # ---------------------------
    # Create a new step and frame
    
    step_1 = odb_vis.Step(name = 'Step-1', description = '', domain = TIME, timePeriod = 1.0)
    analysis_time = 0.1
    frame_1 = step_1.Frame(incrementNumber = 1, frameValue = analysis_time, description = '')
    
    # ------------------------
    # Import displacement data
    
    if u_data != []:
        u_data = tuple(u_data)
        u_field = frame_1.FieldOutput(name = 'U', description = 'Displacements.', type = VECTOR,
                                      validInvariants=(MAGNITUDE,),)
        u_field.addData(position = NODAL, 
                        instance = instance_1, 
                        labels = node_label, 
                        data = u_data)
        step_1.setDefaultDeformedField(u_field)
        odb_vis.save()
    
    # -----------------------------
    # Import strain and stress data
    
    # ---- GLOBAL COORDINATES ----
    # Strains at integration points
    if sg_strain != []:
        s_field = frame_1.FieldOutput(
            name = 'EG', 
            description = 'Strains at Gaussian points in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EG11', 'EG22', 'EG33', '2EG23', '2EG13', '2EG12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = sg_strain
            )
        odb_vis.save()
    
    # Stresses at integration points
    if sg_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SG', 
            description = 'Stresses at Gaussian points in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SG11', 'SG22', 'SG33', 'SG23', 'SG13', 'SG12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = sg_stress
            )
        odb_vis.save()
    
    # Strains at elemental nodes
    if sn_strain != []:
        e_field = frame_1.FieldOutput(
            name = 'EN', 
            description = 'Strains at nodes in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EN11', 'EN22', 'EN33', '2EN23', '2EN13', '2EN12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        e_field.addData(
            position = ELEMENT_NODAL, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = sn_strain
            )
#        step_1.setDefaultField(e_field)
        odb_vis.save()
    
    # Stresses at elemental nodes
    if sn_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SN', 
            description = 'Stresses at nodes in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SN11', 'SN22', 'SN33', 'SN23', 'SN13', 'SN12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = ELEMENT_NODAL, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = sn_stress
            )
        odb_vis.save()
    
    # ---- MATERIAL COORDINATES ----
    # Strains at integration points
    if sgm_strain != []:
        s_field = frame_1.FieldOutput(
            name = 'EGM', 
            description = 'Strains at Gaussian points in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EGM11', 'EGM22', 'EGM33', '2EGM23', '2EGM13', '2EGM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = sgm_strain
            )
        odb_vis.save()
    
    # Stresses at integration points
    if sgm_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SGM', 
            description = 'Stresses at Gaussian points in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SGM11', 'SGM22', 'SGM33', 'SGM23', 'SGM13', 'SGM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = sgm_stress
            )
        odb_vis.save()
    
    # Strains at elemental nodes
    if snm_strain != []:
        e_field = frame_1.FieldOutput(
            name = 'ENM', 
            description = 'Strains at nodes in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('ENM11', 'ENM22', 'ENM33', '2ENM23', '2ENM13', '2ENM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        e_field.addData(
            position = ELEMENT_NODAL, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = snm_strain
            )
        odb_vis.save()
    
    # Stresses at elemental nodes
    if snm_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SNM', 
            description = 'Stresses at nodes in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SNM11', 'SNM22', 'SNM33', 'SNM23', 'SNM13', 'SNM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = ELEMENT_NODAL, 
            sectionPoint = sp_bot, 
            instance = instance_1, 
            labels = elem_label, 
            data = snm_stress
            )
        odb_vis.save()
        
    return 1
    


# ==============================================================================
#
#   Visualization of 3D SG
#
# ==============================================================================

def visualization3D(odb_vis, project_name, node_coord, elem_connt_c4, elem_connt_c10, 
                    elem_connt_c8, elem_connt_c20, elem_sectn, node_label, elem_label, 
                    u_data, sg_strain, sg_stress, sn_strain, sn_stress, 
                    sgm_strain, sgm_stress, snm_strain, snm_stress):

    # -----------------------
    # Create a dummy material
    
    material_name = 'Elastic material'
    material_1 = odb_vis.Material(name = material_name)
    material_1.Elastic(type = ISOTROPIC, 
                       temperatureDependency = OFF, 
                       dependencies = 0, 
                       noCompression = OFF, 
                       noTension = OFF, 
                       moduli = LONG_TERM, 
                       table = ((12000, 0.3), ))
                       
    # -------------------------
    # Create different sections
    section_name_g = 'Homogeneous solid section'
    abq_section = {}
    for k in elem_sectn.keys():
        section_name = section_name_g + '-' + k
        abq_section[k] = odb_vis.HomogeneousSolidSection(
            name = section_name, material = material_name
            )
    
    # -----------------
    # Create a new part
    
    part_1 = odb_vis.Part(name = 'Part-1', embeddedSpace = THREE_D, type = DEFORMABLE_BODY)
    node_coord = tuple(node_coord)
    # Import nodes
    part_1.addNodes(nodeData = node_coord, nodeSetName = 'nSet-1')
    odb_vis.save()
    
#    elem_connt = tuple(elem_connt)
    # Import elements
    if elem_connt_c4 != []:
        elem_connt_c4 = tuple(elem_connt_c4)
        part_1.addElements(elementData = elem_connt_c4, type = 'C3D4', elementSetName = 'eSet-c3d4')
    if elem_connt_c10 != []:
        elem_connt_c10 = tuple(elem_connt_c10)
        part_1.addElements(elementData = elem_connt_c10, type = 'C3D10', elementSetName = 'eSet-c3d10')
    if elem_connt_c8 != []:
        elem_connt_c8 = tuple(elem_connt_c8)
        part_1.addElements(elementData = elem_connt_c8, type = 'C3D8', elementSetName = 'eSet-c3d8')
    if elem_connt_c20 != []:
        elem_connt_c20 = tuple(elem_connt_c20)
        part_1.addElements(elementData = elem_connt_c20, type = 'C3D20', elementSetName = 'eSet-c3d20')
    odb_vis.save()
    
    # ---------------------
    # Create a new instance
    
    instance_1 = odb_vis.rootAssembly.Instance(name = 'Part-1-1', object = part_1)
    for k in elem_sectn.keys():  # Assign sections to element sets
        section_name = section_name_g + ' - ' + k
        elem_sectn_label = tuple(elem_sectn[k])
        elem_set = odb_vis.rootAssembly.instances['Part-1-1'].\
            ElementSetFromElementLabels(name = section_name, elementLabels = elem_sectn_label)
        instance_1.assignSection(region = elem_set, section = abq_section[k])
    odb_vis.save()
    
    # ---------------------------
    # Create a new step and frame
    
    step_1 = odb_vis.Step(name = 'Step-1', description = '', domain = TIME, timePeriod = 1.0)
    analysis_time = 0.1
    frame_1 = step_1.Frame(incrementNumber = 1, frameValue = analysis_time, description = '')
    
    # ------------------------
    # Import displacement data
    
    if u_data != []:
        u_data = tuple(u_data)
        u_field = frame_1.FieldOutput(name = 'U', description = 'Displacements.', type = VECTOR,
                                      validInvariants=(MAGNITUDE,),)
        u_field.addData(position = NODAL, 
                        instance = instance_1, 
                        labels = node_label, 
                        data = u_data)
        step_1.setDefaultDeformedField(u_field)
        odb_vis.save()
    
    # -----------------------------
    # Import strain and stress data
    
    # ---- GLOBAL COORDINATES ----
    # Strains at integration points
    if sg_strain != []:
        s_field = frame_1.FieldOutput(
            name = 'EG', 
            description = 'Strains at Gaussian points in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EG11', 'EG22', 'EG33', '2EG23', '2EG13', '2EG12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            instance = instance_1, 
            labels = elem_label, 
            data = sg_strain
            )
        odb_vis.save()
    
    # Stresses at integration points
    if sg_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SG', 
            description = 'Stresses at Gaussian points in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SG11', 'SG22', 'SG33', 'SG23', 'SG13', 'SG12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            instance = instance_1, 
            labels = elem_label, 
            data = sg_stress
            )
        odb_vis.save()
    
    # Strains at elemental nodes
    if sn_strain != []:
        e_field = frame_1.FieldOutput(
            name = 'EN', 
            description = 'Strains at nodes in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EN11', 'EN22', 'EN33', '2EN23', '2EN13', '2EN12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        e_field.addData(
            position = ELEMENT_NODAL, 
            instance = instance_1, 
            labels = elem_label, 
            data = sn_strain
            )
#        step_1.setDefaultField(e_field)
        odb_vis.save()
    
    # Stresses at elemental nodes
    if sn_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SN', 
            description = 'Stresses at nodes in the global coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SN11', 'SN22', 'SN33', 'SN23', 'SN13', 'SN12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = ELEMENT_NODAL, 
            instance = instance_1, 
            labels = elem_label, 
            data = sn_stress
            )
        odb_vis.save()
    
    # ---- MATERIAL COORDINATES ----
    # Strains at integration points
    if sgm_strain != []:
        s_field = frame_1.FieldOutput(
            name = 'EGM', 
            description = 'Strains at Gaussian points in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('EGM11', 'EGM22', 'EGM33', '2EGM23', '2EGM13', '2EGM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            instance = instance_1, 
            labels = elem_label, 
            data = sgm_strain
            )
        odb_vis.save()
    
    # Stresses at integration points
    if sgm_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SGM', 
            description = 'Stresses at Gaussian points in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SGM11', 'SGM22', 'SGM33', 'SGM23', 'SGM13', 'SGM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = INTEGRATION_POINT, 
            instance = instance_1, 
            labels = elem_label, 
            data = sgm_stress
            )
        odb_vis.save()
    
    # Strains at elemental nodes
    if snm_strain != []:
        e_field = frame_1.FieldOutput(
            name = 'ENM', 
            description = 'Strains at nodes in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('ENM11', 'ENM22', 'ENM33', '2ENM23', '2ENM13', '2ENM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        e_field.addData(
            position = ELEMENT_NODAL, 
            instance = instance_1, 
            labels = elem_label, 
            data = snm_strain
            )
        odb_vis.save()
    
    # Stresses at elemental nodes
    if snm_stress != []:
        s_field = frame_1.FieldOutput(
            name = 'SNM', 
            description = 'Stresses at nodes in the material coordinates.', 
            type = TENSOR_3D_FULL, 
            componentLabels = ('SNM11', 'SNM22', 'SNM33', 'SNM23', 'SNM13', 'SNM12'),
            validInvariants=(MISES, TRESCA, PRESS, INV3, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL),
            )
        s_field.addData(
            position = ELEMENT_NODAL, 
            instance = instance_1, 
            labels = elem_label, 
            data = snm_stress
            )
        odb_vis.save()
        
    return 1
    