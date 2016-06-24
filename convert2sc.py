# -*- coding: utf-8 -*-

from abaqus import *
from math import *
import codecs
from utilities import *
import os.path


def convert2sc(abq_input, new_filename, macro_model, specific_model,
               analysis, elem_flag, trans_flag, temp_flag,
               bk, sk, cos, w):

    if new_filename == '':
        out_file_name = abq_input[:-4] + r'.sc'
    else:
        dir = os.path.dirname(abq_input)
        new_filename = new_filename + '.sc'
        out_file_name = os.path.join(dir, new_filename)
    
    nsg    = 1
    nslave = 0
    
    n_coord      = []
    e_connt      = {}
    e_list       = []
    abq_elset    = {}
    layer_type   = {}
    distribution = {}
    distr_list   = {}
    orientation  = {}
    section      = {}
    material     = {}
    used_section = []
    
    material_type = {'ISOTROPIC': 0, 'ENGINEERING CONSTANTS': 1, 
                     'ORTHOTROPIC': 2, 'ANISOTROPIC': 2}
    
    keywords = ['*Node', '*Element', '*Elset', 
                '*Distribution', '*Orientation', '*Solid Section', '*Shell Section', 
                '*Material', '*Density', '*Elastic']
    
    milestone('Reading Abaqus inputs...')
    
    with open(abq_input, 'r') as fin:
        key = ''
        name = ''
        parameter = ''
    
        for line in fin:
            line = line.strip()
            if line.startswith('**'):
                continue
            else:
                line = line.split(',')
                first = line[0].strip()
                # Switch key
                if first == '':
                    continue
                elif first.startswith('*') and not first in keywords:
                    key = ''
                    continue
                elif first == '*Node':
#                    milestone(first)
                    key = 'node'
                    continue
                elif first == '*Element':
#                    milestone(first)
                    key = 'element'
                    continue
                elif first == '*Elset':
#                    milestone(first)
                    key = 'elset'
                    for i, temp in enumerate(line):
                        if 'elset' in temp:
                            ei = i
                        if 'generate' in temp:
                            parameter = 'generate'
                        else:
                            parameter = 'list'
                    elset = line[ei].split('=')
                    name  = elset[-1]                                        # Abaqus element set name
                    ma = name.split('/')
                    ma = ma[0]
#                    print ma
#                    print abq_elset
                    if ma not in abq_elset.keys():
                        abq_elset[ma] = []
    #                else:
    #                    flag = 1
                    if ma not in layer_type.keys():
                        k = len(layer_type.keys()) + 1
                        j = ma.rfind('_')
                        m = ma[:j]
                        a = ma[j+1:]
                        if 'p' in a:
                            a = a[1:]
                        elif 'n' in a:
                            a = a.replace('n', '-')
                        a = a.replace('d', '.')
    #                    print a
                        try:
                            a = float(a)
                            layer_type[ma] = [k, m, a]                       # {'name': [id, 'material', angle], ...}
                        except ValueError:
                            continue
                    continue
                elif first == '*Distribution':
#                    milestone(first)
                    distr_flag = 'exist'
                    distr_eab = {}
                    for temp in line:
                        if 'name' in temp:
                            distr_name = temp.split('=')[-1].strip()
                            if not distr_name in distribution.keys():
                                distribution[distr_name] = [distr_eab]
                                distr_flag = 'new'
                        if 'Table' in temp and distr_flag == 'new':
                            distr_table = temp.split('=')[-1].strip()
                            distribution[distr_name].insert(0, distr_table)
                    key = 'distribution'
                    continue
                elif first == '*Orientation':
                    orien_flag = 'exist'
                    row = 1
                    for temp in line:
                        if 'name' in temp:
                            orien_name = temp.split('=')[-1].strip()
                            if not orien_name in orientation.keys():
                                orientation[orien_name] = []
                                orien_flag = 'new'
                    key = 'orientation'
                    continue
                elif first == '*Solid Section' or first == '*Shell Section':
#                    milestone(first)
                    key = ''
                    for temp in line:
                        if 'elset' in temp:
                            elset_name = temp.split('=')[-1].strip()
                            ma = elset_name.split('/')[0]
                            used_section.append(ma)
                            section[elset_name] = {}
                        elif 'orientation' in temp:
                            orien_name = temp.split('=')[-1].strip()
                            section[elset_name]['orientation'] = orien_name
                        elif 'material' in temp:
                            mtr_name = temp.split('=')[-1].strip()
                            section[elset_name]['material'] = mtr_name
#                    print used_section
                elif first == '*Material':
#                    milestone(first)
                    key = ''
                    for i, temp in enumerate(line):
                        if 'name' in temp:
                            mi = i
                    mn = line[mi].split('=')
                    mn = mn[-1].strip()
                    if mn not in material.keys():
                        mid = len(material.keys()) + 1
                        material[mn] = [mid]
                    continue
                elif first == '*Density':
#                    milestone(first)
                    key = 'density'
                    continue
                elif first == '*Elastic':
