# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
from symbolicConstants import *
from utilities import *
import numpy as np
#import repr
import customKernel

def assignLayups(baseline, area, model_name, section_name, opposite=0, nsp=20):
    
#    print baseline
#    print boundary
#    print opposite
    
    model = mdb.models[model_name]
    vp_name = session.currentViewportName
    part_name = session.viewports[vp_name].displayedObject.name
    p = model.parts[part_name]
    
    try:
        cst_models = mdb.customData.models
    except AttributeError:
        cst_models = {}
    try:
        cst_model = cst_models[model_name]
    except KeyError:
        cst_model = {}
    try:
        cst_parts = cst_model['Parts']
    except KeyError:
        cst_parts = {}
    try: 
        cst_part = cst_parts[part_name]
    except KeyError:
        cst_part = {}
    try:
        mid_name      = cst_model['mtrId-Name']
        mname_id      = cst_model['mtrName-Id']
        layer_types   = cst_model['Layer types']
        lytid_name    = cst_model['lytId-Name']
        lytname_id    = cst_model['lytName-Id']
    except KeyError:
        mid_name      = {}
        mname_id      = {}
        layer_types   = {}
        lytid_name    = {}
        lytname_id    = {}
        
    try:
        set_name      = cst_part['Set name']
        set_fpt       = cst_part['Set-FacePoint']
        set_said      = cst_part['Set-SectionAssignment id']
        set_id        = cst_part['Set id']
        s_name        = cst_part['Sketch name']
        feat_ptt_name = cst_part['Partition feature name']
        blid_pt       = cst_part['Baseline']
        bl_idn        = cst_part['Baseline id']
        sgm_lyr_id    = cst_part['Interface line id']
        sgm_lyr_set   = cst_part['Layer face set name']
    except KeyError:
        set_name      = []
        set_fpt       = {}
        set_said      = {}
        set_id        = 1
        s_name        = ''
        feat_ptt_name = ''
        blid_pt       = []
        bl_idn        = 1    # self-defined id
        sgm_lyr_id    = {}
        sgm_lyr_set   = {}
    
    e = p.edges
    eids = list(area.getEdges())
#    print eids
#    print baseline.index
    eids.remove(baseline.index)
#    print opposite
#    if opposite != 0:
##        print opposite.index
#        eids.remove(opposite.index)
    vs_bl = baseline.getVertices()
    boundary = []
    for i in eids:
        vs = e[i].getVertices()
        for j in vs:
            if j in vs_bl:
                boundary.append(i)
    
    bl_id  = baseline.index  # edge index, may change
    bd1_id = boundary[0]
    bd2_id = boundary[1]
    bl_pt  = baseline.pointOn[0]
    bd1_pt = e[bd1_id].pointOn[0]
    bd2_pt = e[bd2_id].pointOn[0]
    if opposite != 0:
        ob_id = opposite.index
        ob_pt = opposite.pointOn[0]
        
    blid_pt.append([bl_idn, bl_pt])
        
    layup = model.sections[section_name].layup

    tks = []
    sns = []
    total_tk = 0.0
    for layer in layup:
        tk = layer.thickness
        tks.append(tk)
        total_tk += tk
        mn = layer.material
        ag = layer.orientAngle
        if not mn in mid_name.values():
            n = len(mid_name)
            mid_name[n+1] = mn
            mname_id[mn] = n+1
        mid = mname_id[mn]
#        print ag
        ma = [mid, ag]
        sn = mn + '_' + str(ag)
        sns.append(sn)
        if not ma in layer_types.values():
            n = len(layer_types)
            layer_types[n+1] = ma
            model.HomogeneousShellSection(name = sn, material = mn, thickness = 1.0)
    
    vs = p.vertices
    vs_bl = baseline.getVertices()
    vs_bd1 = e[bd1_id].getVertices()
    vs_bd2 = e[bd2_id].getVertices()
    v0_id = vs_bl[1]
    if v0_id in vs_bd1:
        v1_id = list(vs_bd1)
#        print 'vs_bd1'
#        print v1_id
#        print v0_id
        v1_id.remove(v0_id)
        v1_id = v1_id[0]
    elif v0_id in vs_bd2:
        v1_id = list(vs_bd2)
#        print 'vs_bd2'
#        print v1_id
#        print v0_id
        v1_id.remove(v0_id)
        v1_id = v1_id[0]
    v0 = vs[v0_id]
    v1 = vs[v1_id]
    pt0 = v0.pointOn[0]
    pt1 = v1.pointOn[0]
    
