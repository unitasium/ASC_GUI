# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
import section
import xml.etree.ElementTree as et

def addLayups(method,
              fg_model_name = '', fg_material_name = '', fg_section_name = '', fg_layup = '', fg_ply_thickness = 0.0, 
              rf_model_name = '', rf_section_name = '', rf_material_file = '', rf_layup_file = ''):
    
    if method == 1:
        fastGenerate(fg_model_name, fg_material_name, fg_section_name, fg_layup, fg_ply_thickness)
    elif method == 2:
        mid_name = readMaterialFile(rf_model_name, rf_material_file)
        readLayupFile(rf_model_name, rf_layup_file, mid_name)
        
    return 1
    

def fastGenerate(model_name, material_name, section_name, layup, ply_thickness):

    #### get reduced string without '2s'
    model = mdb.models[model_name]

    mid = layup.find(']')
    rr = layup[:mid]            ## truncated string rr
    
    rr = rr.replace('[',' ')
    rr = rr.replace('/',' ')
    rr = rr.replace('\\',' ')
    #--------------
    
    layup_s = rr.split()   ## list of angles

    #### get reduced string without '2s'
    qq = layup[mid+1:].lower()
    s_exist = qq.find('s') 
    
    if s_exist != -1:
        symm = True        #symmetric
        try:
            times = int(qq[:s_exist])
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

    if symm:
        half0 = layup_s * times
        half1 = half0[:]
        half1.reverse()
        layup_ori = half0 + half1
    else:
        layup_ori = layup_s * times

    section_layer = []
    for a in layup_ori:
        sl = section.SectionLayer(material = material_name, thickness = ply_thickness, 
                                  orientAngle = float(a))
        section_layer.append(sl)
    model.CompositeSolidSection(name = section_name, layup = tuple(section_layer))
    
    return 1
    
    
def readMaterialFile(model_name, file_name):
    
    model = mdb.models[model_name]
    tree = et.parse(file_name)
    mtr_root = tree.getroot()
    
    mid_name = {}
#    mname_id = {}

    for mtr in mtr_root:
        material_id   = int(mtr.find('id').text)
        material_name = mtr.find('name').text
        material_type = mtr.get('type')
        density = mtr.find('density')
        mid_name[material_id] = material_name
#        mname_id[material_name] = material_id
        m = model.Material(name = material_name)
        if not density == None:
            dens = float(density.text)
            m.Density(table = ((dens,),))
        if material_type == 'ISOTROPIC':
            e = float(mtr.find('e').text)
            nu = float(mtr.find('nu').text)
            prop = ((e, nu),)
            m.Elastic(type = ISOTROPIC, table = prop)
#            sn = material_name + '_0.0'
#            model.HomogeneousSolidSection(name = sn, material = material_name, thickness = None)
        elif material_type == 'ENGINEERING CONSTANTS':
            e1 = float(mtr.find('e1').text)
            e2 = float(mtr.find('e2').text)
            e3 = float(mtr.find('e3').text)
            g12 = float(mtr.find('g12').text)
            g13 = float(mtr.find('g13').text)
            g23 = float(mtr.find('g23').text)
            nu12 = float(mtr.find('nu12').text)
            nu13 = float(mtr.find('nu13').text)
            nu23 = float(mtr.find('nu23').text)
            prop = ((e1, e2, e3, nu12, nu13, nu23, g12, g13, g23),)
            m.Elastic(type = ENGINEERING_CONSTANTS, table = prop)
        
    
    return mid_name
    

def readLayupFile(model_name, file_name, mid_name):
    
    model = mdb.models[model_name]
    
    tree_layup = et.parse(file_name)
    root_layup = tree_layup.getroot()
    
    for layup in root_layup:
        section_layer = []
        lyp_name = layup.find('name').text
        lyp_data = layup.find('data').text
        lyp_data = lyp_data.strip().split('\n')
        for l in lyp_data:
            l = l.split()
            [thk, mid, ora] = [float(l[0]), int(l[1]), float(l[2])]
            mname = mid_name[mid]
            sl = section.SectionLayer(material = mname, thickness = thk, 
                                      orientAngle = ora)
            section_layer.append(sl)
        model.CompositeSolidSection(name = lyp_name, layup = tuple(section_layer))
    
#    mat_abq = model.materials.keys()
#
#    # ------------------------------------
#    # Read layup data from layup input file
#    plies_sc={}
#    mat_dict={}
#    parameter_line = [1]
#    sym_flag='n'
#    offset_ratio=0.0
#    i = 1
#    j = 0
#    print '--> Reading Layup input file...'
#    
#    with open(file_name, 'r') as fin:
#        for line in fin:
#            line = line.strip()
#            if line == '\n' or line == '':
#                continue
#            else:
#                line = line.split()
#                if i == parameter_line[-1]:
#                    n_ply = int(line[0])              # Read the number of plies
#                    nmat = int(line[1])            # Read the number of materials
#                    if len(line) <= 4:
#                        sym_flag = line[2].lower()             # Read if the layup should be symmetrical or antisymmetric ( n, sym, antisym)
#                    if len(line) == 4:
#                        offset_ratio = float(line[3])            # Read the offset_ratio
#                    i += 1
#                elif j <= (n_ply-1):                    # construct plies_sc  {'ply_id_sc':}
#                    ply_id_sc = j        #  the key of plies_sc[ply_id_sc] begin at 0.
#                    plies_sc[ply_id_sc] = (float(line[0]), float(line[1]), int(line[2]) )   # thickness, orientation, mat_id
#                    if sym_flag[0] == 's':
#                        ply_id_sc_s = 2*n_ply-1 - ply_id_sc
#                        plies_sc[ply_id_sc_s] = plies_sc[ply_id_sc]
#                    elif sym_flag[0] == 'a' and ply_id_sc != (n_ply-1):
#                        ply_id_sc_a = 2*(n_ply-1) - ply_id_sc
#                        plies_sc[ply_id_sc_a] = plies_sc[ply_id_sc]
#                    j += 1
#                elif j <= (n_ply-1 + nmat):          # Read element connectivities
#                    mat_id = int(line[0])
#                    mat_name = str(line[1])
#                    mat_dict[mat_id] = mat_name
#                    if mat_name not in mat_abq:
#                        raise ValueError('material \'%s \' is not existed in model \'%s\'.' %(mat_name, model_name))
#                    j+=1
#    
#    if len(mat_dict) != nmat:
#        raise ValueError('The material types existed in the layup is not equal to the number of materials specified!')
#    
#    
#    n_ply = len(plies_sc)
#    
#    layup_t=[]
#    layup_ori=[]
#    t_total=0.0
#    layup_mat=[]
#    for ply_id in range(n_ply) :
#        ply_t = plies_sc[ply_id][0]
#        t_total = t_total+ply_t
#        layup_t.append(ply_t)
#        layup_ori.append(plies_sc[ply_id][1])
#        mat_id = plies_sc[ply_id][2]
#        mat_name = mat_dict[mat_id]
#        layup_mat.append(mat_name)
#    
#    section_layer = []
#    for i in range(n_ply):
#        sl = section.SectionLayer(material = layup_mat[i], thickness = layup_t[i], 
#                                  orientAngle = layup_ori[i])
#        section_layer.append(sl)
#    model.CompositeSolidSection(name = section_name, layup = tuple(section_layer))
#    
#    return 1
    
    