# -*- coding: cp949 -*-
import maya.OpenMayaUI as omui
from pymel.core import *
import pymel.core as pm
import pymel.core.datatypes as dt

from PySide2.QtCore import * 
from PySide2.QtGui import * 
from PySide2.QtWidgets import *
from PySide2 import __version__
from shiboken2 import wrapInstance

import sys,os

#파일패스 
if os.path.isdir('D:\Ped\Biped'):
   path_ = 'D:\Ped\Biped'
else:
   path_ = 'Z:\mvtools\scripts\Biped'
if path_ in sys.path:
    pass
else:
    sys.path.insert(0, path_)

#import BipedUI
import JntConvert
from Converts import WorldConvert
from Converts import SpineConvert
from Converts import NeckConvert
from Converts import ArmLegConvert
from Converts import FingerConvert
from Converts import FootConvert
from Converts import MirrorCurve
from Converts import Follow

    
#reload(BipedUI)
# reload(JntConvert)
# reload(WorldConvert)
# reload(SpineConvert)
# reload(NeckConvert)
# reload(ArmLegConvert)
# reload(FingerConvert)
# reload(FootConvert)
# reload(MirrorCurve)
# reload(Follow)


def GuideImport():
    pm.select(cl=1)      
    GuideFile='boneped_guide.mb'
    GuideFileFath='{}/{}'.format(path_, GuideFile)
    pm.importFile(GuideFileFath)
        
def BindJntConvert():
    JntConvert.JntMake_Organize()
        
def Convert():

    WorldConvert.WorldSetting()
    SpineConvert.SpineRig()
    NeckConvert.NeckRig()
    ArmLegConvert.ArmLegRigConvert()
    FingerConvert.FingerConvert()
    FootConvert.FootConvert()
    pm.delete('Biped_Guide',pm.ls('Biped_Guide*'),pm.ls('*',type='tweak'))
    MirrorCurve.TransMirrorCurve()
    Follow.FollowRig()
    

def UI():
    Dialog = 'BipedUI'

    if pm.window(Dialog, exists=True):
        pm.deleteUI(Dialog, window=True)

    aa = pm.loadUI(uiFile='D:/Ped/Biped/BipedUI.ui')
    pm.showWindow(aa)

UI()


'''
class myUIClass(QWidget):
    def __init__(self, *args, **kwargs):
        super(myUIClass, self).__init__(*args, **kwargs)
        self.setWindowFlags(Qt.Window)
        self.ui = BipedUI.Ui_BipedUI()
        self.ui.setupUi(self)
        self.ui.GuideButton.clicked.connect(self.GuideImport)
        self.ui.TransJointButton.clicked.connect(self.BindJntConvert)
        self.ui.ConvertButton.clicked.connect(self.Convert)
        
    def GuideImport(self):
        pm.select(cl=1)      
        GuideFile='boneped_guide.mb'
        GuideFileFath='{}/{}'.format(path_, GuideFile)
        pm.importFile(GuideFileFath)
        
    def BindJntConvert(self):
        JntConvert.JntMake_Organize()
        
    def Convert(self):

        WorldConvert.WorldSetting()
        SpineConvert.SpineRig()
        NeckConvert.NeckRig()
        ArmLegConvert.ArmLegRigConvert()
        FingerConvert.FingerConvert()
        FootConvert.FootConvert()
        pm.delete('Biped_Guide')
        

        
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)
    
def runWin():
    global myWin
    try:
        myWin.close()
    except:
        pass
    myWin = myUIClass(parent=maya_main_window())
    myWin.show()
runWin()
'''
