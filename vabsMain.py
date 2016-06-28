from abaqus import *
from math import *
from datetime import *
from subprocess import call
from utilities import *
import os.path
import codecs
import time


def VABSMain(recover_flag, gen_inp_only, vabs_inp_name='', abq_inp_name='',
             timoshenko_flag='', thermal_flag='', trapeze_flag='',
             vlasov_flag='', curve_flag='', k='', oblique_flag='', cos='',
             model_recover='', vabs_rec_name='', vabs_inp_name2='',
             u='', c='', sf='', sm='', df='', dm='',
             gamma='', kappa='', kappa_p=''):
    
    st = datetime.now()
    print st.strftime("%m-%d-%Y %H:%M:%S")

    if recover_flag == 1:
        vabs_input = getVABSInput(
            vabs_inp_name, abq_inp_name, timoshenko_flag, thermal_flag,
            trapeze_flag, vlasov_flag, curve_flag, k, oblique_flag, cos
        )
    # elif recover_flag == 2:

    if not gen_inp_only:
        try:
            vabsTimeStart = time.clock()
            os.system('VABS ' + vabs_input)
            vabsTimeEnd = time.clock()
            vabsTime = vabsTimeEnd - vabsTimeStart
            print 'VABS TIME: ' + str(vabsTime)
        except:
            raise WindowsError(
                'Unexpected error happened. Please check the Command line window for more information.'
            )

    return 1


def getVABSInput(vabs_inp_name, abq_inp_name, timoshenko_flag, thermal_flag,
                 trapeze_flag, vlasov_flag, curve_flag, ik, oblique_flag, cos):

    if vabs_inp_name == '':
        out_file_name = abq_inp_name[:-4] + r'_vabs.dat'
    else:
        if not '.dat' in vabs_inp_name:
            vabs_inp_name = vabs_inp_name + '.dat'
        dr = os.path.dirname(abq_inp_name)
        out_file_name = os.path.join(dr, vabs_inp_name)

    if timoshenko_flag:
        timoshenko_flag = 1
    else:
        timoshenko_flag = 0

    if thermal_flag:
        thermal_flag = 3
    else:
        thermal_flag = 0

    if trapeze_flag:
        trapeze_flag = 1
    else:
        trapeze_flag = 0

    if vlasov_flag:
        vlasov_flag = 1
    else:
        vlasov_flag = 0

    if curve_flag:
        curve_flag = 1
    else:
        curve_flag = 0

    if oblique_flag:
        oblique_flag = 1
    else:
        oblique_flag = 0

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
                '*Distribution', '*Solid Section',
                '*Shell Section', '*Material', '*Density', '*Elastic']
    
    milestone('Reading Abaqus inputs...')
    
    with open(abq_inp_name, 'r') as fin:
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
                elif first.startswith('*') and first not in keywords:
                    key = ''
                    continue
                elif first == '*Node':
                    key = 'node'
                    continue
                elif first == '*Element':
                    key = 'element'
                    continue
                elif first == '*Elset':
                    key = 'elset'
                    for i, temp in enumerate(line):
                        if 'elset' in temp:
                            ei = i
                        if 'generate' in temp:
                            parameter = 'generate'
                        else:
                            parameter = 'list'
                    elset = line[ei].split('=')
                    name = elset[-1]  # Abaqus element set name
                    ma = name.split('/')
                    ma = ma[0]
                    if ma not in abq_elset.keys():
                        abq_elset[ma] = []
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
                        try:
                            a = float(a)
                            layer_type[ma] = [k, m, a]
                            # {'name': [id, 'material', angle], ...}
                        except ValueError:
                            continue
                    continue
                elif first == '*Distribution':
                    key = 'distribution'
                    continue
                elif first == '*Solid Section' or first == '*Shell Section':
                    key = ''
                    for i, temp in enumerate(line):
                        if 'elset' in temp:
                            ei = i
                    elset = line[ei].split('=')
                    elset = elset[-1]
                    ma = elset.split('/')
                    ma = ma[0]
                    used_section.append(ma)
                elif first == '*Material':
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
                    key = 'density'
                    continue
                elif first == '*Elastic':
                    if len(material[mn]) < 2:    # no density
                        material[mn].append(1.0) # add default density
                    key = 'elastic'
                    tp = 'ISOTROPIC'
                    for temp in line:
                        if 'type' in temp:
                            tp = temp.split('=')[-1].strip()
                    material[mn].append(material_type[tp])
                    continue
                
                # Save data
                if key == '':
                    continue
                elif key == 'node':
                    nid = int(first)
                    x2 = float(line[2].strip())
                    x3 = float(line[3].strip())
                    n_coord.append([nid, x2, x3])
                elif key == 'element':
                    n = len(line) - 1  # number of nodes
                    if n == 3 or n == 6:
                        line.insert(4, '0')
                    m = len(line) - 1
                    zeros = [0] * (9 - m)
                    eid = line[0].strip()
                    e_connt[eid] = [int(v.strip()) for v in line[1:]]
                    # {'eid': [n1, n2, ...], ...}
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
                            abq_elset[ma].append(e)
                            # Abaqus: {'set_name': [e1, e2, ...], ...}
                elif key == 'distribution':
                    eid = str(line[0].strip())
                    if int(eid) in e_list:
                        e_list.remove(int(eid))
                    if eid not in distr_list.keys():
                        distr_list[eid] = [
                            1.0, 0.0, 0.0,  # a_1, a_2, a_3
                            float(line[1]), float(line[2]), float(line[3]),  # b_1, b_2, b_3
                            0.0, 0.0, 0.0  # c_1, c_2, c_3
                        ]
                        # {'element_id': [a_1, ..., c_3], }
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

    # for k, v in e_connt.items():
    #     maid = eid_maid[k]
    #     v.insert(0, maid)
    
