# -*- coding: cp949 -*-
import pymel.core as pm
import sys

path = r'D:\MyScript\sealped'
if not path in sys.path:
    sys.path.insert(0, path)
from Material import General as gn
from Material import IKFKBlend as kb
from Material import FKCtrlMake as fm

'''
reload(gn)
reload(kb)
reload(sb)
reload(si)
reload(fm)
'''
Scale = gn.scaleGet()


def MakeWristCtrl(JntList):
    if 'Left' in str(JntList[0]):
        MainColor = 13
        side = 'Left'
    elif 'Right' in str(JntList[0]):
        MainColor = 6
        side = 'Right'
    else:
        MainColor = 17
        side = ''

    ctlList = []
    for x in JntList:
        if 'Up' in str(x):
            shape_ = 'RoundSquare'
            FKCtrl = gn.ControlMaker(JntList[0].replace('Jnt', 'Ctrl'), shape_, MainColor, exGrp=0, size=Scale)

        else:
            shape_ = 'SealHand'
            FKCtrl = gn.ControlMaker(JntList[1].replace('Jnt', 'Ctrl').replace('Wrist','Hand'), shape_, MainColor, exGrp=0, size=Scale)
            pm.addAttr(FKCtrl[0], ln="FingerCtrlVis", at='bool', dv=0, k=1)
            pm.setAttr(FKCtrl[0]+'.FingerCtrlVis', keyable=0, channelBox=1)
                
        gn.PosCopy(x, FKCtrl[0])
        ctlList.append(FKCtrl[0])
        if shape_ == 'SealHand':
            pm.select(FKCtrl)
            gn.rotate_components(90, 0, 0, nodes=None)
        else:
            pass
        if side == 'Right':
            pm.select(FKCtrl)
            gn.rotate_components(0, 180, 0, nodes=None)
        else:
            pass

    for i in range(len(ctlList)):
        if i == 0: continue
        pm.parent(ctlList[i], ctlList[i - 1])

    for i in range(len(ctlList)):
        gn.Mcon(ctlList[i], JntList[i], t=1, r=1, s=1, sh=1, mo=1, pvtCalc=1)
    for y in ctlList:
        gn.addNPO(y, 'Grp')
    grp_ = pm.listRelatives(ctlList[0], p=1)[0]
    MotherFKCtrlGrp = gn.addNPO(grp_, 'OffGrp')[0]

    if pm.objExists('%sArmCtrlGrp' % side):
        ArmCtrlGrp_ = pm.PyNode('%sArmCtrlGrp' % side)
        pm.parent(MotherFKCtrlGrp, ArmCtrlGrp_)
    return MotherFKCtrlGrp


def getChildren_(object_, type_=None):
    object_ = pm.PyNode(object_)
    if not type_:
        type_ = 'transform'
    child_ = object_.listRelatives(ad=1, c=1, typ=type_)
    child_ = child_ + [object_]
    child_.reverse()
    return child_


def IKFKBlend(object_):
    FKChain = getChildren_(object_[0], type_='joint')

    IKChain = getChildren_(object_[1], type_='joint')

    DrvChain = getChildren_(object_[2], type_='joint')
    switch = object_[-1]

    for i, drv in enumerate(DrvChain):
        name_ = drv.name()

        BC_ = pm.shadingNode('blendColors', au=1, n='{0}BC'.format(name_))
        FKChain[i].s >> BC_.color1
        IKChain[i].s >> BC_.color2

        oc = pm.orientConstraint(IKChain[i], FKChain[i], drv,mo=1)
        BC_.output >> drv.s
        switch.IKFK >> BC_.blender

        find = oc.attr('target[1].targetWeight')
        Str_find = str(find)
        F_attr = find.listConnections(d=0, s=1, p=1)[0]
        switch.IKFK >> F_attr

        find2 = oc.attr('target[0].targetWeight')
        Str_find2 = str(find)
        F_attr2 = find2.listConnections(d=0, s=1, p=1)[0]
        rvs_ = pm.createNode('reverse', n=switch.replace('Ctrl', 'RVS'))
        switch.IKFK >> rvs_.inputX
        rvs_.outputX >> F_attr2

    return BC_


def IKFKBlendForWrist(IKCtrl, FKCtrl, MotherFKCtrlGrp, JntList, side):
    if pm.objExists('%sArmIKFKCtrl' % side):
        switch = pm.PyNode('%sArmIKFKCtrl' % side)
        selList = [FKCtrl, IKCtrl, MotherFKCtrlGrp, switch]
        pbc = IKFKBlend(selList)

    else:
        pass

    if pm.objExists(JntList[0].getParent()):

        cnsJnt = JntList[0].getParent()
        gn.Mcon(cnsJnt, MotherFKCtrlGrp, t=1, mo=1)
    else:
        pass


def WristRig(JntList):
    if 'Left' in str(JntList[0]):
        side = 'Left'
    elif 'Right' in str(JntList[0]):
        side = 'Right'
    else:
        side = ''

    Ctrl_ = MakeWristCtrl(JntList)

    if pm.objExists(JntList[0].getParent()):
        IKCtrl = pm.PyNode(JntList[0].getParent().replace('Jnt', 'IKCtrl'))
        FKCtrl = pm.PyNode(JntList[0].getParent().replace('Jnt', 'FKCtrl'))
        IKFKBlendForWrist(IKCtrl, FKCtrl, Ctrl_, JntList, side)


JntList = pm.ls(sl=1)

yy = WristRig(JntList)




