#--------------------------------------
# -*- coding: utf-8 -*-

#FiberReinforced-RVE Script

#--------------------------------------
## Import Section
#--------------------------------------
from textRepr import *
from abaqus import *
from abaqusConstants import *
from caeModules import *
import sketch
from math import *

def create3DsphericV5(model_name , fiber_flag,vf_f,interface_flag,t_interface,fiber_matname,matrix_matname,interface_matname,mesh_size,elem_type):

    #fiber_flag=2
    #vf_f=0.2
    #interface_flag=2
    #t_interface=0.0
    #
    #modelName='Model-1'
    #model_name='Model-1'
    #fiber_matname='inclusion'
    #matrix_matname='matrix'
    #interface_matname='interface'
    #mesh_size=0.1
    #elem_type = 'Linear'
    #
    #mesh_size=0.1
    #meshSize=mesh_size
    #mdb.Model(name=model_name, modelType=STANDARD_EXPLICIT)
    #model = mdb.models[modelName]
    #
    ##Define materials and Sections and assign them
    ##--------------------------------------
    #
    #Ef1  = 5.86100000E+10
    #Ef2  = 1.44900000E+10
    #Ef3  = 1.44900000E+10
    #vf12 = 2.50000000E-01
    #vf13 = 2.50000000E-01
    #vf23 = 2.47000000E-01
    #Gf12 = 5.38000000E+09
    #Gf13 = 5.38000000E+09
    #Gf23 = 5.80994000E+09
    #
    #Em = 3.45000000E+09
    #vm = 3.70000000E-01
    #
    #Ei = 3.45000000E+09
    #vi = 3.70000000E-01
    #
    #
    #mdb.models[model_name].Material(name=fiber_matname)
    #mdb.models[model_name].materials[fiber_matname].Elastic(type=ENGINEERING_CONSTANTS, 
    #    table=((Ef1, Ef2, Ef3, vf12, vf13, vf23, 
    #    Gf12, Gf13, Gf23), ))
    ##mdb.models[model_name].materials[fiber_matname].Elastic(table=((Ef, vf),))
    #
    #mdb.models[model_name].Material(name=matrix_matname)
    #mdb.models[model_name].materials[matrix_matname].Elastic(table=((Em, vm),))
    #
    #mdb.models[model_name].Material(name=interface_matname)
    #mdb.models[model_name].materials[interface_matname].Elastic(table=((Ei, vi),))
    #
    ##********************************************************
    #from material import createMaterialFromDataString
    #
    #createMaterialFromDataString('Model-1', 'Fiber', '6-13', 
    #    """{'materialIdentifier': '', 'description': '', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((58610000000.0, 14490000000.0, 14490000000.0, 0.25, 0.25, 0.247, 5380000000.0, 5380000000.0, 5809940000.0),), 'type': ENGINEERING_CONSTANTS}, 'name': 'Fiber'}""")
    ##: Material 'Fiber' has been copied to the current model.
    #from material import createMaterialFromDataString
    #createMaterialFromDataString('Model-1', 'Interface', '6-13', 
    #    """{'materialIdentifier': '', 'description': '', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((3450000000.0, 0.37),), 'type': ISOTROPIC}, 'name': 'Interface'}""")
    ##: Material 'Interface' has been copied to the current model.
    #from material import createMaterialFromDataString
    #createMaterialFromDataString('Model-1', 'Matrix', '6-13', 
    #    """{'materialIdentifier': '', 'description': '', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((3450000000.0, 0.37),), 'type': ISOTROPIC}, 'name': 'Matrix'}""")
    ##: Material 'Matrix' has been copied to the current model.
    ##********************************************************
    
    
    
    #---------------------------------------------------------
    part_name=['matrix','inclusion','interface']
    part3DName='inclusionP3'
    
    fiber_setname='Inclusion_section'
    matrix_setname='Matrix_section'
    interface_setname='Interphase_section'
    
    partsobj=mdb.models[model_name].parts
