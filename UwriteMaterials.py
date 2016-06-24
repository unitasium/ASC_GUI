# -*- coding: utf-8 -*-

from utilities import *
from abaqus import *
from abaqusConstants import *
from material import *
from section import *

def writeMaterials(matDict, analysis, model_name, file):
    
    ntemp = 1
    temperature = 0
    model = mdb.models[model_name]
    for mat_name, mat_id in matDict.iteritems():
        matType = model.materials[mat_name].elastic.type
        mp = model.materials[mat_name].elastic.table[0]
        
        try :
            model.materials[mat_name].density
        except:
            print 'density is not defined in material "%s" ' % mat_name
            print 'default values density = 0.1, temperature = 0 will be used,'
            print 'which will not influence the results if analysis is not temperature related.'
            model.materials[mat_name].Density(table=((0.0, ), ))
        density = model.materials[mat_name].density.table[0][0]
        
        if analysis == 1:
            mp1sheat = model.materials[mat_name].specificHeat.table[0]
            mp1cte   = model.materials[mat_name].expansion.table[0]
            mp1      = list(mp1cte) + list(mp1sheat)
        
        if matType == ISOTROPIC:
            writeFormat(file, 'ddd', [int(mat_id), 0, ntemp])
            writeFormat(file, 'EE', [float(temperature), float(density)])
            writeFormat(file, 'EE', mp[:2])
            if analysis == 1:
                writeFormat(file, 'EE', mp1)
        elif matType == ENGINEERING_CONSTANTS:
            writeFormat(file, 'ddd', [int(mat_id), 1, ntemp])
            writeFormat(file, 'EE', [float(temperature), float(density)])
            writeFormat(file, 'EEE', mp[:3])
            writeFormat(file, 'EEE', mp[6:9])
            writeFormat(file, 'EEE', mp[3:6])
            if analysis == 1:
                writeFormat(file, 'E'*4, mp1)
        elif matType == ORTHOTROPIC:
            writeFormat(file, 'ddd', [int(mat_id), 2, ntemp])
            writeFormat(file, 'EE', [float(temperature), float(density)])
            writeFormat(file, 'E'*6, [mp[0], mp[1], mp[3], 0.0, 0.0, 0.0])
            writeFormat(file, 'E'*5, [mp[2], mp[4], 0.0, 0.0, 0.0])
            writeFormat(file, 'E'*4, [mp[5], 0.0, 0.0, 0.0])
            writeFormat(file, 'E'*3, [mp[6], 0.0, 0.0])
            writeFormat(file, 'E'*2, [mp[7], 0.0])
            writeFormat(file, 'E'*1, [mp[8]])
            if analysis == 1:
                writeFormat(file, 'E'*4, mp1)
        elif matType == ANISOTROPIC:
            writeFormat(file, 'ddd', [int(mat_id), 2, ntemp])
            writeFormat(file, 'EE', [float(temperature), float(density)])
            writeFormat(file, 'E'*6, [mp[0], mp[1], mp[3], mp[6], mp[10], mp[15]])
            writeFormat(file, 'E'*5, [mp[2], mp[4], mp[7], mp[11], mp[16]])
            writeFormat(file, 'E'*4, [mp[5], mp[8], mp[12], mp[17]])
            writeFormat(file, 'E'*3, [mp[9], mp[13], mp[18]])
            writeFormat(file, 'E'*2, [mp[14], mp[19]])
            writeFormat(file, 'E'*1, [mp[20]])
            if analysis == 1:
                writeFormat(file, 'E'*7, mp1)

    return

def checkMaterials(matDict, analysis, model_name):

    for mat_name, mat_id in matDict.iteritems():
        
        model = mdb.models[model_name]
        matType = model.materials[mat_name].elastic.type
        mp = model.materials[mat_name].elastic.table[0]
        
        try :
            model.materials[mat_name].density
        except:
            print 'density is not defined in material "%s" ' % mat_name
            print 'default values density = 0.1, temperature = 0 will be used,'
            print 'which will not influence the results if analysis is not temperature related.'
            model.materials[mat_name].Density(table=((0.0, ), ))
             
        if analysis == 1:
            try :
                model.materials[mat_name].specificHeat
            except:
                raise ValueError( 'specificHeat is not defined in material \'%s\' ' % mat_name)
                
            try :
                model.materials[mat_name].expansion
            except:
                raise ValueError( 'expansion is not defined in material \'%s\' ' % mat_name )
    return
    