from abaqusGui import *
#from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class SG1D_v3Form(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='create1DSG',
            objectName='sg1DMain', registerQuery=False)
        pickedDefault = ''


        self.methodKw = AFXIntKeyword(self.cmd, 'method', True, 1)
        
#        self.radioButtonGroups['method'][2] = 'Read from file'
        self.layup_fgKw = AFXStringKeyword(self.cmd, 'layup_fg', True, '[45/-45]2s')
        self.thickness_fgKw = AFXFloatKeyword(self.cmd, 'thickness_fg', True)#, 1.0)
        self.model_name_fgKw = AFXStringKeyword(self.cmd, 'model_name_fg', True,'')
        self.offset_ratio_fgKw = AFXFloatKeyword(self.cmd, 'offset_ratio_fg', True, 0.0)
        self.material_nameKw = AFXStringKeyword(self.cmd, 'material_name', True,'')
        self.model_name_abqKw = AFXStringKeyword(self.cmd, 'model_name_abq', True,'')
        self.partNameKw = AFXStringKeyword(self.cmd, 'part_name', True,'')
        self.layup_abqKw = AFXStringKeyword(self.cmd, 'layup_abq', True)
        
        self.rf_model_nameKw = AFXStringKeyword(self.cmd, 'rf_model_name', True,'')
        self.rf_part_nameKw = AFXStringKeyword(self.cmd, 'rf_part_name', True,'')
        self.rf_section_nameKw = AFXStringKeyword(self.cmd, 'rf_section_name', True,'')
        self.rf_offset_ratioKw = AFXFloatKeyword(self.cmd, 'rf_offset_ratio', True,0.0)
        
        #self.offset_ratio_abqKw = AFXFloatKeyword(self.cmd, 'offset_ratio_abq', True, 0.0)
        self.file_layup_inputKw = AFXStringKeyword(self.cmd, 'file_layup_input', True, '')
        self.element_typeKw = AFXStringKeyword(self.cmd, 'element_type', True, 'five-noded')
        self.model_name_fileKw = AFXStringKeyword(self.cmd, 'model_name_file', True, '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import sG1D_v3DB
        reload(sG1D_v3DB)
        return sG1D_v3DB.SG1D_v3DB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

