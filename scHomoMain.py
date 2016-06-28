# -*- coding: utf-8 -*-

from scGenInput import *
from scGen1DInput_aba import *
from UdetermineVolume import *
from UdetermineNSG import *
from userDataSG import *
from convert2sc import *
import time
import os


def homogenization(
        gen_input_only, model_source, macro_model, analysis,
        elem_flag, trans_flag, ap1, ap2, ap3, w='',
        model_name='', part_name='', abaqus_input='', new_filename='',
        specific_model=0, bk=[[0.0, 0.0, 0.0]],
        sk=[[0.0, 0.0]], cos=[[1.0, 0.0]], temp_flag=0):
    
    # ap = []
    # ap = [
    #     ['ap000', ap000], ['ap100', ap100], ['ap010', ap010], ['ap001', ap001],
    #     ['ap111', ap111], ['ap110', ap110], ['ap101', ap101], ['ap011', ap011]
    # ]
    # ap_dic = {}
    # apvector = []
    # ap_dic['ap000'] = [0, 0, 0]
    # ap_dic['ap100'] = [1, 0, 0]
    # ap_dic['ap010'] = [0, 1, 0]
    # ap_dic['ap001'] = [0, 0, 1]
    # ap_dic['ap111'] = [1, 1, 1]
    # ap_dic['ap110'] = [1, 1, 0]
    # ap_dic['ap101'] = [1, 0, 1]
    # ap_dic['ap011'] = [0, 1, 1]

    if analysis == 33:
        analysis = 3
    elif analysis == 44:
        analysis = 4
    
    apvector = [0, 0, 0]
    # print ap1
    # print ap2
    # print ap3
    
    if ap1:
        apvector[0] = 1
    if ap2:
        apvector[1] = 1
    if ap3:
        apvector[2] = 1

    # print apvector

    if model_source == 1:
        nSG = determineNSG(model_name, part_name)
        macro_model_dimension = str(macro_model) + 'D'
        print 'Dimension of Structure Genome: ' + str(nSG)
        print 'Dimension of Macroscopic Model: ' + macro_model_dimension

        if w == '':   # w imported is a string, this if-else give w as a float
            w = determineVolume(
                model_name, part_name, macro_model_dimension, nSG
            )
        else:
            w = float(w)

        # print apvector
        if nSG == 2 or nSG == 3:
            [sc_input, macro_model_dim] = generateInputFromCAE(
                model_source, macro_model_dimension,
                analysis, elem_flag, trans_flag, w, nSG,
                model_name, part_name, abaqus_input, new_filename,
                specific_model, bk[0],
                sk[0], cos[0], temp_flag, apvector
            )

        elif nSG == 1:
            [sc_input, macro_model_dim] = generate_1DInputFromCAE(
                model_source, macro_model_dimension,
                analysis, elem_flag, trans_flag, w, nSG,
                model_name, part_name, abaqus_input, new_filename,
                specific_model, bk[0],
                sk[0], cos[0], temp_flag
            )  # ,nlayer

    elif model_source == 2:
        if w == '':
            w = 1.0
        else:
            w = float(w)
        
        [sc_input, macro_model_dim] = convert2sc(
            abaqus_input, new_filename, macro_model, specific_model,
            analysis, elem_flag, trans_flag, temp_flag,
            bk[0], sk[0], cos[0], w
        )

    if not gen_input_only:
        try:
            scTimestart = time.clock()
            if apvector == [0, 0, 0]:
                os.system(
                    'Swiftcomp ' + sc_input + ' ' + macro_model_dim + ' H'
                )
            else:
                os.system(
                    'Swiftcomp ' + sc_input + ' ' + macro_model_dim + ' HA'
                )

            scTimeEnd = time.clock()
            scTime = scTimeEnd - scTimestart

            os.system('Notepad ' + sc_input + '.k')
            print 'scTime: ' + str(scTime)

        except:
            raise WindowsError(
                '''
                Unexpected error happened. 
                Please check the Command line window 
                for more information.
                '''
            )

            return 1

    return 1