#    while part3DName in partsobj.keys():
#        print 'The partName has existed, "partName_new" will be created.'
#        part3DName=part3DName+ '_new'
#        print part3DName
#        for i in range(0,3):
#            part_name[i] = part_name[i] + '_new'
#            print part_name[i]
    
    print '#-------part_name  %s---------------------------'  % part3DName
    #------------------------------------------------------------------------------------
    blockSize = 1.
    quarterSize = 1./2*blockSize
    
    
    mesh_size=0.1
    meshSize=mesh_size
    if elem_type == 'Linear':
        elementType1 = C3D8
        elementType2 = C3D4
        
        
    elif elem_type == 'Quadratic':
        elementType1 = C3D20
        elementType2 = C3D10
        
          
    #-------------------------------
    
    totalVolume= blockSize*blockSize*blockSize
    
    if  fiber_flag==1 : #vf_f is volume fraction  of the fiber
        vof_fiber=vf_f
        fiberRadius= blockSize*pow(3*vof_fiber/4/pi, 1.0/3.0) 
    elif  fiber_flag==2 :  #vf_f is radius of the fiber
        fiberRadius=vf_f
        vof_fiber=4.0/3.0*pi*fiberRadius**3
    
    try: 
        if  interface_flag==1 : #t_interface is volume fraction of the interface
            vof_interface=t_interface
            interfaceRadius= blockSize*pow(3*(vof_fiber+vof_interface)/4/pi, 1.0/3.0) 
                
        elif  interface_flag==2 :  #t_interface is thickness of the interface
            interfaceRadius=fiberRadius+t_interface
            vof_interface= 4.0/3.0*pi*(interfaceRadius**3-fiberRadius**3)
            
            
        if interfaceRadius >=  blockSize/2.0 :
            False
    except:
        raise ValueError('The volume fraction of inclusion and interphase is out of range. Please adjust the values.') 
    
    
    
    print 'blockSize: %s' %blockSize
    print 'totalVolume: %s' %totalVolume    
    
    
    print '#---fiber------------------------'
#    print 'fiber_flag: %s' %fiber_flag
#    print 'vf_f: %s' %vf_f
#    print '#----------------------------'
    print 'vof_inclusion: %s' %vof_fiber
    print 'Inclusion Radius: %s' %fiberRadius
    
    if t_interface>0.0:
        print '#---interphase-------------------------'
