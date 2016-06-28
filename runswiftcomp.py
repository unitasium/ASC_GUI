import xml.etree.ElementTree as et
import sys
import os
from sg2DAirfoil import *
from scHomoMain import *


control_file = sys.argv[-1]

cwd      = os.path.dirname(control_file)
# log_name = os.path.join(cwd, 'Log.log')
# log      = open(log_name, 'w')

# log.write('Reading control file...\n')
control      = et.parse(control_file).getroot()
project_name = control.find('name').text
head_file    = control.find('head').text
airfoil_main = control.find('airfoil').text
input_only   = int(control.find('input_only').text)

# log.write('Reading head file...\n')
head           = et.parse(head_file).getroot()
analysis       = int(head.find('analysis').text)
specific_model = int(head.find('specific_model').text)
elem_flag      = int(head.find('elem_flag').text)
trans_flag     = int(head.find('trans_flag').text)
k = head.find('k').text.strip().split()
for i in range(len(k)):
    k[i] = float(k[i])
k = [k]
cos = head.find('cos').text.strip().split()
for i in range(len(cos)):
    cos[i] = float(cos[i])
cos = [cos]

# log.write('Creating airfoil...\n')
abaqus_input = createAirfoil(project_name, airfoil_main)

# log.write('Converting to VABS input and run...\n')
homogenization(
    gen_input_only=abaqus_input, model_source=2, 
    macro_model=1, analysis=analysis, elem_flag=elem_flag, 
    trans_flag=trans_flag, ap1=False, ap2=False, ap3=False, 
    abaqus_input=abaqus_input, new_filename=project_name, 
    specific_model=specific_model, bk=k, cos=cos
    )