#    print '- Partittion layups'
#    print feat_ptt_name
    f, e, d = p.faces, p.edges, p.datums
#    if s_name == '':
#        s_name = 'layer_partition'
#        t = p.MakeSketchTransform(sketchPlane = f[0], sketchUpEdge = d[2], 
#                                  sketchPlaneSide = SIDE1, origin = (0.0, 0.0, 0.0))
#        s = model.ConstrainedSketch(name = s_name, sheetSize = 500.0, transform = t)
#    else:
#        s = model.sketches[s_name]
    s_name = part_name + '_layer_partition'
    try:
        s = model.sketches[s_name]
    except KeyError:
        t = p.MakeSketchTransform(sketchPlane = f[0], sketchUpEdge = d[2], 
                                  sketchPlaneSide = SIDE1, origin = (0.0, 0.0, 0.0))
        s = model.ConstrainedSketch(name = s_name, sheetSize = 500.0, transform = t)
#    s.setPrimaryObject(option = SUPERIMPOSE)
#    p.projectReferencesOntoSketch(sketch = s, filter = COPLANAR_EDGES)
#    p.projectEdgesOntoSketch(sketch = s, edges = (e[bl_id],))
#    if opposite != 0:
#        p.projectEdgesOntoSketch(sketch = s, edges = (e[ob_id],))
    
    
    check_side = 1
    offset_side = 'LEFT'
    ttk = 0.0
    fpt_section = []
    
    g = s.geometry
    
    sbl = g.findAt(coordinates = (bl_pt[1], bl_pt[2]), printWarning = False)
    if sbl == None:
        p.projectEdgesOntoSketch(sketch = s, edges = (e[bl_id],))
        sbl = g.findAt(coordinates = (bl_pt[1], bl_pt[2]))
    
    sbd1 = g.findAt(coordinates = (bd1_pt[1], bd1_pt[2]), printWarning = False)
    if sbd1 == None:
        p.projectEdgesOntoSketch(sketch = s, edges = (e[bd1_id],))
        sbd1 = g.findAt(coordinates = (bd1_pt[1], bd1_pt[2]))
    
#    print s.geometry.keys()
    sbd2 = g.findAt(coordinates = (bd2_pt[1], bd2_pt[2]), printWarning = False)
    if sbd2 == None:
        p.projectEdgesOntoSketch(sketch = s, edges = (e[bd2_id],))
        sbd2 = g.findAt(coordinates = (bd2_pt[1], bd2_pt[2]))
    
#    print s.geometry.keys()
#    print opposite
    if opposite != 0:
        sob = g.findAt(coordinates = (ob_pt[1], ob_pt[2]), printWarning = False)
        if sob == None:
            p.projectEdgesOntoSketch(sketch = s, edges = (e[ob_id],))
            sob = g.findAt(coordinates = (ob_pt[1], ob_pt[2]))
#        print sob
    sbl0 = sbl
    
    
    sgm_lyr_id[bl_idn] = []
    ctype = repr(sbl.curveType)
    if ctype == 'LINE':
        for i, tk in enumerate(tks):
#            print 'Layer: ', str(i+1)
            milestone('Layer: ' + str(i+1))
#            print tk
            ttk += tk/2.0
            if offset_side == 'LEFT':
                s.offset(objectList = (sbl,), distance = ttk, side = LEFT)
            elif offset_side == 'RIGHT':
                s.offset(objectList = (sbl,), distance = ttk, side = RIGHT)
#            print s.geometry.keys()
            if check_side == 1:
                offset_side = checkOffsetSide(s, pt0, pt1, sbl, ttk)
                check_side = 0
#            print s.geometry.keys()
            try:
                g = s.geometry
                tline_id = g.keys()[-1]
    #            print tline_id
                s.trimExtendCurve(curve1 = g[tline_id], point1 = g[tline_id].pointOn, 
                                  curve2 = sbd1, point2 = sbd1.pointOn)
            except:
                pass
#            print s.geometry.keys()
            try:
                g = s.geometry
#                print 'try 2'
#                print s.geometry.keys()
                tline_id = g.keys()[-1]
#                print tline_id
#                print g[tline_id]
                s.trimExtendCurve(curve1 = g[tline_id], point1 = g[tline_id].pointOn, 
                                  curve2 = sbd2, point2 = sbd2.pointOn)
#                print 'try 2'
#                print s.geometry.keys()
            except:
