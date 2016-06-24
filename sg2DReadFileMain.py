# -*- coding: utf-8 -*-

import xml.etree.ElementTree as et
from sg2DAirfoil import *

def createSGfromFile(project_name, control_file):
    
    project = et.parse(control_file)
    project = project.getroot()
    
    sg_type = project.get('type')
    
    if sg_type == 'airfoil':
        createAirfoil(project_name, control_file)
    elif sg_type == 'pass':
        pass
    
    return 1