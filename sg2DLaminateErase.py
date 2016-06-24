# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
from utilities import *
import customKernel

def eraseLayups(baseline, model_name):
    
    model = mdb.models[model_name]
    vp_name = session.currentViewportName
    part_name = session.viewports[vp_name].displayedObject.name
    p = model.parts[part_name]
    
    cst_models = mdb.customData.models
    cst_model = cst_models[model_name]
    cst_parts = cst_model['Parts']
    cst_part = cst_parts[part_name]
    set_name      = cst_part['Set name']
    set_fpt       = cst_part['Set-FacePoint']
    set_said      = cst_part['Set-SectionAssignment id']
#    s_name        = cst_part['Sketch name']
    feat_ptt_name = cst_part['Partition feature name']
    blid_pt       = cst_part['Baseline']
#    bl_idn        = cst_part['Baseline id']
    sgm_lyr_id    = cst_part['Interface line id']
    sgm_lyr_set   = cst_part['Layer face set name']
    
#    print blid_pt
    
    bl_pt  = baseline.pointOn[0]
#    print bl_pt
    s_name = part_name + '_layer_partition'
    s = model.sketches[s_name]
    g = s.geometry
    
    for i, bl in enumerate(blid_pt):
        if bl_pt == bl[1]:
            bl_idn = bl[0]
            index = i
#    print bl_idn
    blid_pt.remove(blid_pt[index])
    
    count_sa_del = 0
    sa = p.sectionAssignments
    for i in sgm_lyr_set[bl_idn]:
        sa_id = set_said[i] - count_sa_del
        del sa[sa_id]       # Delete section assignment
        set_name.remove(i)
#        print set_name
        del p.sets[i]       # Delete set
        del set_fpt[i]
        count_sa_del += 1
    del sgm_lyr_set[bl_idn]
    
    for i, rn in enumerate(set_name):
        set_said[rn] = i
    
    # Delete sketch lines
    for i in sgm_lyr_id[bl_idn]:
#        print i
        for j in i:
#            print j
            s.delete(objectList = (g[j],))
    del sgm_lyr_id[bl_idn]
    
#    print set_fpt
    
    
#    print set_fpt
#    f = p.faces
#    for rn, fpt in set_fpt.items():
#        ff = f.findAt((fpt,))
#        print rn, ', ', ff[0].pointOn[0]
#        sn = rn.split('/')[0].replace('d', '.')
#        print p.sets[rn].faces[0]
#        rg = p.Set(name = rn, faces = ff)
#        print p.sets[rn].faces[0]
#        p.SectionAssignment(region = rg, sectionName = sn)
        
#    for k, v in p.sets.items():
#        print k
#        print v.faces[0]
    
#    refreshSets(mdb, model_name, part_name)
    
    feat = p.features[feat_ptt_name]
    feat.setValues(sketch = s)
    try:
        p.regenerate()
    except:
            pass
    
    refreshSets(mdb, model_name, part_name, set_fpt)
    
    cst_part['Set name'] = set_name
    cst_part['Set-FacePoint'] = set_fpt
    cst_part['Section-Assignment id'] = set_said
#    cst_part['Set id'] = set_id
#    cst_part['Sketch name'] = s_name
#    cst_part['Partition feature name'] = feat_ptt_name
    cst_part['Baseline'] = blid_pt
#    cst_part['Baseline id'] = bl_idn
    cst_part['Interface line id'] = sgm_lyr_id
    cst_part['Layer face set name'] = sgm_lyr_set
    cst_parts[part_name] = cst_part
    
#    cst_model['mtrId-Name'] = mid_name
#    cst_model['mtrName-Id'] = mname_id
#    cst_model['Layer types'] = layer_types
#    cst_model['lytId-Name'] = lytid_name
#    cst_model['lytName-Id'] = lytname_id
    cst_model['Parts'] = cst_parts
    cst_models[model_name] = cst_model
    mdb.customData.models = cst_models
    
    session.viewports[vp_name].enableMultipleColors()
    session.viewports[vp_name].setColor(initialColor='#BDBDBD')
    cmap=session.viewports[vp_name].colorMappings['Section']
    session.viewports[vp_name].setColor(colorMapping=cmap)
    session.viewports[vp_name].disableMultipleColors()