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

def MirrorCurve(source, target):
    sourceCV=pm.ls('%s.cv[*]'%source, fl=1)
    targetCV=pm.ls('%s.cv[*]'%target, fl=1)
    sourcePosX=[]
    sourcePosY=[]
    sourcePosZ=[]

    for ii in range(len(sourceCV)):
        sourcePos=pm.pointPosition( sourceCV[ii], w=1 )        
        sourcePosX.append(sourcePos[0])        
        sourcePosY.append(sourcePos[1])
        sourcePosZ.append(sourcePos[2])
    for i, cv in enumerate(targetCV):       
        pm.move(((sourcePosX[i])*-1),sourcePosY[i],sourcePosZ[i], cv)
   
def TransMirrorCurve():
    sel=pm.ls('Left*Ctrl*',type='nurbsCurve')

    if sel:
        for n in range(len(sel)):
            jj=sel[n].replace('Left','Right')
            tg=pm.PyNode(jj)
            MirrorCurve(sel[n], tg)