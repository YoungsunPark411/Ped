# -*- coding: cp949 -*-
import pymel.core as pm
import sys
sys.path.append(r'D:\MyScript\sealped')
from Material import General as gn
#reload(gn)

Scale = gn.scaleGet()
def FKCtrlMake(JntList,shape_,cns):

    if 'Left' in str(JntList[0]):
        MainColor = 13
    elif 'Right' in str(JntList[0]):
        MainColor = 6
    elif 'Neck' in str(JntList[0]):
        MainColor = 28
    elif 'Spine' in str(JntList[0]):
        MainColor = 15
    else:
        MainColor = 17
    ctlList=[]
    for x in JntList:
        
        FKCtrl = gn.ControlMaker('%sFKCtrl' % x.replace('Jnt','').replace('FK',''), shape_, MainColor, exGrp=0, size= Scale)
        gn.PosCopy(x, FKCtrl[0])
        ctlList.append(FKCtrl[0])
        
        #gn.rotate_components(0, 0, 90, FKCtrl[0])

    for i in range(len(ctlList)):
        if i == 0: continue
        pm.parent(ctlList[i], ctlList[i - 1])

    if cns == 0:
        pass
    elif cns == 1:
        for i in range(len(ctlList)):
            gn.Mcon(ctlList[i],JntList[i],t=1, r=1, s=1, sh=1, mo=1, pvtCalc=1)
    for y in ctlList:
        gn.addNPO(y,'Grp')
    MotherFKCtrlGrp=pm.listRelatives(ctlList[0],p=1)[0]
    return [ctlList,MotherFKCtrlGrp]


#FKCtrlMake(JntList,shape_,cns)
JntList=pm.ls(sl=1)
FKCtrlMake(JntList,'pin',1)


'''
###Finger FKCtrl 리깅 만들기~

side=['Left','Right']
obj=['Index','Middle','Ring','Pinky']

for x in side:
    MotherFKCtrlGrp_list=[]
    for y in obj:
        jnt_list=gn.jntList(x+y+'1Jnt',2)
        fc=FKCtrlMake(jnt_list, 'pin', cns=1)
        MotherFKCtrlGrp_list.append(fc[1])
        for i in fc[0]:
            pm.select(i)
            if x=='Left':
                gn.rotate_components(90, 0, 0, nodes=None)
                gn.ChangeCurveColor(i, colorNum=20)
            else:
                gn.rotate_components(-90, 0, 0, nodes=None)
                gn.ChangeCurveColor(i, colorNum=18)

    if pm.objExists(x+'HandCtrl'):

        pm.parent(MotherFKCtrlGrp_list,x+'HandCtrl')
    #for z in ctrl_List:
        #gn.addNPO(z,'Grp')
'''                

                
