import xml.etree.ElementTree as et
import sys
import os
from vabsMain import *


control_file = sys.argv[-1]
control = et.parse(control_file).getroor()

project_name = control.find('name').text
abaqus_input = control.find('abaqus').text
timoshenko_flag = int(control.find('timoshenko').text)
recover_flag = int(control.find('recover').text)
thermal_flag = int(control.find('thermal').text)
curve_flag = int(control.find('curve').text)
oblique_flag = int(control.find('oblique').text)
trapeze_flag = int(control.find('trapeze').text)
vlasov_flag = int(control.find('vlasov').text)

k = control.find('k').text.split()
k = [float(k[0]), float(k[1]), float(k[2])]
cos = control.find('cos').text.split()
cos = [float(cos[0]), float(cos[1])]

input_only = int(control.find('input_only').text)

VABSMain(recover_flag, input_only, project_name, abaqus_input,
         timoshenko_flag, thermal_flag, trapeze_flag, vlasov_flag,
         curve_flag, k, oblique_flag, cos)
