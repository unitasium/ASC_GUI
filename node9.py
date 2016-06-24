# -*- coding: utf-8 -*-

from abaqus import *
import numpy as np

def generateNode9(abaqus_inp):
    
    new_abaqus_inp = abaqus_inp[:-4] + r'_9n.inp'
    
    inp = []
    node = {}
    element = {}
    nelem_8n = 0
    
    milestone('Reading Abaqus input file...')
    with open(abaqus_inp, 'r') as fin:
        for i, line in enumerate(fin):
            line = line.strip()
            inp.append(line)
            if line.startswith('*Node'):
                key = 'n'
                node_start = i + 1
                continue
            elif line.startswith('*Element'):
                key = 'e'
                element_start = i + 1
                inp.remove(inp[-1])
                inp.append('*Element')
                continue
            elif line.startswith('*'):
                key = ''
                continue
             
            if key == 'n':
                line = line.split(',')
                nid = int(line[0])
                node[nid] = [float(line[1]), float(line[2])]
                try:
                    node[nid].append(float(line[3]))
                    dimension = 3
                except IndexError:
                    dimension = 2
                    pass
            elif key == 'e':
                inp.remove(inp[-1])
                line = line.split(',')
                if len(line) == 9:
                    nelem_8n += 1
                eid = int(line[0])
                element[eid] = []
                for n in line[1:]:
                    element[eid].append(int(n))
            
    nnode_old = len(node)
    nelem = len(element)
    
#    node_extra = {}
#    element_n9 = {}
    
    n9 = nnode_old
    nelem_9n = 0
    
    for eid in range(1, nelem+1):
        nodes = element[eid]
        if len(nodes) == 8:
            nelem_9n += 1
            milestone('Generating 9-node elements', 'element', nelem_9n, nelem_8n)
            n9 += 1
            x, y, z = [], [], []
            for nid in nodes:
                x.append(node[nid][0])
                y.append(node[nid][1])
                if dimension == 3:
                    z.append(node[nid][2])
            x9 = np.mean(x)
            y9 = np.mean(y)
            node[n9] = [x9, y9]
            if dimension == 3:
                z9 = np.mean(z)
                node[n9].append(z9)
            element[eid].append(n9)
        else:
            continue
        
    milestone('Writing new Abaqus input file...')
    with open(new_abaqus_inp, 'w') as fout:
        for i, l in enumerate(inp):
            if i == node_start + nnode_old:
                for nid in range(nnode_old+1, len(node)+1):
                    fout.write('{0:8d},{1:15f},{2:15f}'.format(nid, node[nid][0], node[nid][1]))
                    if dimension == 3:
                        fout.write(',{0:15f}\n'.format(node[nid][2]))
            if l == '*Element':
                fout.write('*Element, type=S9R5\n')
                for eid in range(1, nelem+1):
                    fout.write('{0:8d}'.format(eid))
                    for n in element[eid]:
                        fout.write(',{0:7d}'.format(n))
                    fout.write('\n')
                continue
            
            fout.write(l)
            fout.write('\n')
    