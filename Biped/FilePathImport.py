# -*- coding: cp949 -*-
import pymel.core as pm
import sys,os
import os
#파일패스
if os.path.isdir('D:\Ped\Biped'):
   script_path = 'D:\Ped\Biped'
else:
   script_path = 'Z:\mvtools\scripts\Biped'
if script_path in sys.path:
    pass
else:
    sys.path.insert(0, script_path)

import json


def jsonImport(jsonName):
        currentDir = os.path.dirname(__file__)
        filePath = os.path.join(currentDir, jsonName)
        with open(filePath) as f:
            data_ = json.load(f)
        return data_


def loadConfig_(jsonName):
    # jsonName = "BipedName.json"
    return jsonImport(jsonName)
    
    