#                print 'except 2'
#                print s.geometry.keys()
                pass
#            print g[tline_id]
#            print s.geometry.keys()
            g = s.geometry
            tline_id = g.keys()[-1]
#            print tline_id
            tline = g[tline_id]
            fpt = (0.0,) + tline.pointOn
            sn = sns[i]
            fpt_section.append([fpt,sn])
            s.delete(objectList = (tline,))
#            print s.geometry.keys()
            if not i == len(tks)-1:
                temp = []
                ttk += tk/2.0
                if offset_side == 'LEFT':
                    s.offset(objectList = (sbl,), distance = ttk, side = LEFT)
                elif offset_side == 'RIGHT':
                    s.offset(objectList = (sbl,), distance = ttk, side = RIGHT)
#                print s.geometry.keys()
                try:
                    g = s.geometry
                    tline_id = g.keys()[-1]
                    s.trimExtendCurve(curve1 = g[tline_id], point1 = g[tline_id].pointOn, 
                                      curve2 = sbd1, point2 = sbd1.pointOn)
                except:
                    pass
#                print s.geometry.keys()
                try:
                    g = s.geometry
                    tline_id = g.keys()[-1]
                    s.trimExtendCurve(curve1 = g[tline_id], point1 = g[tline_id].pointOn, 
                                      curve2 = sbd2, point2 = sbd2.pointOn)
                except:
                    pass
#                print s.geometry.keys()
                g = s.geometry
                temp.append(g.keys()[-1])
                sgm_lyr_id[bl_idn].append(temp)
                
    elif ctype == 'SPLINE' or ctype == 'ARC' or ctype == 'CIRCLE' or ctype == 'ELLIPSE':
#        nsp = 100  # number of sample points
        spline_constrain = True
        sbl_pts = []
        oob_pts = []
        temp_pt0 = pt1
        temp_pt1 = pt0
        s.offset(objectList = (sob,), distance = total_tk, side = LEFT)
        a = checkOffsetSide(s, temp_pt0, temp_pt1, sob, total_tk)
        g = s.geometry
        oob_id = g.keys()[-1]  # offset oppposite boundary id
        oob = g[oob_id]
        sbl_vs = sbl.getVertices()
        sbl_pt1 = sbl_vs[0].coords
        sbl_pt2 = sbl_vs[1].coords
        oob_vs = oob.getVertices()
        oob_pt1 = oob_vs[0].coords
        oob_pt2 = oob_vs[1].coords
        sbl_pts.append(sbl_pt1)
        oob_pts.append(oob_pt1)
        for i in range(1, 100, 100/nsp):
            sbl_pt = sbl.getPointAtDistance(point=sbl_pt1, distance=i, percentage=True)
            oob_pt = oob.getPointAtDistance(point=oob_pt1, distance=i, percentage=True)
            sbl_pts.append(sbl_pt)
            oob_pts.append(oob_pt)
        sbl_pts.append(sbl_pt2)
        oob_pts.append(oob_pt2)
        
#        print sbl_pts
#        print oob_pts
        
        sbl_len = sbl.getSize()
        oob_len = oob.getSize()
        sbl_r   = sbl_len / nsp / 2.0
        oob_r   = oob_len / nsp / 2.0
        
#        print sbl_r
#        print oob_r
        
        oob_kp = {}
        for i, pt in enumerate(oob_pts):
            x0, y0 = pt[0], pt[1]
            x1, y1 = sbl_pt1[0], sbl_pt1[1]
            x2, y2 = sbl_pt2[0], sbl_pt2[1]
            d1 = np.sqrt((x1-x0)**2+(y1-y0)**2)
            d2 = np.sqrt((x2-x0)**2+(y2-y0)**2)
#            print '[' + str(d1) + ', ' + str(d2) + ']'
            if d1 < oob_r:
                oob_kp[1] = [i, pt]
            if d2 < oob_r:
                oob_kp[2] = [i, pt]
                
#        print oob_kp
        
        if len(oob_kp) == 0 or len(oob_kp) == 2:
            if oob_len > sbl_len:
                sbl = oob
        elif len(oob_kp) == 1:
            oob_kp_id = oob_kp.values()[0][0]
#            print oob_kp_id
            for i, pt in enumerate(sbl_pts):
                x0, y0 = pt[0], pt[1]
                x1, y1 = oob_pt1[0], oob_pt1[1]
                x2, y2 = oob_pt2[0], oob_pt2[1]
                d1 = np.sqrt((x1-x0)**2+(y1-y0)**2)
                d2 = np.sqrt((x2-x0)**2+(y2-y0)**2)
