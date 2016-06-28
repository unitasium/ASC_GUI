import xml.etree.ElementTree as et
import sys
import os
from sg2DAirfoil import *
from vabsMain import *


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
head            = et.parse(head_file).getroot()
timoshenko_flag = int(head.find('timoshenko').text)
recover_flag    = int(head.find('recover').text) + 1
thermal_flag    = int(head.find('thermal').text)
curve_flag      = int(head.find('curve').text)
if timoshenko_flag == 0:
    vlasov_flag = 0
    oblique_flag = int(head.find('oblique').text)
    if oblique_flag == 1:
        cos = control.find('cos').text.split()
        cos = [float(cos[0]), float(cos[1])]
    else:
        cos = [1.0, 0.0]
else:
    vlasov_flag = int(head.find('vlasov').text)
    oblique_flag = 0
trapeze_flag = int(head.find('trapeze').text)
if curve_flag == 1:
    k = control.find('k').text.split()
    k = [float(k[0]), float(k[1]), float(k[2])]
else:
    k = [0.0, 0.0, 0.0]

# log.write('Creating airfoil...\n')
abaqus_input = createAirfoil(project_name, airfoil_main)

# log.write('Converting to VABS input and run...\n')
VABSMain(recover_flag, input_only, project_name, abaqus_input,
         timoshenko_flag, thermal_flag, trapeze_flag, vlasov_flag,
         curve_flag, k, oblique_flag, cos)