#                    milestone(first)
                    if len(material[mn]) < 2:    # no density
                        material[mn].append(1.0) # add default density
                    key = 'elastic'
                    tp = 'ISOTROPIC'
                    for temp in line:
                        if 'type' in temp:
                            tp = temp.split('=')[-1].strip()
                    material[mn].append(material_type[tp])
#                    material[mn].append(density)
                    continue
                
                
                # Save data
                if key == '':
                    continue
                elif key == 'node':
                    nid = int(first)
                    if len(line) == 3:
                        x2 = float(line[1].strip())
                        x3 = float(line[2].strip())
                        try:
                            if nsg != 2:
                                if x2 != x2_old and x3 != x3_old:
                                    nsg = 2
                                    i2, i3 = 1, 2
                                else:
                                    nsg = 1
                                    if x2 != x2_old:
                                        i3 = 1
                                    elif x3 != x3_old:
                                        i3 = 2
                        except NameError:
                            pass
                        n_coord.append([nid, x2, x3])
                        x2_old, x3_old = x2, x3
                    elif len(line) == 4:
                        x1 = float(line[1].strip())
                        x2 = float(line[2].strip())
                        x3 = float(line[3].strip())
                        try:
                            if nsg != 3:
                                if x1 != x1_old and x2 != x2_old and x3 != x3_old:
                                    nsg = 3
                                    i1, i2, i3 = 1, 2, 3
                                if nsg != 2:
                                    if x1 != x1_old and x2 != x2_old:
                                        nsg = 2
                                        i2, i3 = 1, 2
                                    elif x2 != x2_old and x3 != x3_old:
                                        nsg = 2
                                        i2, i3 = 2, 3
                                    elif x3 != x3_old and x1 != x1_old:
                                        nsg = 2
                                        i2, i3 = 3, 1
                                    else:
                                        nsg = 1
                                        if x1 != x1_old:
                                            i3 = 1
                                        elif x2 != x2_old:
                                            i3 = 2
                                        elif x3 != x3_old:
                                            i3 = 3
                        except NameError:
                            pass
                        n_coord.append([nid, x1, x2, x3])                       # [[node_id, 0.0, x_2, x_3], ...]
                        x1_old, x2_old, x3_old = x1, x2, x3
                elif key == 'element':
                    n = len(line) - 1  # number of nodes
                    if n == 3 or n == 6:
                        line.insert(4, '0')
                    m = len(line) - 1
                    zeros = [0] * (9 - m)
                    eid = line[0].strip()
                    e_connt[eid] = [int(v.strip()) for v in line[1:]]             # {'eid': [n1, n2, ...], ...}
                    e_connt[eid] += zeros
                    e_list.append(int(eid))
                elif key == 'elset':
                    if parameter == 'list':
                        for e in line:
                            if e.strip() == '':
                                continue
                            abq_elset[ma].append(int(e.strip()))
                    elif parameter == 'generate':
                        start = int(line[0].strip())
                        stop = int(line[1].strip()) + 1
                        step = int(line[2].strip())
                        for e in range(start, stop, step):
                            abq_elset[ma].append(e)                              # Abaqus: {'set_name': [e1, e2, ...], ...}
                elif key == 'distribution':
                    if distr_flag == 'new':
                        eid = str(line[0].strip())
        #                print eid
                        if int(eid) in e_list:
                            e_list.remove(int(eid))
                        if eid not in distr_list.keys():
                            if nsg == 2:
                                distr_list[eid] = [1.0, 0.0, 0.0,                        # a_1, a_2, a_3
                                                   float(line[1]), float(line[2]), float(line[3]),  # b_1, b_2, b_3
                                                   0.0, 0.0, 0.0]                        # c_1, c_2, c_3
                                                                                         # {'element_id': [a_1, ..., c_3], }
                            elif nsg == 3:
                                distr_list[eid] = [float(line[1]), float(line[2]), float(line[3]), 
                                                   float(line[4]), float(line[5]), float(line[6]),
                                                   0.0, 0.0, 0.0]
                        distr_eab = distribution[distr_name][-1]
                        if nsg == 2:
                            distr_eab[eid] = [1.0, 0.0, 0.0,                        # a_1, a_2, a_3
                                              float(line[1]), float(line[2]), float(line[3]),  # b_1, b_2, b_3
                                              0.0, 0.0, 0.0]                        # c_1, c_2, c_3
                        elif nsg == 3:
                            distr_eab[eid] = [float(line[1]), float(line[2]), float(line[3]),  # a_1, a_2, a_3
                                              float(line[4]), float(line[5]), float(line[6]),  # b_1, b_2, b_3
                                              0.0, 0.0, 0.0]                        # c_1, c_2, c_3
                elif key == 'orientation':
                    if orien_flag == 'new':
                        if row == 1:
                            try:
                                ab = []
                                for i in line:
                                    ab.append(float(line[0].strip()))
                                orientation[orien_name].append('ab')
                                orientation[orien_name].append(ab)
                            except ValueError:
                                orientation[orien_name].append('distr')
                                orientation[orien_name].append(line[0])
                            row += 1
                        elif row == 2:
                            orientation[orien_name].append(int(line[0]))
                            orientation[orien_name].append(float(line[1]))
                elif key == 'density':
                    d = float(line[0])
