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

import General as gn



def WorldSetting():
    Scale=gn.scaleGet()
    characterGrp = pm.createNode('transform', n='Character' )
    rigGrp = pm.createNode('transform', n='RigGrp' )
    rigSysGrp = pm.createNode('transform', n='RigSysGrp' )
    worldCtrl = gn.ControlMaker('WorldCtrl', 'circle', 22, exGrp=0, size=Scale*4)
    moveCtrl = gn.ControlMaker('MoveCtrl', 'cross', 21, exGrp=0, size=Scale*3.5)
    flyCtrl = gn.ControlMaker('FlyCtrl', 'reverscheck', 18, exGrp=0, size=Scale*2)
    rootCtrl = gn.ControlMaker('RootCtrl', 'diamond', 21, exGrp=0, size=Scale*3)
    
    Upperbody_Guide=pm.PyNode('Upperbody_Guide')
    pm.delete(pm.pointConstraint(Upperbody_Guide,rootCtrl[0]))
    pm.delete(pm.pointConstraint(Upperbody_Guide,flyCtrl[0]))
    
    bindJntGrp=pm.createNode('transform', n='BindJntGrp' )
    
    pm.parent(rigGrp,characterGrp)
    pm.parent(worldCtrl[0],rigGrp)
    pm.parent(rigSysGrp,rigGrp)
    pm.parent(moveCtrl[0],worldCtrl[0])
    pm.parent(flyCtrl[0],moveCtrl[0])
    pm.parent(rootCtrl[0],flyCtrl[0])
    pm.parent(bindJntGrp,rootCtrl[0])
    
    gn.rotate_components(90, 0, 0, nodes=flyCtrl[0])
    gn.translate_components(0, 0, -2 * Scale, nodes=flyCtrl[0])
    
    
    needGrp=[worldCtrl[0],moveCtrl[0],flyCtrl[0],rootCtrl[0]]
    
    for x in needGrp:
        gn.addNPO(x,'Grp')
        
    if pm.objExists('RootJnt'):
        pm.parent('RootJnt',bindJntGrp)
    else:
        pass
        
    rigSysGrp.v.set(0)
        
#WorldSetting()
        
    
    