#        print 'interface_flag: %s' % str(interface_flag)
#        print 't_interface=: %s' % str(t_interface)
#        print '#----------------------------'
        print 'vof_interphace: %s' %vof_interface
        print 'interphase Radius: %s' %interfaceRadius
    #--------------------------------------------------------------
    
    

        
    #----------------------------------------------------------------------
    #matrix 
    s = mdb.models[model_name].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(-0.5*blockSize, -0.5*blockSize), point2=(0.5*blockSize, 0.5*blockSize))
    p = mdb.models[model_name].Part(name= part_name[0], dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts[ part_name[0]]
    p.BaseSolidExtrude(sketch=s, depth=blockSize)
    s.unsetPrimaryObject()
    p = mdb.models[model_name].parts[ part_name[0]]
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models[model_name].sketches['__profile__']
    
    mdb.models[model_name].HomogeneousSolidSection(name=matrix_setname, 
        material=matrix_matname, thickness=None)
    
        
        
    #--------------------------------------
    #inclusion    
    s1 = mdb.models[model_name].ConstrainedSketch(name='__profile__', 
        sheetSize=20.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    s1.ConstructionLine(point1=(0.0, -10.0), point2=(0.0, 10.0))
    s1.FixedConstraint(entity=g[2])
    s1.Line(point1=(0.0, -fiberRadius), point2=(0.0, fiberRadius))
    s1.VerticalConstraint(entity=g[3], addUndoState=False)
    s1.ArcByCenterEnds(center=(0.0, 0.0), point1=(0.0, fiberRadius), point2=(0.0, -fiberRadius), 
        direction=CLOCKWISE)
    s1.CoincidentConstraint(entity1=v[2], entity2=g[3], addUndoState=False)
    s1.EqualDistanceConstraint(entity1=v[0], entity2=v[1], midpoint=v[2], 
        addUndoState=False)
    p = mdb.models[model_name].Part(name=part_name[1], dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts[part_name[1]]
    p.BaseSolidRevolve(sketch=s1, angle=360.0, flipRevolveDirection=OFF)
    s1.unsetPrimaryObject()
    p = mdb.models[model_name].parts[part_name[1]]
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models[model_name].sketches['__profile__']
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
        engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)  
    
    
    mdb.models[model_name].HomogeneousSolidSection(name=fiber_setname, 
        material=fiber_matname, thickness=None)    
        
    
    #---------------------------------------------------    
    
    #--------------------------------------
    #Interface
    if t_interface>0:
        s = mdb.models[model_name].ConstrainedSketch(name='__profile__', sheetSize=20.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.ConstructionLine(point1=(0.0, -10.0), point2=(0.0, 10.0))
        s.FixedConstraint(entity=g[2])
        s.Line(point1=(0.0, -interfaceRadius), point2=(0.0, interfaceRadius))
        s.VerticalConstraint(entity=g[3], addUndoState=False)
        s.ArcByCenterEnds(center=(0.0, 0.0), point1=(0.0, interfaceRadius), point2=(0.0, -interfaceRadius), 
            direction=CLOCKWISE)
        s.CoincidentConstraint(entity1=v[2], entity2=g[3], addUndoState=False)
        s.EqualDistanceConstraint(entity1=v[0], entity2=v[1], midpoint=v[2], 
            addUndoState=False)
        p = mdb.models[model_name].Part(name=part_name[2], dimensionality=THREE_D, 
            type=DEFORMABLE_BODY)
        p = mdb.models[model_name].parts[part_name[2]]
        p.BaseSolidRevolve(sketch=s, angle=360.0, flipRevolveDirection=OFF)
        s.unsetPrimaryObject()
        p = mdb.models[model_name].parts[part_name[2]]
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models[model_name].sketches['__profile__']
        
        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
            engineeringFeatures=ON)
        session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
            referenceRepresentation=OFF)
        
        mdb.models[model_name].HomogeneousSolidSection(name=interface_setname, 
            material=interface_matname, thickness=None)
    
        
    #--------------------------------------------------------------------------
    
    a = mdb.models[model_name].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
    a = mdb.models[model_name].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    p = mdb.models[model_name].parts[part_name[0]]
    a.Instance(name=part_name[0]+'-1', part=p, dependent=ON)
    a = mdb.models[model_name].rootAssembly
    p = mdb.models[model_name].parts[part_name[1]]
    a.Instance(name=part_name[1]+'-1', part=p, dependent=ON)
    
    if t_interface>0:
        a = mdb.models[model_name].rootAssembly
        p = mdb.models[model_name].parts[part_name[2]]
        a.Instance(name=part_name[2]+'-1', part=p, dependent=ON)
    
    a.translate(instanceList=(part_name[0]+'-1', ), vector=(0.0, 0.0, -0.5*blockSize))
    a1 = mdb.models[model_name].rootAssembly
    
    if t_interface>0:
        a1.InstanceFromBooleanMerge(name=part3DName, 
                                    instances=(a1.instances[part_name[0]+'-1'], 
                                    a1.instances[part_name[1]+'-1'],
                                    a1.instances[part_name[2]+'-1'], ), 
                                    keepIntersections=ON, 
                                    originalInstances=SUPPRESS, domain=GEOMETRY)
        for i in range(0,3):
            del a1.features[part_name[i]+'-1']
            del mdb.models[model_name].parts[part_name[i]]
    
    elif t_interface==0:
        a1.InstanceFromBooleanMerge(name=part3DName, 
                                    instances=(a1.instances[part_name[0]+'-1'], 
                                    a1.instances[part_name[1]+'-1'],
                                     ), 
                                    keepIntersections=ON, 
                                    originalInstances=SUPPRESS, domain=GEOMETRY)
        for i in range(0,2):
            del a1.features[part_name[i]+'-1']
            del mdb.models[model_name].parts[part_name[i]]
    
    elif t_interface<0:
        raise ValueError( 'Interphase thickness should be equal or larger than zero.' )
    #
    ##------------------------------------------
    p = mdb.models[model_name].parts[part3DName]
    c = p.cells
    cells = c.findAt(((blockSize/2, 0.0,0.0),))
    region = p.Set(cells=cells, name=matrix_setname)
    p.SectionAssignment(region=region, sectionName=matrix_setname, offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    
    session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)
    
    cells = c.findAt(((0, 0, 0),))
    cells
    region = p.Set(cells=cells, name=fiber_setname)
    p.SectionAssignment(region=region, sectionName=fiber_setname, offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    
    if t_interface>0.0 :
        Rr=(fiberRadius+interfaceRadius)/2.0
        cells = c.findAt(((Rr, 0.0,0.0),))
        cells
        region = p.Set(cells=cells, name=interface_setname)
        p.SectionAssignment(region=region, sectionName=interface_setname, offset=0.0, 
            offsetType=MIDDLE_SURFACE, offsetField='', 
            thicknessAssignment=FROM_SECTION)   
        
        
    
      
    
    #------------------------------------------------
    #mesh
    p = mdb.models[model_name].parts[part3DName]
    c = p.cells
    pickedRegions = c
    p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
    elemType1 = mesh.ElemType(elemCode=elementType1)
    elemType2 = mesh.ElemType(elemCode=elementType2)
    p = mdb.models[model_name].parts[part3DName]
    c = p.cells
    cells = c
    pickedRegions =(cells, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
    p = mdb.models[model_name].parts[part3DName]
    p.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
    p = mdb.models[model_name].parts[part3DName]
    p.generateMesh()
    #
    
    a = mdb.models[model_name].rootAssembly
    del a.features[part3DName+'-1']
    
    #-----------------------------------------------------------------------
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
    session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
        meshTechnique=ON)
    p = mdb.models[model_name].parts[part3DName]
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
        engineeringFeatures=OFF, mesh=ON)
    session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
        meshTechnique=ON)
    
    return