#                    print material
                    material[mn].append(d)
                elif key == 'elastic':
                    for p in line:
                        if p.strip() != '':
                            material[mn].append(float(p.strip()))
    #                print material[mn]
    
#    print distribution
#    print orientation
#    print section
    
#    print 'Finish reading Abaqus inputs.'
    nlayer = len(layer_type)
    nmate  = len(material)
    
    for k in abq_elset.keys():
        if k not in used_section:
            del abq_elset[k]
    
    eid_maid = {}
#    print abq_elset
    for k, v in abq_elset.items():
        maid = layer_type[k][0]
        for eid in v:
            eid_maid[str(eid)] = maid
            
#    print eid_maid

    for k, v in e_connt.items():
        maid = eid_maid[k]
        v.insert(0, maid)
    
#    print 'Writing SwiftComp inputs...'
    milestone('Writing SwiftComp inputs...')
    with codecs.open(out_file_name, encoding = 'utf-8', mode = 'w') as fout:
        nnode = len(n_coord)
        nelem = len(e_connt)
        if macro_model == 1:
            writeFormat(fout, 'd', [specific_model])
            fout.write('\n')
            writeFormat(fout, 'EEE', bk)
            fout.write('\n')
            writeFormat(fout, 'EE', cos)
            fout.write('\n')
        elif macro_model == 2:
            writeFormat(fout, 'd', [specific_model])
            fout.write('\n')
            writeFormat(fout, 'EE', sk)
            fout.write('\n')
        writeFormat(fout, 'd'*4, [analysis, elem_flag, trans_flag, temp_flag])
        fout.write('\n')
        writeFormat(fout, 'd'*6, [nsg, nnode, nelem, nmate, nslave, nlayer])
        fout.write('\n')
    
        for n in n_coord:
            if nsg == 1:
                writeFormat(fout, 'dE', [n[0], n[i3]])
            elif nsg == 2:
                writeFormat(fout, 'dEE', [n[0], n[i2], n[i3]])
            elif nsg == 3:
                writeFormat(fout, 'dEEE', [n[0], n[i1], n[i2], n[i3]])
        fout.write('\n')
    
        for k, v in e_connt.items():
            e = [int(k),] + v
            writeFormat(fout, 'd'*11, e)
        fout.write('\n')
    
        if trans_flag == 1:
            for e in e_list:
                a = [1.0, 0.0, 0.0]
                b = [0.0, 1.0, 0.0]
                c = [0.0, 0.0, 0.0]
                writeFormat(fout, 'd'+'E'*9, [e]+a+b+c)
            for e, abc in distr_list.items():
                writeFormat(fout, 'd'+'E'*9, [int(e)]+abc)
        fout.write('\n')
            
        if nlayer != 0:
            for v in layer_type.values():
                mn = v[1]
                mid = material[mn][0]
                v[1] = mid
                writeFormat(fout, 'ddE', v)
            fout.write('\n')
        
        if nmate != 0:
            for i in material.values():
                writeFormat(fout, 'ddd', [i[0], i[2], 1])
                writeFormat(fout, 'EE', [20.0, i[1]])
                if i[2] == 0:  # isotropic
                    writeFormat(fout, 'EE', i[3:5])
                elif i[2] == 1:  # engineering constants
                    writeFormat(fout, 'EEE', i[3:6])
                    writeFormat(fout, 'EEE', i[9:12])
                    writeFormat(fout, 'EEE', i[6:9])
                elif i[2] == 2:
                    if len(i) == 12:   # orthotropic
                        writeFormat(fout, 'E'*6, [i[3], i[4], i[6],     0,     0,     0])
                        writeFormat(fout, 'E'*5, [      i[5], i[7],     0,     0,     0])
                        writeFormat(fout, 'E'*4, [            i[8],     0,     0,     0])
                        writeFormat(fout, 'E'*3, [                  i[11],     0,     0])
                        writeFormat(fout, 'E'*2, [                         i[10],     0])
                        writeFormat(fout, 'E'*1, [                                 i[9]])
                    elif len(i) == 24: # anisotropic
                        writeFormat(fout, 'E'*6, [i[3], i[4], i[6], i[18], i[13],  i[9]])
                        writeFormat(fout, 'E'*5, [      i[5], i[7], i[19], i[14], i[10]])
                        writeFormat(fout, 'E'*4, [            i[8], i[20], i[15], i[11]])
                        writeFormat(fout, 'E'*3, [                  i[23], i[22], i[21]])
                        writeFormat(fout, 'E'*2, [                         i[17], i[16]])
                        writeFormat(fout, 'E'*1, [                                i[12]])
                fout.write('\n')
            fout.write('\n')
    
        writeFormat(fout, 'E', [w])
        fout.write('\n')
        
    sc_input = os.path.basename(out_file_name)
    macro_model_dim = str(macro_model) + 'D'
    
    return [sc_input, macro_model_dim]
