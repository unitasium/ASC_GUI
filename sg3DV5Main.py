# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
from sg3Dparticle_V5 import *
import regionToolset



def create3DV5SG(profile,fiber_flag,vf_f,interface_flag,t_interface,modelName,fiber_matname,matrix_matname,interface_matname,mesh_size,elem_type):


    
    #Create the model
    model_name = modelName
    if profile == 1:
        #-----------
#        modelobj = mdb.models
#        nmodel = len(modelobj)
#        
#        if model_name in modelobj.keys():
#            print 'The model "squreUF" has existed, "squreUF_new" will be created.'
#            model_name = model_name + '_new'
#            #mdb.Model(name=model_name, objectToCopy=mdb.models[modelName])
#            mdb.Model(name=model_name, modelType=STANDARD_EXPLICIT)
##            model = mdb.models[model_name]
#        else:
#            #mdb.Model(name=model_name, objectToCopy=mdb.models[modelName])
#            mdb.Model(name=model_name, modelType=STANDARD_EXPLICIT)
##            model = mdb.models[model_name]
#            #-----------------------------------------------------------
#            #Create squreUF model by execfile 2DsquareUF.py
#            #-----------------------------------
##            execfile('2DsquareUF.py', __main__.__dict__)
        create3DsphericV5( model_name , fiber_flag,vf_f,interface_flag,t_interface,fiber_matname,matrix_matname,interface_matname,mesh_size,elem_type)
                
    return            
#    elif profile == 2:
#        model_name = 'hexUF'
#        modelobj = mdb.models
#        nmodel = len(modelobj)
#        if model_name in modelobj.keys():
#            print 'The model "hexUF" has existed, "hexUF_new" will be created.'
#            model_name = model_name+'_new'
#            #mdb.Model(name=model_name, objectToCopy=mdb.models[modelName])
#            mdb.Model(name=model_name, modelType=STANDARD_EXPLICIT)
#        else:
#            mdb.Model(name=model_name, objectToCopy=mdb.models[modelName])
            
            #-----------------------------------------------------------
            #Create squreUF model by execfile 2DsquareUF.py
            #-----------------------------------
#            execfile('2DhexUF.py', __main__.__dict__)
#        if t_interface == 0.0 :
#            createHexV5(model_name, fiber_flag,vf_f, fiber_matname,matrix_matname,mesh_size,elem_type)
#        elif t_interface != 0.0 :
#            createHexInterfaceV5( model_name , fiber_flag,vf_f,interface_flag,t_interface,fiber_matname,matrix_matname,interface_matname,mesh_size,elem_type)

#    else:
#        model_name='corrugate'
#        modelobj=mdb.models
#        nmodel = len(modelobj)
#        if model_name in modelobj.keys():
#            print 'The model "corrugate" has been existed, "corrugate_new" will be created.'
#            mdb.Model(name=model_name, modelType=STANDARD_EXPLICIT)
#            model_name=model_name+'_new'
#            model = mdb.models[model_name]
#        else:
#            mdb.Model(name=model_name, modelType=STANDARD_EXPLICIT)
#            model = mdb.models[model_name]
            #execfile('2DcorrugateUF.py', __main__.__dict__)
    
    
    
    
                    
