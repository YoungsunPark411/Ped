# -*- coding: cp949 -*-
import pymel.core as pm
import sys, os

#파일패스 
if os.path.isdir('D:\Ped\Biped\Converts'):
   script_path = 'D:\Ped\Biped\Converts'
else:
   script_path = 'Z:\mvtools\scripts\Biped\Converts'
if script_path in sys.path:
    pass
else:
    sys.path.insert(0, script_path)

import json
import FilePathImport

from imp import reload
# reload(FilePathImport)


def FromJson():      
    config_ = FilePathImport.loadConfig_("BipedName.json")
    return config_

config_=FromJson()   

def NameExtraction(ObjName):
    side = []
    ob = []

    side_=config_["sideName"]

    for side_Value in side_:
        if side_Value in str(ObjName):
            side = side_Value
        else:
            side=''

    obj_=config_["objName"]
    for obj_Value in obj_:
        if obj_Value in str(ObjName):
            ob = obj_Value
        else:
            pass

    parts_=config_["parts"]
    parts=parts_[ob]
    color_=config_["color"]
    if side :
        colors=color_[side]
    else:
        colors=color_['other']

    return side,ob,parts,colors