# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
import regionToolset
from utilities import *

def setSketchPlane(nsg, part_name, model_name): 

    p = mdb.models[model_name].Part(name=part_name, dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)

    datumPlaneYZ_id = p.DatumPlaneByPrincipalPlane(principalPlane = YZPLANE, offset=0.0).id
    datumAxisZ_id = p.DatumAxisByPrincipalAxis(principalAxis=ZAXIS).id
    YZworkPlaneTransform = (0,1,0,   0,0,1,  1,0,0,   0,0,0) #y-z plane
 
    if nsg == 1:
        s = mdb.models[model_name].ConstrainedSketch(name='__profile__', 
            sheetSize=20.0,transform=YZworkPlaneTransform)
        
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        
        p = mdb.models[model_name].parts[part_name]
        p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
        s.Line(point1=(0., -0.5), point2=(0., 0.5))
            
        e1, d2 = p.edges, p.datums
        p.Wire(sketchPlane=d2[datumPlaneYZ_id], sketchUpEdge=d2[datumAxisZ_id], sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s)
        s.unsetPrimaryObject()
        del mdb.models[model_name].sketches['__profile__']    

        p = mdb.models[model_name].parts[part_name]
        e = p.edges
        edges = e.findAt(((0.0, 0.0, -0.0), ))
        p.Set(edges=edges, name='Set_layup')
        print 'A set "Set_layup" has been created to assign composite layup in "Property" module.'

    cv = session.viewports[session.currentViewportName]
    setViewYZ(cv, nsg, p)
    cv.partDisplay.geometryOptions.setValues(referenceRepresentation = ON)
    
    return 1