#                print '[' + str(d1) + ', ' + str(d2) + ']'
                if d1 < sbl_r:
                    kp_id = 0
                if d2 < sbl_r:
                    kp_id = -1
#            print kp_id
            sbl_vec = np.array((0.0,)+sbl_pt2) - np.array((0.0,)+sbl_pt1)
            oob_vec = np.array((0.0,)+oob_pt2) - np.array((0.0,)+oob_pt1)
            dp = np.dot(sbl_vec, oob_vec)
#            print dp
            if kp_id == 0:
                sbl_pts_extra = oob_pts[oob_kp_id+1:]
                if dp > 0.0:
                    sbl_pts = sbl_pts + sbl_pts_extra
                    pt0 = (0.0,) + sbl_pts[-1]
                elif dp < 0.0:
                    sbl_pts = sbl_pts_extra.reverse() + sbl_pts
            elif kp_id == -1:
                sbl_pts_extra = oob_pts[:oob_kp_id-1]
                if dp > 0.0:
#                    print sbl_pts
#                    print sbl_pts_extra
                    sbl_pts = sbl_pts_extra + sbl_pts
                elif dp < 0.0:
                    sbl_pts = sbl_pts + sbl_pts_extra.reverse()
                    pt0 = (0.0,) + sbl_pts[-1]
#            print sbl_pts
            sbl = s.Spline(points = sbl_pts, constrainPoints = spline_constrain)
        
        vs_sbl0 = sbl0.getVertices()
        pt0_sbl0 = vs_sbl0[0].coords
        pt1_sbl0 = vs_sbl0[1].coords
        vs_sbl1 = sbl.getVertices()
        pt0_sbl1 = vs_sbl1[0].coords
        pt1_sbl1 = vs_sbl1[1].coords
        vec_sbl0 = np.array(pt1_sbl0) - np.array(pt0_sbl0)
        vec_sbl1 = np.array(pt1_sbl1) - np.array(pt0_sbl1)
        dp = np.dot(vec_sbl0, vec_sbl1)
        sbd0 = sbd1
        sbd1 = sbd2
        if vs_sbl0[0] in sbd1.getVertices():
            temp = sbd0
            sbd0 = sbd1
            sbd1 = temp
            
        for i, tk in enumerate(tks):
#            print 'Layer: ', str(i+1)
            milestone('Layer: ' + str(i+1))
            ttk += tk / 2.0
            if offset_side == 'LEFT':
                s.offset(objectList = (sbl,), distance = ttk, side = LEFT)
            elif offset_side == 'RIGHT':
                s.offset(objectList = (sbl,), distance = ttk, side = RIGHT)
            if check_side == 1:
                offset_side = checkOffsetSide(s, pt0, pt1, sbl, ttk)
                check_side = 0
            # trim curve
            try:
                g = s.geometry
                tline_id = g.keys()[-1]
                s.breakCurve(curve1 = g[tline_id], point1 = g[tline_id].pointOn, 
                             curve2 = sbd0, point2 = sbd0.pointOn)
                g = s.geometry
                if dp > 0.0:
#                    print g.keys()[-2]
                    s.delete(objectList = (g[g.keys()[-2]],))
                elif dp < 0.0:
#                    print g.keys()[-1]
                    s.delete(objectList = (g[g.keys()[-1]],))
            except:
                pass
            
            try:
                g = s.geometry
                tline_id = g.keys()[-1]
                s.breakCurve(curve1 = g[tline_id], point1 = g[tline_id].pointOn, 
                             curve2 = sbd1, point2 = sbd1.pointOn)
                g = s.geometry
                if dp > 0.0:
#                    print g.keys()[-1]
                    s.delete(objectList = (g[g.keys()[-1]],))
                elif dp < 0.0:
#                    print g.keys()[-2]
                    s.delete(objectList = (g[g.keys()[-2]],))
            except:
                pass
            
            g = s.geometry
            tline_id = g.keys()[-1]
            tline = g[tline_id]
            fpt = (0.0,) + tline.pointOn
            sn = sns[i]
            fpt_section.append([fpt,sn])
            s.delete(objectList = (tline,))
            
            if not i == len(tks)-1:
                temp = []
                ttk += tk / 2.0
                if offset_side == 'LEFT':
                    s.offset(objectList = (sbl,), distance = ttk, side = LEFT)
                elif offset_side == 'RIGHT':
                    s.offset(objectList = (sbl,), distance = ttk, side = RIGHT)
                # trim curve
                g = s.geometry
                ledge_id = g.keys()[-1]
                temp.append(ledge_id)
                try:
                    s.breakCurve(curve1 = g[ledge_id], point1 = g[ledge_id].pointOn, 
                                 curve2 = sbd0, point2 = sbd0.pointOn)