#    print 'Writing SwiftComp inputs...'
    milestone('Writing VABS inputs...')
    with codecs.open(out_file_name, encoding='utf-8', mode='w') as fout:
        nnode = len(n_coord)
        nelem = len(e_connt)
        nmate = len(material)
        nlayer = len(layer_type)

        # format_flag  nlayer
        writeFormat(fout, 'dd', [1, nlayer])
        fout.write('\n')

        # timoshenko_flag  recover_flag  thermal_flag
        writeFormat(fout, 'ddd',
                    [timoshenko_flag, 0, thermal_flag])
        fout.write('\n')

        # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
        writeFormat(fout, 'd'*4,
                    [curve_flag, oblique_flag, trapeze_flag, vlasov_flag])
        fout.write('\n')

        if curve_flag == 1:
            writeFormat(fout, 'EEE', ik[0])
            fout.write('\n')

        if oblique_flag == 1 and timoshenko_flag == 0:
            writeFormat(fout, 'EE', cos[0])
            fout.write('\n')

        # nnode  nelem  nmate
        writeFormat(fout, 'ddd', [nnode, nelem, nmate])
        fout.write('\n')

        for n in n_coord:
            writeFormat(fout, 'dEE', n)
        fout.write('\n')

        for k, v in e_connt.items():
            e = [int(k), ] + v
            writeFormat(fout, 'd'*10, e)
        fout.write('\n')

        for e in e_list:
            ma = eid_maid[str(e)]
            writeFormat(fout, 'ddE', [int(e), ma, 0.0])
        for e, abc in distr_list.items():
            ma = eid_maid[str(e)]
            t1 = degrees(atan2(abc[5], abc[4]))  # b3, b2
            if t1 < 0:
                t1 += 360.0
            if t1 == 360.0:
                t1 = 0.0
            writeFormat(fout, 'ddE', [int(e), ma, t1])
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
                # material_id  isotropy
                writeFormat(fout, 'dd', [i[0], i[2]])
                if i[2] == 0:  # isotropic
                    writeFormat(fout, 'EE', i[3:5])
                elif i[2] == 1:  # engineering constants
                    writeFormat(fout, 'EEE', i[3:6])
                    writeFormat(fout, 'EEE', i[9:12])
                    writeFormat(fout, 'EEE', i[6:9])
                elif i[2] == 2:
                    if len(i) == 12:   # orthotropic
                        c1111 = i[3]
                        c1122 = i[4]
                        c2222 = i[5]
                        c1133 = i[6]
                        c2233 = i[7]
                        c3333 = i[8]
                        c1212 = i[9]
                        c1313 = i[10]
                        c2323 = i[11]
                        writeFormat(fout, 'E'*6,
                                    [c1111,     0,     0, c1122,     0, c1133])
                        writeFormat(fout, 'E'*5,
                                    [       c1212,     0,     0,     0,     0])
                        writeFormat(fout, 'E'*4,
                                    [              c1313,     0,     0,     0])
                        writeFormat(fout, 'E'*3,
                                    [                     c2222,     0, c2233])
                        writeFormat(fout, 'E'*2,
                                    [                            c2323,     0])
                        writeFormat(fout, 'E'*1,
                                    [                                   c3333])
                    elif len(i) == 24:  # anisotropic
                        c1111, c1122, c2222 = i[3], i[4], i[5]
                        c1133, c2233, c3333 = i[6], i[7], i[8]
                        c1112, c2212, c3312 = i[9], i[10], i[11]
                        c1212, c1113, c2213 = i[12], i[13], i[14]
                        c3313, c1213, c1313 = i[15], i[16], i[17]
                        c1123, c2223, c3323 = i[18], i[19], i[20]
                        c1223, c1323, c2323 = i[21], i[22], i[23]
                        writeFormat(fout, 'E'*6,
                                    [c1111, c1112, c1113, c1122, c1123, c1133])
                        writeFormat(fout, 'E'*5,
                                    [       c1212, c1213, c2212, c1223, c3312])
                        writeFormat(fout, 'E'*4,
                                    [              c1313, c2213, c1323, c3313])
                        writeFormat(fout, 'E'*3,
                                    [                     c2222, c2223, c2233])
                        writeFormat(fout, 'E'*2,
                                    [                            c2323, c3323])
                        writeFormat(fout, 'E'*1,
                                    [                                   c3333])
                writeFormat(fout, 'E', [i[1]])
                fout.write('\n')
            fout.write('\n')

    vabs_input = os.path.basename(out_file_name)

    return vabs_input
