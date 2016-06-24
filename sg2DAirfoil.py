# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
from part import *
from assembly import *
from mesh import *
from job import *
from utilities import *
import customKernel
import sys
import time
import os
import math
import xml.etree.ElementTree as et

#from convert2sc import *

def createAirfoil(project_name, control_file):
    
    mc = mdb.customData

    sec_0 = time.time()
    sec_o = sec_0
    
    # Terminate flag
    # rf: Read files
    # sf: Sketch profile
    # st: Sketch partition
    # cp: Create part and partition
    # ff: Find faces
    # im: Import materials
    # cs: Create and assign sections
    # ao: Assign orientations
    # gm: Generate mesh
    # cj: Create job and write input
    steps = ['rf', 'sf', 'st', 'cp', 'ff', 'im', 'cs', 'ao', 'gm', 'cj']
    ns = len(steps)
    tnt = 'all'
    
    mesh_size   = 0.003
    sp_transform = (0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
#    cwd = os.getcwd()  # current working directory
    cwd = os.path.dirname(control_file)
    os.chdir(cwd)
    log_name    = os.path.join(cwd, project_name+'.log')
    debug_name  = os.path.join(cwd, project_name+'.debug')
    cae_name    = os.path.join(cwd, project_name+'.cae')
    model_name  = project_name + '_model'
    ss_name     = project_name + '_sketch_surface'
    ps_name     = project_name + '_part_surface'
    job_name    = project_name
    abq_input   = os.path.join(cwd, job_name+'.inp')
    tolerance   = 1.0E-05
    
    f_log   = open(log_name, 'w')
    f_debug = open(debug_name, 'w')
    
    mc.mid_name = {}
    mc.mname_id = {}
    
    mc.layups = {}         # {id: [total_thickness, [[thickness, layer_type_id], ...]], ...}
    mc.lypid_name = {}     # {id: 'name'}
    mc.lypname_id = {}     # {'name': id}
    
    mc.layer_types = {}    # {id: [material_id, angle], ...}
    mc.lytid_name = {}     # {id: 'name}
    mc.lytname_id = {}     # {'name': id}
    
    # ==========================================================================
    # Read files
    # ==========================================================================
    if (tnt in steps[0:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Reading file...  ' + time_now + '\n')
        milestone('Reading file...')
    #    print 'Reading file...'
        
        # ----------------------------------------------------------------------
        # Read control file
        project = et.parse(control_file)
        project = project.getroot()
        
        fn_shape    = project.find('shapes').text
        fn_material = project.find('materials').text
        fn_layup    = project.find('layups').text
        if (not '.xml' in fn_shape) and (not '.XML' in fn_shape):
            fn_shape += '.xml'
        if (not '.xml' in fn_material) and (not '.XML' in fn_material):
            fn_material += '.xml'
        if (not '.xml' in fn_layup) and (not '.XML' in fn_layup):
            fn_layup += '.xml'
        ffn_shape    = os.path.join(cwd, fn_shape)
        ffn_material = os.path.join(cwd, fn_material)
        ffn_layup    = os.path.join(cwd, fn_layup)
        
        mc.chord_length = float(project.find('chord_length').text)
        mc.twist_angle = float(project.find('twisted_angle').text)
        xy_offset = project.find('pitch_axis_yz').text.split()
        mc.x_offset = float(xy_offset[0])
        mc.y_offset = float(xy_offset[1])
        mc.flip = project.find('flip').text
        
        # ----------------------------------------------------------------------
        # Read shape file
        coord_lps = []
        coord_hps = []
        sgm_pt_id_lps = []  # [[start_pt, end_pt, layup_id], ...]
        sgm_pt_id_hps = []
        nwebs = 0
        webs = {}           # {id: [x, y, angle], ...}
        webs_layup = []     # [layup_id, ...]
        nfills = 0
        fills = {}          # {id: [region, material_id], ...}
        shape = et.parse(ffn_shape)
        assmb = shape.getroot()
        for p in assmb:
            strct = p.get('structure')
            if strct == 'surface':
                bl = p.find('baseline')
                fmt = bl.get('format')
                if fmt == 'lednicer':
                    lps = bl.find('lps').text.strip().split('\n')
                    for c in lps:
                        c = c.split()
                        coord_lps.append((float(c[0]), float(c[1])))
                    hps = bl.find('hps').text.strip().split('\n')
                    for c in hps:
                        c = c.split()
                        coord_hps.append((float(c[0]), float(c[1])))
                lyp = p.find('layup')
                lps = lyp.find('lps').text.strip().split('\n')
                for l in lps:
                    l = l.split()
                    sgm_pt_id_lps.append([int(l[0]), int(l[1]), int(l[2])])
                hps = lyp.find('hps').text.strip().split('\n')
                for l in hps:
                    l = l.split()
                    sgm_pt_id_hps.append([int(l[0]), int(l[1]), int(l[2])])
            elif strct == 'web':
                bl = p.find('baseline')
                for i, w in enumerate(bl):
                    w = w.text.split()
                    webs[i+1] = [float(w[0]), float(w[1]), float(w[2])]
                nwebs = len(webs)
                lyp = p.find('layup').text.strip().split('\n')
                for l in lyp:
                    webs_layup.append(int(l))
            elif strct == 'filling':
                for i, f in enumerate(p):
                    m = f.get('material')
                    r = f.text
                    fills[i+1] = [int(r), int(m)]
                nfills = len(fills)
                
#        if coord_lps[0] != (0.0, 0.0):
#            coord_lps.insert(0, (0.0, 0.0))
#        if coord_hps[0] != (0.0, 0.0):
#            coord_hps.insert(0, (0.0, 0.0))
        
        # ----------------------------------------------------------------------
        # Read materials
        tree = et.parse(ffn_material)
        mtr_root = tree.getroot()

        for mtr in mtr_root:
            material_id   = int(mtr.find('id').text)
            material_name = mtr.find('name').text
            material_type = mtr.get('type')
            mc.mid_name[material_id] = material_name
            mc.mname_id[material_name] = material_id
        
        # ----------------------------------------------------------------------
        # Read layups
        tree_layup = et.parse(ffn_layup)
        root_layup = tree_layup.getroot()

        lyt_id = 0
        for layup in root_layup:
            lyp_id = int(layup.find('id').text)
            lyp_name = layup.find('name').text
            lyp_data = layup.find('data').text
            lyp_data = lyp_data.strip().split('\n')
            total_thk = 0.0
            temp_layup = []
            for l in lyp_data:
                l = l.split()
                [t, m, a] = [float(l[0]), int(l[1]), float(l[2])]
                total_thk += t
                lyt_name = mc.mid_name[m] + '_' + str(a)
                if lyt_name not in mc.lytname_id.keys():
                    lyt_id += 1
                    mc.layer_types[lyt_id] = [m, a]
                    mc.lytid_name[lyt_id] = lyt_name
                    mc.lytname_id[lyt_name] = lyt_id
                lyp_lyt_id = mc.lytname_id[lyt_name]
                temp_layup.append([t, lyp_lyt_id])
                
            mc.layups[lyp_id] = [total_thk, temp_layup]
            mc.lypid_name[lyp_id] = lyp_name
            mc.lypname_id[lyp_name] = lyp_id

        sgm_divpt_lps = []
        sgm_divpt_hps = []
        
        try:
            for n in range(len(sgm_pt_id_lps) - 1):
                ptid = sgm_pt_id_lps[n][1]
                c = coord_lps[ptid - 1]
                sgm_divpt_lps.append(c)
            for n in range(len(sgm_pt_id_hps) - 1):
                ptid = sgm_pt_id_hps[n][1]
                c = coord_hps[ptid - 1]
                sgm_divpt_hps.append(c)
        except IndexError:
            print 'Please check the dividing point number and the total number of airfoil data points'
            
        coord_lps.reverse()
        coord_lps.remove((0.0, 0.0))
        coord = coord_lps + coord_hps
            
#        sgm_lps = {}
#        sgm_hps = {}
#        web_lyp = {}
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
        
        
        try:
            model = mdb.models[model_name]
        except KeyError:
            model = mdb.Model(name = model_name)
        
    # ==========================================================================
    # Sketch profile
    # ==========================================================================
    if (tnt in steps[1:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Sketching profile...  ' + time_now + '\n')
        milestone('Sketching profile...')
    #    print 'Sketching profile...'
        
        trailing_edge = 'Sharp'
        
        fill_side_pts = []
        fill_fpt = []
        fill_partition_v = []
        
        if coord[-1] == coord[0]:                                                 # Open the outline
            del coord[-1]
        np = len(coord)
        
        pts = tuple(coord)
        
        # ----------------------------------------------------------------------
        # Sketch the airfoil surface
        sheet_size = mc.chord_length * 2.0
        ss = model.ConstrainedSketch(name = ss_name, sheetSize = sheet_size)
        sketch = ss
        sketch.sketchOptions.setValues(gridOrigin = (0.0, 0.0))
        
        if trailing_edge == 'Straight':
            s = sketch.Spline(points = pts)
            l = sketch.Line(point1 = pts[-1], point2 = pts[0])
            s = (s, l)
        elif trailing_edge == 'Sharp':
            last_x = (coord[-1][0] + coord[0][0]) / 2.0                           # Find the middle of the connecting line between
            last_y = (coord[-1][1] + coord[0][1]) / 2.0                           # the first and the last point.
            pts += ((last_x, last_y),)                                            # Add an extra point.
#            print pts
#            print len(pts)
            s = sketch.Spline(points = pts)
#            for i in range(len(sketch.vertices.keys())):
#                print sketch.vertices[i]
            sketch.FixedConstraint(entity = sketch.vertices[0])
            sketch.CoincidentConstraint(entity1 = sketch.vertices[np],            # Let the extra point coincide with the first point.
                                        entity2 = sketch.vertices[0])
            s = (s,)
        elif trailing_edge == 'Round':
            pts += ((coord[0][0], coord[0][1]),)
            s = sketch.Spline(points = pts)
            s = (s,)
        
        cline_h = sketch.ConstructionLine(point1 = (-1.0, 0.0),                # Horizontal reference line
                                          point2 = (0.0, 0.0))
        sketch.HorizontalConstraint(entity = cline_h)
        cline_v = sketch.ConstructionLine(point1 = (0.0, -1.0),                # Vertical reference line at the leading edge
                                          point2 = (0.0, 1.0))
        sketch.VerticalConstraint(entity = cline_v)
        cline_c = sketch.ConstructionLine(point1 = (mc.x_offset, -1.0),           # Vertical reference line at the x_offset
                                          point2 = (mc.x_offset, 1.0))
                                          
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Make a copy for the mask later
        if nwebs != 0:
            sm_name = project_name + '_sketch_mask'
            sm = model.ConstrainedSketch(name = sm_name, 
                                         objectToCopy = model.sketches[ss_name])
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Find dividing points and store construction lines
        clines_lps = []
        clines_hps = []
        for pt in sgm_divpt_lps:
            x = pt[0]
            y = pt[1]
    #        if abs(x - 1.0) > tolerance:
            dl = sketch.ConstructionLine(point1 = (x, y), 
                                         point2 = (x, 0.0))
            sketch.VerticalConstraint(entity = dl)
            clines_lps.append(dl)
        for pt in sgm_divpt_hps:
            x = pt[0]
            y = pt[1]
    #        if abs(x - 1.0) > tolerance:
            dl = sketch.ConstructionLine(point1 = (x, y), 
                                         point2 = (x, 0.0))
            sketch.VerticalConstraint(entity = dl)
            clines_hps.append(dl)
        
        # Split curves
        s0 = s[0]
        sketch.breakCurve(curve1 = s0, point1 = (0.0, 0.0), 
                          curve2 = cline_h, point2 = (0.0, 0.0))
        g = sketch.geometry
        #print g
        gk = g.keys()
        gk_lps = gk[-2]
        gk_hps = gk[-1]
        #print gk_lps
        #print gk_hps
        
        # --------------------------
        # Split low pressure surface
        sgm_id_lps_out = []
        k = gk_lps
        for i in range(len(clines_lps)):
            sketch.breakCurve(curve1 = g[k], point1 = sgm_divpt_lps[i], 
                              curve2 = clines_lps[i], point2 = sgm_divpt_lps[i])
            g = sketch.geometry
            gk = g.keys()
            gk_left = gk[-1]
            gk_right = gk[-2]
            sgm_id_lps_out.append(gk_left)
            k = gk_right
        sgm_id_lps_out.append(k)
        
        # ---------------------------
        # Split high pressure surface
        sgm_id_hps_out = []
        k = gk_hps
        for i in range(len(clines_hps)):
            sketch.breakCurve(curve1 = g[k], point1 = sgm_divpt_hps[i], 
                              curve2 = clines_hps[i], point2 = sgm_divpt_hps[i])
            g = sketch.geometry
            gk = g.keys()
            gk_left = gk[-2]
            gk_right = gk[-1]
            sgm_id_hps_out.append(gk_left)
            k = gk_right
        sgm_id_hps_out.append(k)
        
        g = sketch.geometry
        
        # ----------------------------
        # Flip, Move, Scale and Rotate
        
        g = sketch.geometry
        gk = g.keys()
        objects_mirror = []
        for k in gk:
            if k != cline_v.id:
                objects_mirror.append(g[k])
        objects_all = objects_mirror + [cline_v,]
        objects_mirror = tuple(objects_mirror)
        objects_all = tuple(objects_all)
        
        if mc.flip == 'Yes':
            sketch.mirror(mirrorLine = cline_v, 
                          objectList = objects_mirror)
            x_offset_t = mc.x_offset
            twist_angle_t = mc.twist_angle
        #    twist_angle = -1.0 * twist_angle
        elif mc.flip == 'No':
            x_offset_t = -1.0 * mc.x_offset
            twist_angle_t = -1.0 * mc.twist_angle
        sketch.move(objectList = objects_all, 
                    vector = (x_offset_t, 0.0))
        sketch.scale(objectList = objects_all, 
                     scaleCenter = (0.0, 0.0), 
                     scaleValue = mc.chord_length)
        sketch.rotate(objectList = objects_all, 
                      centerPoint = (0.0, 0.0), 
                      angle = twist_angle_t)
        
        g = sketch.geometry
        
        # Get new coordinates of dividing points
        sgm_divpt_lps_new = []
        for i in sgm_id_lps_out:
            vi = g[i].getVertices()
            v_near_le = vi[1].coords
            v_near_te = vi[0].coords
            sgm_divpt_lps_new.append(v_near_le)
        sgm_divpt_lps_new.append(v_near_te)
        sgm_divpt_hps_new = []
        for i in sgm_id_hps_out:
            vi = g[i].getVertices()
            v_near_le = vi[0].coords
            v_near_te = vi[1].coords
            sgm_divpt_hps_new.append(v_near_le)
        sgm_divpt_hps_new.append(v_near_te)
        
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Make a copy for the fillings later
        if nfills != 0:
            sf_name = project_name + '_sketch_fill'
            sf = model.ConstrainedSketch(name = sf_name, 
                                         objectToCopy = model.sketches[ss_name])
            
        
        # ----------------------------------------------------------------------
        # Offset the total thickness of each layup
        
        g = sketch.geometry
        sgm_id_lps_in = []
        for i, sid in enumerate(sgm_id_lps_out):
            s = g[sid]
            lyp_id = sgm_pt_id_lps[i][2]
            t = mc.layups[lyp_id][0]
            if mc.flip == 'No':
                sketch.offset(objectList = (s,), distance = t, side = LEFT)
            elif mc.flip == 'Yes':
                sketch.offset(objectList = (s,), distance = t, side = RIGHT)
            g = sketch.geometry
            gk = g.keys()
            sgm_id_lps_in.append(gk[-1])
            
        g = sketch.geometry    
        sgm_id_hps_in = []
        for i, sid in enumerate(sgm_id_hps_out):
            s = g[sid]
            lyp_id = sgm_pt_id_hps[i][2]
            t = mc.layups[lyp_id][0]
            if mc.flip == 'No':
                sketch.offset(objectList = (s,), distance = t, side = LEFT)
            elif mc.flip == 'Yes':
                sketch.offset(objectList = (s,), distance = t, side = RIGHT)
            g = sketch.geometry
            gk = g.keys()
            sgm_id_hps_in.append(gk[-1])
        
        # ----------------------------------------------------------------------
        # Trim the trailing edge
        g = sketch.geometry
        gid_lps = sgm_id_lps_in[-1]
        gid_hps = sgm_id_hps_in[-1]
        sgm_id_lps_in.remove(sgm_id_lps_in[-1])
        sgm_id_hps_in.remove(sgm_id_hps_in[-1])
        [new_l, new_h] = trimIntersectCurves(sketch, gid_lps, 2, gid_hps, 1, (1.0, 0.0))
        sgm_id_lps_in.append(new_l)
        sgm_id_hps_in.append(new_h)
        
        # ----------------------------------------------------------------------
        # Get the two vertices for each inner curve
        # Get the vertices closer to the outer curve
        g = sketch.geometry
        v_lps_in = []
        for i in sgm_id_lps_in:
    #        s = segments_offset_curve_lps[i]
            s = g[i]
            v = s.getVertices()
            v_near_le = v[1].coords
            v_near_te = v[0].coords
            v_lps_in.append([v_near_le, v_near_te])
        fill_side_pts.append(v_lps_in[0][0])
        
        v_near_lps = [v_lps_in[0][0]]
        for i in range(len(v_lps_in) - 1):
            v1 = v_lps_in[i][1]
            v2  = v_lps_in[i+1][0]
            v0 = sgm_divpt_lps_new[i+1]
            d1 = findTwoPointsDistance(v0, v1)
            d2 = findTwoPointsDistance(v0, v2)
            if d1 < d2:
                v_near_lps.append(v1)
            elif d1 > d2:
                v_near_lps.append(v2)
            elif d1 == d2:
                v_near_lps.append(v1)
        v_near_lps.append(v_lps_in[-1][-1])
            
        v_hps_in = []
        for i in sgm_id_hps_in:
    #        s = segments_offset_curve_hps[i]
            s = g[i]
            v = s.getVertices()
            v_near_le = v[0].coords
            v_near_te = v[1].coords
            v_hps_in.append([v_near_le, v_near_te])
        
        v_near_hps = [v_hps_in[0][0]]
        for i in range(len(v_hps_in) - 1):
            v1 = v_hps_in[i][1]
            v2  = v_hps_in[i+1][0]
            v0 = sgm_divpt_hps_new[i+1]
            d1 = findTwoPointsDistance(v0, v1)
            d2 = findTwoPointsDistance(v0, v2)
            if d1 < d2:
                v_near_hps.append(v1)
            elif d1 > d2:
                v_near_hps.append(v2)
            elif d1 == d2:
                v_near_hps.append(v1)
        v_near_hps.append(v_hps_in[-1][-1])
        
        # Connet inner curve
        for i in range(len(v_lps_in) - 1):
            v_start = v_lps_in[i][1]
            v_end = v_lps_in[i+1][0]
            sketch.Line(point1 = v_start, point2 = v_end)
        
        for i in range(len(v_hps_in) - 1):
            v_start = v_hps_in[i][1]
            v_end = v_hps_in[i+1][0]
            sketch.Line(point1 = v_start, point2 = v_end)
            
        g = sketch.geometry
        
        # -----------------------------------------------------------------------
        # Sketch the mask
        # -----------------------------------------------------------------------
        
        if nwebs != 0:
            pt1 = (-mc.chord_length, mc.chord_length)
            pt2 = (mc.chord_length, -mc.chord_length)
            sm.rectangle(point1 = pt1, point2 = pt2)
            
            gm = sm.geometry
            gmk = gm.keys()
            objects_mirror = []
            for k in gmk:
                if k != cline_v.id:
                    objects_mirror.append(gm[k])
            objects_all = objects_mirror + [gm[cline_v.id],]
            objects_mirror = tuple(objects_mirror)
            objects_all = tuple(objects_all)
            
            if mc.flip == 'Yes':
                sm.mirror(mirrorLine = gm[cline_v.id], 
                          objectList = objects_mirror)
                x_offset_t = mc.x_offset
                twist_angle_t = mc.twist_angle
            #    twist_angle = -1.0 * twist_angle
            elif mc.flip == 'No':
                x_offset_t = -1.0 * mc.x_offset
                twist_angle_t = -1.0 * mc.twist_angle
            sm.move(objectList = objects_all, 
                    vector = (x_offset_t, 0.0))
            sm.scale(objectList = objects_all, 
                     scaleCenter = (0.0, 0.0), 
                     scaleValue = mc.chord_length)
            sm.rotate(objectList = objects_all, 
                      centerPoint = (0.0, 0.0), 
                      angle = twist_angle_t)
        
        # -----------------------------------------------------------------------
        # Sketch the webs
        # -----------------------------------------------------------------------
        
        if nwebs != 0:
            sw_name = project_name + '_sketch_webs_trim0'
            sw = model.ConstrainedSketch(name = sw_name, sheetSize = sheet_size)
            sw.sketchOptions.setValues(gridOrigin = (0.0, 0.0))
            
            cline_vw = sw.ConstructionLine(point1 = (0.0, -1.0),                # Vertical reference line at the leading edge
                                           point2 = (0.0, 1.0))
            
            ymin = 0.0
            ymax = 0.0
            for p in coord:
                if p[1] < ymin:
                    ymin = p[1]
                if p[1] > ymax:
                    ymax = p[1]
            
            wcl_id = {}
            for k, v in webs.items():
                x0 = v[0]
                y0 = v[1]
                angle = v[2]
                angle = math.radians(angle - 90.0)
                slope = math.tan(angle)
                y1 = 1.5 * ymin
                x1 = slope * (y1 - y0) + x0
                y2 = 1.5 * ymax
                x2 = slope * (y2 - y0) + x0
                pt1 = (x1, y1)
                pt2 = (x2, y2)
                wcl = sw.Line(point1 = pt1, point2 = pt2)                            # Draw center line of the web
                wcl_id[k] = wcl.id
                
            gw = sw.geometry
            gwk = gw.keys()
            objects_mirror = []
            for k in gwk:
                if k != cline_vw.id:
                    objects_mirror.append(gw[k])
            objects_all = objects_mirror + [gw[cline_vw.id],]
            objects_mirror = tuple(objects_mirror)
            objects_all = tuple(objects_all)
            
            if mc.flip == 'Yes':
                sw.mirror(mirrorLine = gw[cline_vw.id], 
                          objectList = objects_mirror)
                x_offset_t = mc.x_offset
                twist_angle_t = mc.twist_angle
            #    twist_angle = -1.0 * twist_angle
            elif mc.flip == 'No':
                x_offset_t = -1.0 * mc.x_offset
                twist_angle_t = -1.0 * mc.twist_angle
            sw.move(objectList = objects_all, 
                    vector = (x_offset_t, 0.0))
            sw.scale(objectList = objects_all, 
                     scaleCenter = (0.0, 0.0), 
                     scaleValue = mc.chord_length)
            sw.rotate(objectList = objects_all, 
                      centerPoint = (0.0, 0.0), 
                      angle = twist_angle_t)
                      
            gw = sw.geometry
            web_ept = []
            web_eid = []
            for k, v in webs.items():
                lyp_id = webs_layup[k-1]
                tt = mc.layups[lyp_id][0]
                t = tt / 2
                if mc.flip == 'No':
                    sw.offset(objectList = (gw[wcl_id[k]],), distance = t, side = LEFT)            # Offset the edge near LE
                    sw.offset(objectList = (gw[wcl_id[k]],), distance = t, side = RIGHT)           # Offset the edge near TE
                elif mc.flip == 'Yes':
                    sw.offset(objectList = (gw[wcl_id[k]],), distance = t, side = RIGHT)           # Offset the edge near LE
                    sw.offset(objectList = (gw[wcl_id[k]],), distance = t, side = LEFT)            # Offset the edge near TE
                gw = sw.geometry
                gwk = gw.keys()
        #        web_id_c = gwk[-3]
                web_id_near_le = gwk[-2]
                web_id_near_te = gwk[-1]
                web_eid.append([web_id_near_le, web_id_near_te])
                vle = gw[web_id_near_le].getVertices()
                vle1 = vle[0].coords
                vle2 = vle[1].coords
                vre = gw[web_id_near_te].getVertices()
                vte1 = vre[0].coords
                vte2 = vre[1].coords
                xle = (vle1[0] + vle2[0]) / 2
                yle = (vle1[1] + vle2[1]) / 2
                xte = (vte1[0] + vte2[0]) / 2
                yte = (vte1[1] + vte2[1]) / 2
                temp = [(xle, yle), (xte, yte)]
                web_ept.append(temp)
                sw.Line(point1 = vle1, point2 = vte1)
                sw.Line(point1 = vle2, point2 = vte2)

                v = gw[wcl_id[k]].getVertices()
                v1, v2 = v[0].coords, v[1].coords
                fill_partition_v.append([v1, v2])
                fill_side_pts.append((xle, yle))
                fill_side_pts.append((xte, yte))
                
                sw.delete(objectList = (gw[wcl_id[k]],))
                
            fill_side_pts.append(v_lps_in[-1][-1])
        
        for i in range(len(fill_side_pts)/2):
            pt1 = fill_side_pts[2*i]
            pt2 = fill_side_pts[2*i+1]
            x1, y1 = pt1[0], pt1[1]
            x2, y2 = pt2[0], pt2[1]
            xf = x1 + (x2 - x1) / 10.0
            yf = y1 + (y2 - y1) / 10.0
            fill_fpt.append((xf, yf))
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Sketch partition
    # =======================================================================
    if (tnt in steps[2:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Sketching partition...  ' + time_now + '\n')
        milestone('Sketching partition...')
    #    print 'Sketching partition...'
        
        # Copy the sketch
        ssp_name = project_name + '_sketch_surface_layers'
        ssp = model.ConstrainedSketch(name = ssp_name, 
                                      objectToCopy = model.sketches[ss_name])
        
        sec_3 = sec_o
        sec_31 = time.time()
        f_log.write('    -> Copy the sketch: ' + str(sec_31 - sec_3) + '\n')
    #    print '    -> Copy the sketch: ', str(sec_31 - sec_3)
        gp = ssp.geometry
        
        ssp.Line(point1 = sgm_divpt_lps_new[0], point2 = v_near_lps[0])
        for i in range(1, len(v_near_lps) - 1):
            ps = sgm_divpt_lps_new[i]
            pe = v_near_lps[i]
            ssp.Line(point1 = ps, point2 = pe)
        for i in range(1, len(v_near_hps) - 1):
            ps = sgm_divpt_hps_new[i]
            pe = v_near_hps[i]
            ssp.Line(point1 = ps, point2 = pe)
        
        sec_32 = time.time()
        f_log.write('    -> Draw segment walls: ' + str(sec_32 - sec_31) + '\n')
    #    print '    -> Draw segment walls: ', str(sec_32 - sec_31)
        gp = ssp.geometry
        
        sgm_lyr_id_lps = []
        for i in range(len(sgm_id_lps_out) - 1):
            sgm_id = sgm_id_lps_out[i]
            sgm_lyr_id_lps.append([sgm_id])
            sgm = gp[sgm_id]
            lyp_id = sgm_pt_id_lps[i][2]
            lyp = mc.layups[lyp_id][1]
            t = 0
            for j in range(len(lyp) - 1):
                t += lyp[j][0]
                if mc.flip == 'No':
                    ssp.offset(objectList = (sgm,), distance = t, side = LEFT)
                elif mc.flip == 'Yes':
                    ssp.offset(objectList = (sgm,), distance = t, side = RIGHT)
                gpk = ssp.geometry.keys()
                sgm_lyr_id_lps[i].append(gpk[-1])
            sgm_lyr_id_lps[i].append(sgm_id_lps_in[i])
        sec_33 = time.time()
        f_log.write('    -> Draw layers of the lower pressure surface: ' + str(sec_33 - sec_32) + '\n')
    #    print '    -> Draw layers of the lower pressure surface: ', str(sec_33 - sec_32)
        
        sgm_lyr_id_hps = []
        for i in range(len(sgm_id_hps_out) - 1):
            sgm_id = sgm_id_hps_out[i]
            sgm_lyr_id_hps.append([sgm_id])
            sgm = gp[sgm_id]
            lyp_id = sgm_pt_id_hps[i][2]
            lyp = mc.layups[lyp_id][1]
            t = 0
            for j in range(len(lyp) - 1):
                t += lyp[j][0]
                if mc.flip == 'No':
                    ssp.offset(objectList = (sgm,), distance = t, side = LEFT)
                elif mc.flip == 'Yes':
                    ssp.offset(objectList = (sgm,), distance = t, side = RIGHT)
                gpk = ssp.geometry.keys()
                sgm_lyr_id_hps[i].append(gpk[-1])
            sgm_lyr_id_hps[i].append(sgm_id_hps_in[i])
        sec_34 = time.time()
        f_log.write('    -> Draw layers of the higher pressure surface: ' + str(sec_34 - sec_33) + '\n')
    #    print '    -> Draw layers of the higher pressure surface: ', str(sec_34 - sec_33)
        
        gp = ssp.geometry
        
        # Partition sketch for the trailing edge
        lyp_id_lps = sgm_pt_id_lps[-1][2]
        lyp_id_hps = sgm_pt_id_hps[-1][2]
        lyp_lps = mc.layups[lyp_id_lps][1]
        lyp_hps = mc.layups[lyp_id_hps][1]
        temp_lps_id = sgm_id_lps_out[-1]
        temp_hps_id = sgm_id_hps_out[-1]
        sgm_lyr_id_lps.append([temp_lps_id])
        sgm_lyr_id_hps.append([temp_hps_id])
        temp_lps = gp[temp_lps_id]
        temp_hps = gp[temp_hps_id]
        tl = 0
        th = 0
        temp_curve_id_list = [temp_lps_id]
        for i in range(len(lyp_lps) - 1):
            tl += lyp_lps[i][0]
            th += lyp_hps[i][0]
            if mc.flip == 'No':
                ssp.offset(objectList = (temp_lps,), distance = tl, side = LEFT)
                ssp.offset(objectList = (temp_hps,), distance = th, side = LEFT)
            elif mc.flip == 'Yes':
                ssp.offset(objectList = (temp_lps,), distance = tl, side = RIGHT)
                ssp.offset(objectList = (temp_hps,), distance = th, side = RIGHT)
            gp = ssp.geometry
            gpk = gp.keys()
            id_1 = gpk[-2]
            id_2 = gpk[-1]
            [new_id_lps, new_id_hps] = trimIntersectCurves(ssp, id_1, 2, id_2, 1, (1.0, 0.0))
            sgm_lyr_id_lps[-1].append(new_id_lps)
            sgm_lyr_id_hps[-1].append(new_id_hps)
            temp_curve_id_list.append(new_id_lps)
        temp_curve_id_list.append(sgm_id_lps_in[-1])
        sgm_lyr_id_lps[-1].append(sgm_id_lps_in[-1])
        sgm_lyr_id_hps[-1].append(sgm_id_hps_in[-1])
        sec_35 = time.time()
        f_log.write('    -> Draw layers of the trailing edge: ' + str(sec_35 - sec_34) + '\n')
    #    print '    -> Draw layers of the trailing edge: ', str(sec_35 - sec_34)
        
        gp = ssp.geometry
        for i in range(len(temp_curve_id_list) - 1):
            id_1 = temp_curve_id_list[i]
            id_2 = temp_curve_id_list[i+1]
            v = gp[id_1].getVertices()
            v_1 = v[0].coords
            v = gp[id_2].getVertices()
            v_2 = v[0].coords
            ssp.Line(point1 = v_1, point2 = v_2)
        sec_36 = time.time()
        f_log.write('    -> Draw segment wall of the trailing edge: ' + str(sec_36 - sec_35) + '\n')
    #    print '    -> Draw segment wall of the trailing edge: ', str(sec_36 - sec_35)
        
        
        # -----------------------------------------------------------------------
        # Sketch partitions for webs
        # -----------------------------------------------------------------------
        
        if nwebs != 0:
            swp_name = sw_name + '_sketch_webs_layers'
            swp = model.ConstrainedSketch(name = swp_name, 
                                         objectToCopy = model.sketches[sw_name])
            gwp = swp.geometry
            web_lyr_pt = [[web_ept[0][0]],[web_ept[1][0]]]
            for i in range(len(webs_layup)):
                lyp_id = webs_layup[i]
                lyp = mc.layups[lyp_id][1]
                t = 0.0
                for j in range(len(lyp) - 1):
                    t += lyp[j][0]
                    if mc.flip == 'No':
                        swp.offset(objectList = (gwp[web_eid[i][0]],), distance = t, side = RIGHT)
                    elif mc.flip == 'Yes':
                        swp.offset(objectList = (gwp[web_eid[i][0]],), distance = t, side = LEFT)
                    gwp = swp.geometry
                    gwpk = gwp.keys()
                    lid = gwpk[-1]
                    v = gwp[lid].getVertices()
                    v1 = v[0].coords
                    v2 = v[1].coords
                    xm = (v1[0] + v2[0]) / 2
                    ym = (v1[1] + v2[1]) / 2
                    web_lyr_pt[i].append((xm, ym))
                web_lyr_pt[i].append(web_ept[i][1])
                
            web_lyr_fpt = []
            for i in range(len(web_lyr_pt)):
                webi = web_lyr_pt[i]
                temp = []
                for j in range(len(webi) - 1):
                    vl = webi[j]
                    vr = webi[j+1]
                    xm = (vl[0] + vr[0]) / 2
                    ym = (vl[1] + vr[1]) / 2
                    temp.append((xm, ym))
                web_lyr_fpt.append(temp)
        
        # ----------------------------------------------------------------------
        # Sketch partition for fillings
        # ----------------------------------------------------------------------
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Create part and assembly
    # =======================================================================
    if (tnt in steps[3:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Creating part and assembly...  ' + time_now + '\n')
        milestone('Creating part and assembly...')
    #    print 'Creating part and assembly...'
        
        ps_name = project_name + '_part_surface'
        ps = createPartYZ(model_name, ps_name)
        ps = createFirstShell(model, ps, ss)
        ps = partitionPart(model, ps, ssp)
        
        is0_name = ps_name + '-1'
        a = model.rootAssembly
        a.DatumCsysByDefault(CARTESIAN)
        a.Instance(name = is0_name, part = ps, dependent = ON)
        pa_name = ps_name
        
#        print pa_name
        
        if nwebs != 0:
            sm = model.sketches[sm_name]
            sw = model.sketches[sw_name]
            swp = model.sketches[swp_name]
            pm_name = project_name + '_part_mask'
            pw0_name = project_name + '_part_web_trim0'

            pm = createPartYZ(model_name, pm_name)
            pm = createFirstShell(model, pm, sm)

            pw = createPartYZ(model_name, pw0_name)
            pw = createFirstShell(model, pw, sw)
            pw = partitionPart(model, pw, swp)
            
            # Cut webs by mask
            im_name = pm_name + '-1'
            iw0_name = pw0_name + '-1'
            is1_name = ps_name + '_copy-1'
            a.Instance(name = im_name, part = pm, dependent = ON)
            a.Instance(name = iw0_name, part = pw, dependent = ON)
            a.Instance(name = is1_name, part = ps, dependent = ON)
            pw1_name = project_name + '_part_web_trim1'
            iw1_name = pw1_name + '-1'
            a.InstanceFromBooleanCut(name = pw1_name, 
                                     instanceToBeCut = a.instances[iw0_name], 
                                     cuttingInstances = (a.instances[im_name],), 
                                     originalInstances = DELETE)
                                     
            pwf_name = project_name + '_part_web'
            iwf_name = pwf_name + '-1'
            a.InstanceFromBooleanCut(name = pwf_name, 
                                     instanceToBeCut = a.instances[iw1_name], 
                                     cuttingInstances = (a.instances[is1_name],), 
                                     originalInstances = DELETE)
                                     
            psw_name = pa_name + '_web'
            a.InstanceFromBooleanMerge(name = psw_name, 
                                       instances = (a.instances[is0_name], a.instances[iwf_name]), 
                                       keepIntersections = ON, 
                                       originalInstances = DELETE, 
                                       domain = GEOMETRY)
                                       
            del model.parts[ps_name]
            del model.parts[pm_name]
            del model.parts[pw0_name]
            del model.parts[pw1_name]
            del model.parts[pwf_name]
            
            pa_name = psw_name
            a.regenerate()
            
        if nfills != 0:
            pf_name = project_name + '_part_fill_cut0'
            pf = createPartYZ(model_name, pf_name)
            pf = createFirstShell(model, pf, sf)
            
            d, ff = pf.datums, pf.faces
            tf = pf.MakeSketchTransform(sketchPlane = ff[0], sketchUpEdge = d[2], 
                                        sketchPlaneSide = SIDE1, origin = (0.0, 0.0, 0.0))
            sf1 = model.ConstrainedSketch(name = '__profile__', sheetSize = sheet_size, 
                                          transform = tf)
            sf1.setPrimaryObject(option = SUPERIMPOSE)
            pf.projectReferencesOntoSketch(sketch = sf1, filter = COPLANAR_EDGES)
            for vs in fill_partition_v:
                pt1, pt2 = vs[0], vs[1]
                sf1.Line(point1 = pt1, point2 = pt2)
            pf.PartitionFaceBySketch(faces = tuple(ff), sketchUpEdge = d[2], sketch = sf1)
            sf1.unsetPrimaryObject()
            del sf1
            
            fill_fpt_del = fill_fpt[:]
            fill_fpt = {}
            for i in range(len(fills.keys())):
                fno = fills[i+1][0]
                fill_fpt[i+1] = fill_fpt_del[fno-1]
                del fill_fpt_del[fno-1]
            ff = pf.faces
            for pt in fill_fpt_del:
                pt = (0.0,) + pt
                fff = ff.findAt(coordinates = pt)
                pf.RemoveFaces(faceList = (fff,), deleteCells = False)
            psw = model.parts[pa_name]
            isw_name = psw_name + '-1'
            isw1_name = psw_name + '_copy-1'
            if1_name = pf_name + '-1'
            a.Instance(name = isw1_name, part = psw, dependent = ON)
            a.Instance(name = if1_name, part = pf, dependent = ON)
            pff_name = project_name + '_part_fill'
            iff_name = pff_name + '-1'
            a.InstanceFromBooleanCut(name = pff_name, 
                                     instanceToBeCut = a.instances[if1_name], 
                                     cuttingInstances = (a.instances[isw1_name],), 
                                     originalInstances = DELETE)
            pswf_name = pa_name + '_fill'
            a.InstanceFromBooleanMerge(name = pswf_name, 
                                       instances = (a.instances[isw_name], a.instances[iff_name]), 
                                       keepIntersections = ON, 
                                       originalInstances = DELETE, 
                                       domain = GEOMETRY)
            del model.parts[psw_name]
            del model.parts[pf_name]
            del model.parts[pff_name]
            
            pa_name = pswf_name
   
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Find layer faces
    # =======================================================================
    if (tnt in steps[4:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Finding layer faces...  ' + time_now + '\n')
        milestone('Finding layer faces...')
    #    print 'Finding layer faces...'
        
        # Copy the sketch
        st_name = project_name + '_temp'
        st = model.ConstrainedSketch(name = st_name, 
                                     objectToCopy = model.sketches[ssp_name])
        
        gt = st.geometry
        sgm_lyr_fpt_lps = []
        sgm_ept_lps_out = []
        for i in range(len(sgm_id_lps_out)):
            pt_l = sgm_divpt_lps_new[i]
            pt_r = sgm_divpt_lps_new[i+1]
            x01 = pt_l[0]
            y01 = pt_l[1]
            x02 = pt_r[0]
            y02 = pt_r[1]
            xm1 = (x01 + x02) / 2
            ym1 = (y01 + y02) / 2
            pt_m1 = (xm1, ym1)
            slope = (y02 - y01) / (x02 - x01)
            slope_m = -1 / slope
            ym2 = 0.0
            xm2 = (ym2 - ym1) / slope_m + xm1
            pt_m2 = (xm2, ym2)
            cline_t = st.ConstructionLine(point1 = pt_m1, point2 = pt_m2)
            xt = xm2 - xm1
            yt = ym2 - ym1
            theta = math.atan2(yt, xt)
            sid = sgm_id_lps_out[i]
            st.breakCurve(curve1 = gt[sid], point1 = pt_m1, 
                          curve2 = cline_t, point2 = pt_m1)
            gt = st.geometry
            gtk = gt.keys()
            c0 = gt[gtk[-1]]
            v0 = c0.getVertices()
            v0 = v0[0].coords
            x0 = v0[0]
            y0 = v0[1]
            sgm_ept_lps_out.append((x0, y0))
            lyp_id = sgm_pt_id_lps[i][2]
            lyp = mc.layups[lyp_id][1]
            sgm_lyr_fpt_lps.append([])
            t0 = 0.0
            for j in range(len(lyp)):
                t = lyp[j][0] / 2 + t0
                x = x0 + math.cos(theta) * t
                y = y0 + math.sin(theta) * t
                sgm_lyr_fpt_lps[i].append((x, y))
                t0 += lyp[j][0]
        
        gt = st.geometry
        sgm_lyr_fpt_hps = []
        sgm_ept_hps_out = []
        for i in range(len(sgm_id_hps_out)):
            pt_l = sgm_divpt_hps_new[i]
            pt_r = sgm_divpt_hps_new[i+1]
            x01 = pt_l[0]
            y01 = pt_l[1]
            x02 = pt_r[0]
            y02 = pt_r[1]
            xm1 = (x01 + x02) / 2
            ym1 = (y01 + y02) / 2
            pt_m1 = (xm1, ym1)
            slope = (y02 - y01) / (x02 - x01)
            slope_m = -1 / slope
            ym2 = 0.0
            xm2 = (ym2 - ym1) / slope_m + xm1
            pt_m2 = (xm2, ym2)
            cline_t = st.ConstructionLine(point1 = pt_m1, point2 = pt_m2)
            xt = xm2 - xm1
            yt = ym2 - ym1
            theta = math.atan2(yt, xt)
            sid = sgm_id_hps_out[i]
            st.breakCurve(curve1 = gt[sid], point1 = pt_m1, 
                          curve2 = cline_t, point2 = pt_m1)
            gt = st.geometry
            gtk = gt.keys()
            c0 = gt[gtk[-1]]
            v0 = c0.getVertices()
            v0 = v0[0].coords
            x0 = v0[0]
            y0 = v0[1]
            sgm_ept_hps_out.append((x0, y0))
            lyp_id = sgm_pt_id_hps[i][2]
            lyp = mc.layups[lyp_id][1]
            sgm_lyr_fpt_hps.append([])
            t0 = 0.0
            for j in range(len(lyp)):
                t = lyp[j][0] / 2 + t0
                x = x0 + math.cos(theta) * t
                y = y0 + math.sin(theta) * t
                sgm_lyr_fpt_hps[i].append((x, y))
                t0 += lyp[j][0]
                
        del model.sketches[st_name]
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Import materials
    # =======================================================================
    if (tnt in steps[5:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Importing materials...  ' + time_now + '\n')
        milestone('Importing materials...')
    #    print 'Importing materials...'
        
        for mtr in mtr_root:
            material_id   = int(mtr.find('id').text)
            material_name = mtr.find('name').text
            material_type = mtr.get('type')
            density = mtr.find('density')
            m = model.Material(name = material_name)
            if not density == None:
                dens = float(density.text)
                m.Density(table = ((dens,),))
            if material_type == 'ISOTROPIC':
                e = float(mtr.find('e').text)
                nu = float(mtr.find('nu').text)
                prop = ((e, nu),)
                m.Elastic(type = ISOTROPIC, table = prop)
                sn = material_name + '_0.0'
                model.HomogeneousSolidSection(name = sn, material = material_name, thickness = None)
            elif material_type == 'ENGINEERING CONSTANTS':
                e1 = float(mtr.find('e1').text)
                e2 = float(mtr.find('e2').text)
                e3 = float(mtr.find('e3').text)
                g12 = float(mtr.find('g12').text)
                g13 = float(mtr.find('g13').text)
                g23 = float(mtr.find('g23').text)
                nu12 = float(mtr.find('nu12').text)
                nu13 = float(mtr.find('nu13').text)
                nu23 = float(mtr.find('nu23').text)
                prop = ((e1, e2, e3, nu12, nu13, nu23, g12, g13, g23),)
                m.Elastic(type = ENGINEERING_CONSTANTS, table = prop)
            elif material_type == 'ORTHOTROPIC':
                d1111 = float(mtr.find('d1111').text)
                d1122 = float(mtr.find('d1122').text)
                d2222 = float(mtr.find('d2222').text)
                d1133 = float(mtr.find('d1133').text)
                d2233 = float(mtr.find('d2233').text)
                d3333 = float(mtr.find('d3333').text)
                d1212 = float(mtr.find('d1212').text)
                d1313 = float(mtr.find('d1313').text)
                d2323 = float(mtr.find('d2323').text)
                prop = ((d1111, d1122, d2222, 
                         d1133, d2233, d3333, 
                         d1212, d1313, d2323),)
                m.Elastic(type = ORTHOTROPIC, table = prop)
            elif material_type == 'ANISOTROPIC':
                d1111 = float(mtr.find('d1111').text)
                d1122 = float(mtr.find('d1122').text)
                d2222 = float(mtr.find('d2222').text)
                d1133 = float(mtr.find('d1133').text)
                d2233 = float(mtr.find('d2233').text)
                d3333 = float(mtr.find('d3333').text)
                d1112 = float(mtr.find('d1112').text)
                d2212 = float(mtr.find('d2212').text)
                d3312 = float(mtr.find('d3312').text)
                d1212 = float(mtr.find('d1212').text)
                d1113 = float(mtr.find('d1113').text)
                d2213 = float(mtr.find('d2213').text)
                d3313 = float(mtr.find('d3313').text)
                d1213 = float(mtr.find('d1213').text)
                d1313 = float(mtr.find('d1313').text)
                d1123 = float(mtr.find('d1123').text)
                d2223 = float(mtr.find('d2223').text)
                d3323 = float(mtr.find('d3323').text)
                d1223 = float(mtr.find('d1223').text)
                d1323 = float(mtr.find('d1323').text)
                d2323 = float(mtr.find('d2323').text)
                prop = ((d1111, d1122, d2222, d1133, d2233, d3333, 
                         d1112, d2212, d3312, d1212, d1113, d2213, 
                         d3313, d1213, d1313, d1123, d2223, d3323, 
                         d1223, d1323, d2323),)
                m.Elastic(type = ANISOTROPIC, table = prop)
                
        for k, v in mc.layer_types.items():
            lyt_id = k
            mtr_id = v[0]
            lyt_name = mc.lytid_name[lyt_id]
            mtr_name = mc.mid_name[mtr_id]
            model.HomogeneousSolidSection(name = lyt_name, material = mtr_name, thickness = None)
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    # =======================================================================
    # Create and assign sections
    # =======================================================================
    if (tnt in steps[6:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Creating and assigning sections...  ' + time_now + '\n')
        milestone('Creating and assigning sections...')
    #    print 'Creating and assigning sections...'
        
        p = model.parts[pa_name]
        f = p.faces
        sgm_lyr_fid_lps = []
        for i in range(len(sgm_pt_id_lps)):
            lyp_id = sgm_pt_id_lps[i][2]
            lyp = mc.layups[lyp_id][1]
            fids = []
            for j in range(len(lyp)):
                lyt_id = lyp[j][1]
                sn = mc.lytid_name[lyt_id]
                pt = sgm_lyr_fpt_lps[i][j]
                pt = (0.0,) + pt                  # (x, y, z)
                ff = f.findAt((pt,))    # sequence of Face object
                fids.append(ff[0].index)
                rn = sn + '/lps-' + str(i+1) + '-' + str(j+1)
                rn = rn.replace('.', 'd')
                rg = p.Set(name = rn, faces = ff)
                p.SectionAssignment(region = rg, sectionName = sn)
            sgm_lyr_fid_lps.append(fids)
        sgm_lyr_fid_hps = []
        for i in range(len(sgm_pt_id_hps)):
            lyp_id = sgm_pt_id_hps[i][2]
            lyp = mc.layups[lyp_id][1]
            fids = []
            for j in range(len(lyp)):
                lyt_id = lyp[j][1]
                sn = mc.lytid_name[lyt_id]
                pt = sgm_lyr_fpt_hps[i][j]
                pt = (0.0,) + pt                  # (x, y, z)
                ff = f.findAt((pt,))    # sequence of Face object
                fids.append(ff[0].index)
                rn = sn + '/hps-' + str(i+1) + '-' + str(j+1)
                rn = rn.replace('.', 'd')
                rg = p.Set(name = rn, faces = ff)
                p.SectionAssignment(region = rg, sectionName = sn)
            sgm_lyr_fid_hps.append(fids)
                
        web_lyr_fid = []
        if nwebs != 0:
            for i in range(len(webs_layup)):
                lyp_id = webs_layup[i]
                lyp = mc.layups[lyp_id][1]
                fids = []
                for j in range(len(lyp)):
                    lyt_id = lyp[j][1]
                    sn = mc.lytid_name[lyt_id]
                    pt = web_lyr_fpt[i][j]
                    pt = (0.0,) + pt
                    ff = f.findAt((pt,))
                    fids.append(ff[0].index)
                    rn = sn + '/web-' + str(i+1) + '-' + str(j+1)
                    rn = rn.replace('.', 'd')
                    rg = p.Set(name = rn, faces = ff)
                    p.SectionAssignment(region = rg, sectionName = sn)
                web_lyr_fid.append(fids)

        if nfills != 0:
            fill_fid = []
            for k, v in fill_fpt.items():
                mtr_id = fills[k][1]
                mtr_name = mc.mid_name[mtr_id]
                sn = mtr_name + '_0.0'
                pt = (0.0,) + v
                ff = f.findAt((pt,))
                fill_fid.append(ff[0].index)
                rn = sn + '/fill-' + str(k)
                rn = rn.replace('.', 'd')
                rg = p.Set(name = rn, faces = ff)
                p.SectionAssignment(region = rg, sectionName = sn)
        
        model.rootAssembly.regenerate()
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Assign orientation
    # =======================================================================
    if (tnt in steps[7:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Assigning orientations...  ' + time_now + '\n')
        milestone('Assigning orientations...')
    #    print 'Assigning orientations...'
        
        p = model.parts[pa_name]
        f = p.faces
        e = p.edges
        for i in range(len(sgm_ept_lps_out)):
            ept = (0.0,) + sgm_ept_lps_out[i]
            edg = e.findAt((ept,))
            rn = 'set-edge-lps-' + str(i+1)
            par = p.Set(edges = edg, name = rn)
            for fid in sgm_lyr_fid_lps[i]:
                ffs = f[fid:fid+1]
                rg = Region(faces = ffs)
                p.MaterialOrientation(region = rg, 
                                      orientationType = DISCRETE, 
                                      axis = AXIS_3, 
                                      normalAxisDefinition = VECTOR, 
                                      normalAxisVector = (0.0, 0.0, 1.0), 
                                      flipNormalDirection = False, 
                                      normalAxisDirection = AXIS_3, 
                                      primaryAxisDefinition = EDGE, 
                                      primaryAxisRegion = par, 
                                      primaryAxisDirection = AXIS_1, 
                                      flipPrimaryDirection = True)
                                  
        for i in range(len(sgm_ept_hps_out)):
            ept = (0.0,) + sgm_ept_hps_out[i]
            edg = e.findAt((ept,))
            rn = 'set-edge-hps-' + str(i+1)
            par = p.Set(edges = edg, name = rn)
            for fid in sgm_lyr_fid_hps[i]:
                ffs = f[fid:fid+1]
                rg = Region(faces = ffs)
                p.MaterialOrientation(region = rg, 
                                      orientationType = DISCRETE, 
                                      axis = AXIS_3, 
                                      normalAxisDefinition = VECTOR, 
                                      normalAxisVector = (0.0, 0.0, 1.0), 
                                      flipNormalDirection = False, 
                                      normalAxisDirection = AXIS_3, 
                                      primaryAxisDefinition = EDGE, 
                                      primaryAxisRegion = par, 
                                      primaryAxisDirection = AXIS_1, 
                                      flipPrimaryDirection = True)
                                  
        if nwebs != 0:
            for i in range(len(web_ept)):
                ept = (0.0,) + web_ept[i][0]
                edg = e.findAt((ept,))
                rn = 'set-edge-web-' + str(i+1)
                par = p.Set(edges = edg, name = rn)
                for fid in web_lyr_fid[i]:
                    ffs = f[fid:fid+1]
                    rg = Region(faces = ffs)
                    p.MaterialOrientation(region = rg, 
                                          orientationType = DISCRETE, 
                                          axis = AXIS_3, 
                                          normalAxisDefinition = VECTOR, 
                                          normalAxisVector = (0.0, 0.0, 1.0), 
                                          flipNormalDirection = False, 
                                          normalAxisDirection = AXIS_3, 
                                          primaryAxisDefinition = EDGE, 
                                          primaryAxisRegion = par, 
                                          primaryAxisDirection = AXIS_1, 
                                          flipPrimaryDirection = True)
        
        model.rootAssembly.regenerate()
                         
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Generate mesh
    # =======================================================================
    if (tnt in steps[8:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Generating mesh...  ' + time_now + '\n')
        milestone('Generating mesh...')
    #    print 'Generating mesh...'
        
        p = model.parts[pa_name]
        p.seedPart(size = mesh_size, deviationFactor = 0.1, minSizeFactor = 0.1)
        f = p.faces
        p.generateMesh()
        
        model.rootAssembly.regenerate()
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Create job and write input
    # =======================================================================
    if (tnt in steps[9:]) or (tnt == 'all'):
        
        time_now = time.strftime('%H:%M:%S', time.localtime())
        f_log.write('--> Creating job and writing input...  ' + time_now + '\n')
        milestone('Creating job and writing input...')
    #    print 'Creating job and writing input...'
        
        job = mdb.Job(name = job_name, model = model_name)
        job.writeInput()
        
        sec_n = time.time()
        f_log.write('    Seconds spent: [{0:8.3f}]s\n'.format((sec_n - sec_o)))
        sec_o = sec_n
    
    
    # =======================================================================
    # Set view
    # =======================================================================
    if tnt == 'all':
        
        p = model.parts[pa_name]
        setView(p)
        cvp = session.viewports[session.currentViewportName]
        cvp.partDisplay.setValues(mesh = ON)
        cvp.partDisplay.meshOptions.setValues(meshTechnique = ON)
        cvp.enableMultipleColors()
        cvp.setColor(initialColor = '#BDBDBD')
        cmap = cvp.colorMappings['Section']
        cvp.setColor(colorMapping = cmap)
        cvp.disableMultipleColors()
        
    
    mdb.saveAs(pathName = cae_name)
    
    
    milestone('Done.')
    print 'Done.'
    sec_1 = time.time()
    f_log.write('\n')
    f_log.write('\n')
    f_log.write('>>> TOTAL TIME: [{0:8.3f}]s\n'.format((sec_1 - sec_0)))
    
    f_debug.close()
    f_log.close()
    
def createPartYZ(model_name, part_name):
    
    m = mdb.models[model_name]
    p = m.Part(name = part_name, dimensionality = THREE_D, type = DEFORMABLE_BODY)
    p.DatumPlaneByPrincipalPlane(principalPlane = YZPLANE, offset = 0.0)
    p.DatumAxisByPrincipalAxis(principalAxis = ZAXIS)
    
    return p
    
def createFirstShell(model, part, sketch):
    
    t = (0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    d = part.datums
    s = model.ConstrainedSketch(name = '__temp__', sheetSize = 100.0, transform = t)
    s.retrieveSketch(sketch)
    part.Shell(sketchPlane = d[1], sketchUpEdge = d[2], sketchPlaneSide = SIDE1, 
             sketchOrientation = RIGHT, sketch = s)
    del model.sketches['__temp__']
    part.regenerate()
    
    return part
    
def partitionPart(model, part, sketch):
    
    d, f = part.datums, part.faces
    t = part.MakeSketchTransform(sketchPlane = f[0], sketchUpEdge = d[2], 
                                 sketchPlaneSide = SIDE1, origin = (0.0, 0.0, 0.0))
    s = model.ConstrainedSketch(name = '__temp__', sheetSize = 100.0, transform = t)
    s.retrieveSketch(sketch)
    part.PartitionFaceBySketch(faces = tuple(f), sketchUpEdge = d[2], sketch = s)
    del model.sketches['__temp__']
    part.regenerate()
    
    return part