#                    print 'Break curve by boundary 1'
                    g = s.geometry
                    if dp > 0.0:
                        s.delete(objectList = (g[g.keys()[-2]],))
                    elif dp < 0.0:
                        s.delete(objectList = (g[g.keys()[-1]],))
                    g = s.geometry
                    ledge_id = g.keys()[-1]
                    temp.remove(temp[-1])
                    temp.append(ledge_id)
                except:
                    g = s.geometry
                    tline_id = g.keys()[-1]
                    tline_vs = g[tline_id].getVertices()
                    tline_pt0 = tline_vs[0].coords
                    tline_pt1 = tline_vs[1].coords
                    if dp > 0.0:
                        tline_pt2x = tline_pt0[0] + (tline_pt0[0] - tline_pt1[0])
                        tline_pt2y = tline_pt0[1] + (tline_pt0[1] - tline_pt1[1])
                        tline_pt2 = (tline_pt2x, tline_pt2y)
                        s.Line(point1 = tline_pt0, point2 = tline_pt2)
                    elif dp < 0.0:
                        tline_pt2x = tline_pt1[0] + (tline_pt1[0] - tline_pt0[0])
                        tline_pt2y = tline_pt1[1] + (tline_pt1[1] - tline_pt0[1])
                        tline_pt2 = (tline_pt2x, tline_pt2y)
                        s.Line(point1 = tline_pt1, point2 = tline_pt2)
                    g = s.geometry
                    sline_id = g.keys()[-1]
                    s.FixedConstraint(entity = g[tline_id])
                    s.TangentConstraint(entity1 = g[tline_id], entity2 = g[sline_id])
                    try:
                        s.breakCurve(curve1 = g[sline_id], point1 = g[sline_id].pointOn, 
                                     curve2 = sbd0, point2 = sbd0.pointOn)
                        temp.append(s.geometry.keys()[-2])
                    except:
                        pass
                    g = s.geometry
                    sline_id = g.keys()[-1]
                    s.delete(objectList = (g[sline_id],))
                    
                
                try:
                    s.breakCurve(curve1 = g[ledge_id], point1 = g[ledge_id].pointOn, 
                                 curve2 = sbd1, point2 = sbd1.pointOn)
#                    print 'Break curve by boundary 2'
                    g = s.geometry
                    if dp > 0.0:
                        s.delete(objectList = (g[g.keys()[-1]],))
                    elif dp < 0.0:
                        s.delete(objectList = (g[g.keys()[-2]],))
                    g = s.geometry
                    temp.remove(ledge_id)
                    ledge_id = g.keys()[-1]
#                    temp.remove(temp[-1])
                    temp.append(ledge_id)
                except:
                    g = s.geometry
                    tline_id = g.keys()[-1]
                    tline_vs = g[tline_id].getVertices()
                    tline_pt0 = tline_vs[0].coords
                    tline_pt1 = tline_vs[1].coords
                    if dp > 0.0:
                        tline_pt2x = tline_pt1[0] + (tline_pt1[0] - tline_pt0[0])
                        tline_pt2y = tline_pt1[1] + (tline_pt1[1] - tline_pt0[1])
                        tline_pt2 = (tline_pt2x, tline_pt2y)
                        s.Line(point1 = tline_pt1, point2 = tline_pt2)
                    elif dp < 0.0:
                        tline_pt2x = tline_pt0[0] + (tline_pt0[0] - tline_pt1[0])
                        tline_pt2y = tline_pt0[1] + (tline_pt0[1] - tline_pt1[1])
                        tline_pt2 = (tline_pt2x, tline_pt2y)
                        s.Line(point1 = tline_pt0, point2 = tline_pt2)
                    g = s.geometry
                    sline_id = g.keys()[-1]
                    s.FixedConstraint(entity = g[tline_id])
                    s.TangentConstraint(entity1 = g[tline_id], entity2 = g[sline_id])
                    try:
                        s.breakCurve(curve1 = g[sline_id], point1 = g[sline_id].pointOn, 
                                     curve2 = sbd1, point2 = sbd1.pointOn)
                        temp.append(s.geometry.keys()[-2])
                    except:
                        pass
                    g = s.geometry
                    sline_id = g.keys()[-1]
                    s.delete(objectList = (g[sline_id],))
                sgm_lyr_id[bl_idn].append(temp)
        
        s.delete(objectList = (oob,))
        if len(oob_kp) == 1:
            s.delete(objectList = (sbl,))
        
