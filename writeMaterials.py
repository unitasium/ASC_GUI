# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 12:52:35 2016

@author: peng69
"""
from utilities import *

def writeMaterials(matDict, analysis, model_name, file):
    
    model=mdb.models[model_name]
#    file = open(file_name+'.sc','w')
    for mat_name, mat_id in matDict.iteritems():
        matType = model.materials[mat_name].elastic.type
        mp = model.materials[mat_name].elastic.table[0]
        
        try :
            model.materials[mat_name].density
            
        except:
            #print 'density is not defined in materials {:s} '.format(str(matName))
            print 'density is not defined in material "%s" ' % mat_name
            print 'default values density=0.1, temperature=0 will be used,'
            print 'which will not influence the results if analysis is not temperature related.'
            model.materials[mat_name].Density(table=((0.1, ), ))
        density=model.materials[mat_name].density.table[0][0]
             
             
        if analysis==1:
            
            try :
                model.materials[mat_name].specificHeat
            except:
                print 'specificHeat is not defined in material \'%s\' ' % mat_name
                print 'default value 0.1 will be used, please specify correct value in material module.'
                model.materials[mat_name].SpecificHeat(table=((0.1, ), ))
            mp1sheat = model.materials[mat_name].specificHeat.table[0]
                
            try :
                model.materials[mat_name].expansion
            except:
                print 'expansion is not defined in material \'%s\' ' % mat_name
                print 'default value will be used, please specify it in material module.'
                if matType == ISOTROPIC:
                    model.materials[mat_name].Expansion(table=((1.0, ), ))
                elif matType == ENGINEERING_CONSTANTS or matType == ORTHOTROPIC :
                    model.materials[mat_name].Expansion(type=ORTHOTROPIC, table=((1.0, 2.0, 3.0), ))
                elif matType == ANISOTROPIC:
                    model.materials[mat_name].Expansion(type=ANISOTROPIC, table=((1.0, 2.0, 3.0, 4.0, 5.0, 6.0), ))
            mp1cte = model.materials[mat_name].expansion.table[0]
                
                mp1=list(mp1cte)+ list(mp1sheat)
                
        if matType == ISOTROPIC:
            writeFormat(file, 'ddd', [int(mat_id), 0, ntemp])
            riteFormat(file, 'EE', [float(temperature), float(density)])
            writeFormat(file, 'EE', mp[:2])
            if analysis==1:
                writeFormat(file, 'EE', mp1)
            
        elif matType == ENGINEERING_CONSTANTS:
            writeFormat(file, 'ddd', [int(mat_id), 1, ntemp])
            writeFormat(file, 'EE', [float(temperature), float(density)])
            writeFormat(file, 'EEE', mp[:3])
            writeFormat(file, 'EEE', mp[6:9])
            writeFormat(file, 'EEE', mp[3:6])
            if analysis==1:
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
            if analysis==1:
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
            if analysis==1:
                writeFormat(file, 'E'*7, mp1)
    
    
    
    return
    