#    print sgm_lyr_id[bl_idn]
#    if feat_ptt_name == '':
#        feat = p.PartitionFaceBySketch(faces = f, sketchUpEdge = d[2], sketch = s)
#        feat_ptt_name = feat.name
#    else:
#        p.features[feat_ptt_name].setValues(sketch = s)
    try:
        feat = p.features[feat_ptt_name]
        feat.setValues(sketch = s)
    except KeyError:
        feat = p.PartitionFaceBySketch(faces = f, sketchUpEdge = d[2], sketch = s)
        feat_ptt_name = feat.name
    p.regenerate()
    
    # Update sets
#    print '- Update sets'
#    f = p.faces
#    for i in range(len(set_fpt)):
#        rn = set_fpt[i][0]
#        fpt = set_fpt[i][1]
#        ff = f.findAt((fpt,))
#        p.Set(name = rn, faces = ff)
        
#    for rn, fpt in set_fpt.items():
#        ff = f.findAt((fpt,))
#        p.Set(name = rn, faces = ff)
    refreshSets(mdb, model_name, part_name, set_fpt)
    
    # Assign sections
#    print '- Assign sections'
    f = p.faces
#    n = len(set_fpt)
    sgm_lyr_set[bl_idn] = []
    for i in range(len(fpt_section)):
        fpt = fpt_section[i][0]
#        print fpt
        sn = fpt_section[i][1]
        rn = sn.replace('.', 'd') + '/' + str(set_id)
        ff = f.findAt((fpt,))
#        print ff
        rg = p.Set(name = rn, faces = ff)
        sa = p.SectionAssignment(region = rg, sectionName = sn)
#        set_fpt.append([rn, fpt])
        set_name.append(rn)
        set_fpt[rn] = fpt
        set_said[rn] = len(p.sectionAssignments) - 1
        set_id += 1
        sgm_lyr_set[bl_idn].append(rn)

    bl_idn += 1

    cst_part['Set name'] = set_name
    cst_part['Set-FacePoint'] = set_fpt
    cst_part['Set-SectionAssignment id'] = set_said
    cst_part['Set id'] = set_id
    cst_part['Sketch name'] = s_name
    cst_part['Partition feature name'] = feat_ptt_name
    cst_part['Baseline'] = blid_pt
    cst_part['Baseline id'] = bl_idn
    cst_part['Interface line id'] = sgm_lyr_id
    cst_part['Layer face set name'] = sgm_lyr_set
    cst_parts[part_name] = cst_part
    
    cst_model['mtrId-Name'] = mid_name
    cst_model['mtrName-Id'] = mname_id
    cst_model['Layer types'] = layer_types
    cst_model['lytId-Name'] = lytid_name
    cst_model['lytName-Id'] = lytname_id
    cst_model['Parts'] = cst_parts
    cst_models[model_name] = cst_model
    mdb.customData.models = cst_models
    
    session.viewports[vp_name].enableMultipleColors()
    session.viewports[vp_name].setColor(initialColor='#BDBDBD')
    cmap = session.viewports[vp_name].colorMappings['Section']
    session.viewports[vp_name].setColor(colorMapping=cmap)
    session.viewports[vp_name].disableMultipleColors()
    
    
def checkOffsetSide(sketch, point0, point1, line, distance):
    s = sketch
    pt0 = point0
    pt1 = point1
    sbl = line
    ttk = distance
    
    g = s.geometry
    gk = g.keys()
    tline_id = gk[-1]
    v = g[tline_id].getVertices()
    pt2 = (0.0,) + v[1].coords
    vec1 = np.array(pt1) - np.array(pt0)
    vec2 = np.array(pt2) - np.array(pt0)
    offset_side = 'LEFT'
    if np.dot(vec1, vec2) < 0.0:
        offset_side = 'RIGHT'
        s.delete(objectList = (g[tline_id],))
        s.offset(objectList = (sbl,), distance = ttk, side = RIGHT)
    
    return offset_side