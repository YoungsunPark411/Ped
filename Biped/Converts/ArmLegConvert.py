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
import IKFKBlend as kb
import Seal_IKStretchSet as st
import json
import FilePathImport
# reload(gn)
# reload(kb)
# reload(st)



def FromJson():      
    config_ = FilePathImport.loadConfig_("BipedName.json")
    return config_

config_=FromJson()   

def NameExtraction(JntSel):
    side = []
    ob = []
    
    side_=config_["sideName"]
    for side_Value in side_:
        if side_Value in str(JntSel):
            side = side_Value
        else: 
            pass
    
    obj_=config_["objName"]
    for obj_Value in obj_:
        if obj_Value in str(JntSel):
            ob = obj_Value
        else: 
            pass

    parts_=config_["parts"]
    parts=parts_[ob]
    
    color_=config_["color"]
    colors=color_[side]    

    return side,ob,parts,colors

# 조인트만들기
def DuplicateJnt(JntSel, type):
    orgJnt = JntSel
    rstJnt = []
    [rstJnt.append(pm.createNode('joint', n='%s%sJnt' % (jnt.replace('Jnt', '').replace('Drv', ''), type))) for jnt in orgJnt]

    list(map(lambda a, b: pm.delete(pm.parentConstraint(a, b)), orgJnt, rstJnt))
    for i in range(len(orgJnt)):
        if i == 0: continue
        if '|' in rstJnt[i]:
            rstJnt[i] = rstJnt[i].replace('|', '')
        pm.parent(rstJnt[i], rstJnt[i - 1])
        pm.makeIdentity(rstJnt[i], a=1, t=1, r=1, s=1, n=0, pn=1)

        pm.makeIdentity(rstJnt[0], a=1, t=1, r=1, s=1, n=0, pn=1)
        pm.setAttr("%s.jointOrientX" % rstJnt[-1], 0)
        pm.setAttr("%s.jointOrientY" % rstJnt[-1], 0)
        pm.setAttr("%s.jointOrientZ" % rstJnt[-1], 0)
    return rstJnt


# IK 컨트롤 만들기
def IKCtrlMake(IKJnt):
    # 크기 정하기
    Scale = gn.scaleGet()
    if ob == 'Leg':
        shape = 'Foot'
        Scale_= Scale/5
    else:
        shape = 'circle'
        Scale_= Scale
    IKCtrl = gn.ControlMaker('%s%sIKCtrl' % (side, ob), shape, MainColor, exGrp=0, size=Scale_)
    pm.select(IKCtrl[0])
    pm.addAttr(ln="Twist", at='double', dv=0, k=1)
    pm.addAttr(ln="Stretch", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="Squash", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="UpSlide", at='double', dv=0, k=1)
    pm.addAttr(ln="DnSlide", at='double', dv=0, k=1)
    pm.addAttr(ln="PVctrlVis", at='bool', k=1)
    pm.setAttr('%s%sIKCtrl.PVctrlVis' % (side, ob), keyable=0, channelBox=1)
    pm.addAttr(ln="PVStretch", at='double', min=0, max=10, dv=0, k=1)
    if 'Arm' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Head:Chest:Hip:Root:Fly', k=1)
        pm.setAttr(IKCtrl[0] + ".Follow", 1)
    elif 'Leg' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Hip:Root:Fly:World', k=1)
        FootFunction = ["FootRoll", "BallRoll", "ToeRoll", "InOut", "HeelPivot", "BallPivot", "ToePivot"]
        for x in FootFunction:
            pm.addAttr(ln=x, at='double', min=-10, max=10, dv=0, k=1)
        pm.setAttr("%s%sIKCtrl.Follow" % (side, ob), 2)
    pm.addAttr(ln="ConstCtrlVis", at='bool', k=1)
    pm.setAttr(IKCtrl[0] + '.ConstCtrlVis', keyable=0, channelBox=1)
    IKConstCtrl = gn.ControlMaker('%s%sIKConstCtrl' % (side, ob), shape, MainColor, exGrp=0, size=Scale_ * 1.2)
    IKSubCtrl = gn.ControlMaker('%s%sIKSubCtrl' % (side, ob), shape, SubColor, exGrp=0, size=Scale_ * 0.8)
    if 'Arm' in ob:
        gn.rotate_components(0, 0, 90, nodes=IKCtrl[0])
        gn.rotate_components(0, 0, 90, nodes=IKConstCtrl[0])
        gn.rotate_components(0, 0, 90, nodes=IKSubCtrl[0])
    return [IKCtrl[0], IKConstCtrl[0], IKSubCtrl[0]]


def IKCtrlMatch(IKJnt):
    IKCtrlList = IKCtrlMake(IKJnt)
    IKCtrl, IKConstCtrl, IKSubCtrl = IKCtrlList[0], IKCtrlList[1], IKCtrlList[2]
    pm.parent(IKCtrl, IKConstCtrl)
    pm.parent(IKSubCtrl, IKCtrl)
    pm.delete(pm.pointConstraint(IKJnt[-1], IKConstCtrl))

    if ob == 'Leg':
        gn.addNPO(IKConstCtrl, 'Grp')
        gn.addNPO(IKCtrl, 'Grp')
        gn.addNPO(IKSubCtrl, 'Grp')

    else:

        gn.PosCopy(IKJnt[-1], IKConstCtrl)
        RX = IKConstCtrl.rotateX.get()
        RZ = IKConstCtrl.rotateZ.get()
        RY = IKConstCtrl.rotateY.get()
        if side == 'Right':
            IKConstCtrl.rotateX.set(RX - 90)
            IKConstCtrl.rotateY.set(RY - 180)

        elif side == 'Left':
            IKConstCtrl.rotateX.set(RX - 90)
        gn.addNPO(IKConstCtrl, 'Grp')
        gn.addNPO(IKCtrl, 'Grp')
        gn.addNPO(IKSubCtrl, 'Grp')

    return [IKCtrl, IKConstCtrl, IKSubCtrl]


def PolevectorMake(handle, IKJnt):
    PoleVectorCtrl = gn.ControlMaker('%s%sPoleVectorCtrl' % (side, ob), 'reverscheck', MainColor, exGrp=0, size=Scale)
    pm.select(PoleVectorCtrl[0])

    if ob == 'Arm':
        pm.addAttr(ln="Follow", at='enum', en='Auto:Chest:Root:Fly:World', k=1)
        gn.translate_components(0, 0,  Scale, nodes=PoleVectorCtrl[0])

    elif ob == 'Leg':
        pm.addAttr(ln="Follow", at='enum', en='Auto:Hip:Root:Fly:World', k=1)
        gn.rotate_components(0, 180, 0, nodes=PoleVectorCtrl[0])
        gn.translate_components(0, 0, -1 * Scale, nodes=PoleVectorCtrl[0])
    else:
        pass

    gn.PosCopy(IKJnt[1], PoleVectorCtrl[0])
    PoleVectorCtrl[0].tz.set(0.5)
    gn.addNPO(PoleVectorCtrl[0], 'Grp')
    pm.poleVectorConstraint(PoleVectorCtrl[0], handle, n='%sPoleVectorConst' % handle.replace('IKHandle', ''))
    return PoleVectorCtrl[0]


def IKRig(IKJnt):
    IKCtrlList = IKCtrlMatch(IKJnt)
    IKCtrl, IKConstCtrl, IKSubCtrl = IKCtrlList[0], IKCtrlList[1], IKCtrlList[2]
    IKHandle = pm.ikHandle(sj=IKJnt[0], ee=IKJnt[-1], n='%s%sIKHandle' % (side, ob), sol='ikRPsolver', ccv=0)
    IKPos = pm.createNode('transform', n='%s%sIKPos' % (side, ob))
    gn.PosCopy(IKCtrl, IKPos)
    pm.parent(IKPos, IKSubCtrl)
    gn.Mcon(IKPos, IKHandle[0], t=1, mo=0, pvtCalc=1)
    poleCtrl = PolevectorMake(IKHandle[0], IKJnt)
    return [IKCtrlList, poleCtrl, IKPos]


# FK 리깅 만들기
def FKCtrlMake(JntList, shape_, cns):
    ctlList = []
    for x in JntList:
        FKCtrl = gn.ControlMaker('%sFKCtrl' % x.replace('Jnt', '').replace('FK', ''), shape_, MainColor, exGrp=0, size=Scale*0.5)
        gn.PosCopy(x, FKCtrl[0])
        ctlList.append(FKCtrl[0])
    # gn.rotate_components(0, 0, 90, FKCtrl[0])
    for i in range(len(ctlList)):
        if i == 0: continue
        pm.parent(ctlList[i], ctlList[i - 1])

    if cns == 0:
        pass
    elif cns == 1:
        for i in range(len(ctlList)):
            gn.Mcon(ctlList[i], JntList[i], t=1, r=1, mo=0, pvtCalc=1)
    for y in ctlList:
        gn.addNPO(y, 'Grp')
    MotherFKCtrlGrp = pm.listRelatives(ctlList[0], p=1)[0]
    return [ctlList, MotherFKCtrlGrp]


def FKRig(FKJnt):
    ctrl = FKCtrlMake(FKJnt, 'RoundSquare', 1)
    firstFKCtrl = ctrl[0][0]
    pm.select(firstFKCtrl)
    if 'Arm' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Clavicle:Chest:Root:Fly:World', k=1)
    elif 'Leg' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Hip:LegRoot:Root:Fly:World', k=1)
    return ctrl


xyzList = ['x', 'y', 'z']
trsList = ['t', 'r', 's']


# Drv 리깅 만들기
def IKFKCtrlMake(JntSel):
    IKFKCtrl = gn.ControlMaker('%s%sIKFKCtrl' % (side, ob), 'switch', MainColor, exGrp=1, size=Scale)
    for i, j in zip(xyzList, trsList):
        pm.setAttr(IKFKCtrl[0] + '.' + j + i, lock=1, k=0, channelBox=0)
    pm.select(IKFKCtrl[0])
    pm.addAttr(ln="IKFK", at='double', min=0, max=1, dv=0, k=1)
    pm.addAttr(ln="Arc", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="UpTwistFix", at='double', dv=0, k=1)
    pm.addAttr(ln="MidTwistFix", at='double', dv=0, k=1)
    pm.addAttr(ln="DnTwistFix", at='double', dv=0, k=1)
    pm.addAttr(ln="AutoHideIKFK", at='bool', k=1)
    pm.addAttr(ln="ArcCtrlVis", at='bool', k=1)
    pm.setAttr(IKFKCtrl[0] + '.AutoHideIKFK', keyable=0, channelBox=1)
    pm.setAttr(IKFKCtrl[0] + '.ArcCtrlVis', keyable=0, channelBox=1)
    if ob == 'Leg':
        pm.delete(pm.pointConstraint(JntSel[-1], IKFKCtrl[1]))
        pm.delete(pm.orientConstraint(JntSel[-1].getParent(), IKFKCtrl[1]))
        gn.Mcon(JntSel[-1], IKFKCtrl[1], t=1, r=0, s=0, sh=1, mo=1, pvtCalc=1)        
    else:
        pm.delete(pm.parentConstraint(JntSel[-1], IKFKCtrl[1]))
        gn.Mcon(JntSel[-1], IKFKCtrl[1], t=1, r=0, s=0, sh=1, mo=1, pvtCalc=1)
    gn.rotate_components(-90, 0, 0, nodes=IKFKCtrl[0])
    gn.translate_components(0, -2 * Scale, 0, nodes=IKFKCtrl[0])
    
    return IKFKCtrl[0]


# def IKFKVisSet(IKFKCtrl,IKFKCtrl,IKFKCtrl,PolevectorCtrl):

#     IKFKRVS=pm.createNode('reverse',n='%s%sIKFKRVS'%(side,ob))
#     IKFKCDT = pm.createNode('condition', n='%s%sIKFKCDT'%(side,ob))
#     IKFKCtrl=IKFKCtrl
#     IKCtrlGrp = pm.PyNode('%s%sIKConstCtrlGrp'%(side,ob))
#     IKFK1CtrlGrp = pm.PyNode('%s%sFK1CtrlGrp'%(side,ob))
#     PolevectorShape=pm.PyNode('%s%sPoleVectorCtrlShape'%(side,ob))
#     IKFKCtrl.IKFK>>IKFKRVS.input.inputX
#     IKFKRVS.output.outputX>>IKFKCDT.colorIfTrue.colorIfTrueR
#     IKFKCtrl.IKFK >> IKFKCDT.colorIfTrue.colorIfTrueG
#     IKFKCtrl.AutoHideIKFK >> IKFKCDT.firstTerm
#     IKFKCDT.secondTerm.set(1)
#     IKFKCDT.outColor.outColorR>>IKCtrlGrp.visibility
#     IKFKCDT.outColor.outColorR >> PolevectorShape.visibility
#     IKFKCDT.outColor.outColorG >> IKFK1CtrlGrp.visibility
#     IKFKCtrl.AutoHideIKFK.set(1)

def IKFKVisConnect(IKCtrlGrp, FKCtrlGrp, IKFKCtrl):
    switch = IKFKCtrl
    FKCtrlGrp_ = FKCtrlGrp
    IKCtrlGrp_ = IKCtrlGrp
    rev = pm.createNode('reverse', n='%s%sRV' % (side, ob))
    cd = pm.createNode('condition', n='%s%sCD' % (side, ob))
    cd.secondTerm.set(1)
    switch.IKFK >> cd.colorIfTrue.colorIfTrueR
    switch.IKFK >> rev.input.inputX
    switch.AutoHideIKFK >> cd.firstTerm
    switch.AutoHideIKFK.set(1)
    rev.output.outputX >> cd.colorIfTrue.colorIfTrueG
    cd.outColor.outColorR >> FKCtrlGrp_.visibility
    cd.outColor.outColorG >> IKCtrlGrp_.visibility


# Arc 리깅 만들기
def ArcCtrlMake():
    UpArcCtrl = gn.ControlMaker('%s%sUpArcCtrl' % (side, ob), 'hexagon', SubColor, exGrp=0, size=Scale)
    MidArcCtrl = gn.ControlMaker('%s%sMidArcCtrl' % (side, ob), 'hexagon', SubColor, exGrp=0, size=Scale)
    DnArcCtrl = gn.ControlMaker('%s%sDnArcCtrl' % (side, ob), 'hexagon', SubColor, exGrp=0, size=Scale)

    ArcCtrlList = [UpArcCtrl[0], MidArcCtrl[0], DnArcCtrl[0]]
    for i in ArcCtrlList:
        gn.rotate_components(0, 0, 90, nodes=i)
    # for i,j in zip(ArcJntMatchList,ArcCtrlList):
    #     gn.rotate_components(0, 0, 90, nodes=j)
    #     gn.PosCopy(i,j)
    #     gn.addNPO(j,'Grp')
    return ArcCtrlList


def CurveToPC(src, tg):
    mm = pm.createNode('multMatrix', n='%sMM' % tg)
    dm = pm.createNode('decomposeMatrix', n='%sDM' % tg)
    mm.i[0].set(tg.getMatrix(worldSpace=1))
    mm.i[1].set(src.getMatrix(worldSpace=1).inverse())
    src.wm >> mm.i[2]
    tg.pim >> mm.i[3]
    mm.o >> dm.imat
    dm.ot >> tg.t
    cm = pm.createNode('composeMatrix', n='%sCM' % tg)
    pc = pm.createNode('pointOnCurveInfo', n='%sPC' % tg)
    cm.outputMatrix >> mm.matrixIn[0]
    pc.result.position >> cm.inputTranslate
    src.worldSpace[0] >> pc.inputCurve
    pc.turnOnPercentage.set(1)
    pc.parameter.set(0.5)
    return pc


def ArcCtrlMatch(DrvJnt, UpIKCrv, DnIKCrv, ArcPointPos, bs):
    ArcCtrlList = ArcCtrlMake()
    if side == 'Right':
        aim_=[-1,0,0]
    else:
        aim_=[1,0,0]

    UpArcCtrl, MidArcCtrl, DnArcCtrl = ArcCtrlList[0], ArcCtrlList[1], ArcCtrlList[2]
    for x in ArcCtrlList:
        grp_ = gn.addNPO(x, 'Grp')

        if x == UpArcCtrl:
            pm.delete(pm.pointConstraint(DrvJnt[0], DrvJnt[1], grp_[0], mo=0))
            # gn.Mcon(UpIKCrv,grp_[0],t=1, r=0, s=0, sh=1, mo=1, pvtCalc=1)
            tc = pm.tangentConstraint(UpIKCrv, grp_, wut=2, wuo=DrvJnt[0],aim=aim_)
            tg = grp_[0]
            src = UpIKCrv
            pc = CurveToPC(src, tg)
            bs.outputGeometry[0] >> pc.inputCurve
            bs.outputGeometry[0] >> tc.target[0].targetGeometry

        elif x == MidArcCtrl:
            pm.delete(pm.pointConstraint(DrvJnt[1], grp_[0], mo=0))
            pm.parentConstraint(DrvJnt[1], grp_[0], mo=1)
            PBgrp_ = gn.addNPO(x, 'PBGrp')
            pm.pointConstraint(ArcPointPos, PBgrp_)
            pm.orientConstraint(DrvJnt[0], PBgrp_)
            gn.PairBlend(PBgrp_[0], r=1, t=1, sh=1, mo=0, pvtCalc=1)
            PBgrp_[0].pbw.set(0.5)
        elif x == DnArcCtrl:
            pm.delete(pm.pointConstraint(DrvJnt[1], DrvJnt[2], grp_[0], mo=0))
            # gn.Mcon(DnIKCrv,grp_[0],t=1, r=0, s=0, sh=1, mo=1, pvtCalc=1)
            tc2 = pm.tangentConstraint(DnIKCrv, grp_, wut=2, wuo=DrvJnt[-1],aim=aim_)
            tg = grp_[0]
            src = DnIKCrv
            pc = CurveToPC(src, tg)
            bs.outputGeometry[1] >> pc.inputCurve
            bs.outputGeometry[1] >> tc2.target[0].targetGeometry

    IKFKCtrl = pm.PyNode('%s%sIKFKCtrl' % (side, ob))
    for x in ArcCtrlList:
        Grp_ = x.getParent()
        IKFKCtrl.ArcCtrlVis >> Grp_.visibility
    return ArcCtrlList


def ArcCurveMake(DrvJnt):
    Crv = gn.CrvFromJnt(DrvJnt)

    # ArcPosConnect
    PosList = []
    for x in range(len(DrvJnt)):
        Pos = pm.createNode('transform', n=DrvJnt[x].replace('DrvJnt', 'ArcPos').replace('|', ''))
        pm.pointConstraint(DrvJnt[x], Pos, mo=0)
        PosList.append(Pos)

    # Pos->ArcPointPos
    App = pm.createNode('transform', n='%s%sArcPointPos' % (side, ob))

    AUpDB = pm.createNode('distanceBetween', n='%s%sArcUpDB' % (side, ob))
    PosList[0].t >> AUpDB.point1
    PosList[1].t >> AUpDB.point2
    ADnDB = pm.createNode('distanceBetween', n='%s%sArcDnDB' % (side, ob))
    PosList[1].t >> ADnDB.point1
    PosList[2].t >> ADnDB.point2
    ADL = pm.createNode('addDoubleLinear', n='%s%sArcPointADL' % (side, ob))
    AUpDB.distance >> ADL.input1
    ADnDB.distance >> ADL.input2
    MDL = pm.createNode('multDoubleLinear', n='%s%sArcPointMDL' % (side, ob))
    ADL.output >> MDL.input1
    MDL.input2.set(3)
    PointCNS = pm.pointConstraint(PosList[0], PosList[1], PosList[2], App)
    PointCNS.offsetZ.set(-0.05)
    pm.connectAttr(ADnDB + '.distance', PointCNS + '.%sW0' % PosList[0])
    pm.connectAttr(MDL + '.output', PointCNS + '.%sW1' % PosList[1])
    pm.connectAttr(AUpDB + '.distance', PointCNS + '.%sW2' % PosList[-1])

    # ArcPointPos->...
    TPC = pm.createNode('makeThreePointCircularArc', n='%s%sTPC' % (side, ob))
    PosList[0].t >> TPC.point1
    App.t >> TPC.point2
    PosList[2].t >> TPC.point3
    ArcDT = pm.createNode('detachCurve', n='%s%sArcDetach' % (side, ob))
    TPC.outputCurve >> ArcDT.inputCurve
    # detach parameter 연결
    PMP1 = pm.createNode('plusMinusAverage', n='%s%sArcPos1_App' % (side, ob))
    PMP1.operation.set(2)
    App.t >> PMP1.input3D[1]
    PosList[0].t >> PMP1.input3D[0]
    PMP2 = pm.createNode('plusMinusAverage', n='%s%sApp_ArcPos3' % (side, ob))
    PMP2.operation.set(2)
    PosList[2].t >> PMP2.input3D[1]
    App.t >> PMP2.input3D[0]
    PMP3 = pm.createNode('plusMinusAverage', n='%s%sArcPos3_ArcPos1' % (side, ob))
    PMP3.operation.set(2)
    PosList[2].t >> PMP3.input3D[1]
    PosList[0].t >> PMP3.input3D[0]
    ArcInAB = pm.createNode('angleBetween', n='%s%sArcInAB' % (side, ob))
    PMP1.output3D >> ArcInAB.vector1
    PMP3.output3D >> ArcInAB.vector2
    ArcOutAB = pm.createNode('angleBetween', n='%s%sArcOutAB' % (side, ob))
    PMP2.output3D >> ArcOutAB.vector1
    PMP3.output3D >> ArcOutAB.vector2
    ArcAngleSR = pm.createNode('setRange', n='%s%sArcAngleSR' % (side, ob))
    TPC.sections >> ArcAngleSR.max.maxX
    ArcAngleADL = pm.createNode('addDoubleLinear', n='%s%sArcAngleADL' % (side, ob))
    ArcInAB.axisAngle.angle >> ArcAngleADL.input1
    ArcOutAB.axisAngle.angle >> ArcAngleADL.input2
    ArcAngleADL.output >> ArcAngleSR.oldMax.oldMaxX
    ArcOutAB.axisAngle.angle >> ArcAngleSR.value.valueX

    ArcDetach = pm.createNode('detachCurve', n='%s%sArcDetach' % (side, ob))
    ArcAngleSR.outValue.outValueX >> ArcDetach.parameter[0]
    TPC.outputCurve >> ArcDetach.inputCurve

    # 커브 자르기
    CrvList = pm.detachCurve("%s.ep[1]" % Crv, ch=1, cos=1, rpo=1)

    UpArcCrv = pm.rename(CrvList[1], '%s%sUpArcCrv' % (side, ob))
    DnArcCrv = pm.rename(CrvList[0], '%s%sDnArcCrv' % (side, ob))
    N_CrvList = [UpArcCrv, DnArcCrv]

    UpIKCrv = pm.duplicate(UpArcCrv, n='%s%sUpIKCrv' % (side, ob))[0]
    DnIKCrv = pm.duplicate(DnArcCrv, n='%s%sDnIKCrv' % (side, ob))[0]

    IKCrvList = [UpIKCrv, DnIKCrv]
    for x in IKCrvList:
        cls = pm.cluster(x)
        orig = pm.listRelatives(x, s=1)[-1]
        if x == IKCrvList[0]:
            PosList[0].t >> orig.controlPoints[0]
            PosList[1].t >> orig.controlPoints[1]
        else:
            PosList[1].t >> orig.controlPoints[0]
            PosList[2].t >> orig.controlPoints[1]
        pm.delete(cls)
        pm.rebuildCurve(x, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)

    for i in N_CrvList:
        Rbd = pm.rebuildCurve(i, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)
    
    IKCrvGrp = pm.group(UpIKCrv, DnIKCrv, n='%s%sIKCrvGrp' % (side, ob))
    ArcCrvGrp = pm.group(UpArcCrv, DnArcCrv, n='%s%sArcCrvGrp' % (side, ob))

    # 커브 블랜드쉐입
    bs = pm.blendShape(ArcCrvGrp, IKCrvGrp, n='%s%sArcBS' % (side, ob))[0]
    ArcMDL = pm.createNode('multDoubleLinear', n='%s%sArcMDL' % (side, ob))
    ArcMDL.input2.set(0.1)
    IKFKCtrl = pm.PyNode('%s%sIKFKCtrl' % (side, ob))
    IKFKCtrl.Arc >> ArcMDL.input1
    pm.connectAttr(ArcMDL.output, bs + '.%s%sArcCrvGrp' % (side, ob))
    # ArcMDL.output>>bs.%s%sArcCrvGrp

    UpIKChkCrv = pm.duplicate(UpIKCrv, n='%s%sUpIKChkCrv' % (side, ob))[0]
    DnIKChkCrv = pm.duplicate(DnIKCrv, n='%s%sDnIKChkCrv' % (side, ob))[0]
    # IKChkCrvGrp=pm.group(UpIKChkCrv,DnIKChkCrv, n='%s%sIKChkCrvGrp')
    # pm.parent(IKChkCrvGrp,EtcGrp)
    pm.parentConstraint(DrvJnt[0], UpIKChkCrv, mo=1)
    pm.parentConstraint(DrvJnt[1], DnIKChkCrv, mo=1)

    UpArcCrvSh = pm.listRelatives(UpArcCrv, s=1)[0]
    DnArcCrvSh = pm.listRelatives(DnArcCrv, s=1)[0]

    ArcDetach.outputCurve[0] >> UpArcCrvSh.create
    ArcDetach.outputCurve[1] >> DnArcCrvSh.create

    # ArcCtrl 만들고 위치 시키기
    ArcCtrlList = ArcCtrlMatch(DrvJnt, UpIKCrv, DnIKCrv, App, bs)

    # for i in IKCrvList:
    #     Rbd=pm.rebuildCurve(i, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)

    for i in N_CrvList:
        Rbd = pm.rebuildCurve(i, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)

    PosList.append(App)

    return [PosList, UpIKCrv, DnIKCrv, UpArcCrv, DnArcCrv, ArcCtrlList]


def ArcSplineRig(PosNCrv_, UpArcJnt, DnArcJnt):
    PosNCrv = PosNCrv_
    PosList, UpIKCrv, DnIKCrv, UpArcCrv, DnArcCrv = PosNCrv[0], PosNCrv[1], PosNCrv[2], PosNCrv[3], PosNCrv[4]

    # ArcSpline
    UpikHandle = pm.ikHandle(sj=UpArcJnt[0], ee=UpArcJnt[-1], n='%s%sUpArcHandle' % (side, ob), sol='ikSplineSolver', ccv=0, c=UpIKCrv)
    Uphandle = UpikHandle[0]
    Uphandle.dTwistControlEnable.set(1)
    Uphandle.dWorldUpType.set(4)
    DnikHandle = pm.ikHandle(sj=DnArcJnt[0], ee=DnArcJnt[-1], n='%s%sDnArcHandle' % (side, ob), sol='ikSplineSolver', ccv=0, c=DnIKCrv)
    Dnhandle = DnikHandle[0]
    Dnhandle.dTwistControlEnable.set(1)
    Dnhandle.dWorldUpType.set(4)

    return [Uphandle, Dnhandle, UpIKCrv, DnIKCrv]


def ArcCtrlRig(ArcCtrls):
    ArcCtrlList = ArcCtrls
    N_CrvList = ['%s%sUpIKCrv' % (side, ob), '%s%sDnIKCrv' % (side, ob)]
    for x in N_CrvList:
        i = pm.PyNode(x)
        N_cls1 = pm.cluster(i.cv[1:3], n='%s1Cls' % i)

        pm.percent(N_cls1[0], '%sShape.cv[1]' % i, v=0.5)
        pm.percent(N_cls1[0], '%sShape.cv[3]' % i, v=0.5)
        if 'Up' in x:

            N_cls2 = pm.cluster(i.cv[3:4], n='%s2Cls' % i)
            pm.percent(N_cls2[0], '%sShape.cv[3]' % i, v=0.5)
            pm.parent(N_cls1, ArcCtrlList[0])

            ArcCtrlList[0].t >> N_cls1[1].t
            ArcCtrlList[0].r >> N_cls1[1].r
            ArcCtrlList[0].s >> N_cls1[1].s


        elif 'Dn' in x:

            N_cls2 = pm.cluster(i.cv[0:1], n='%s2Cls' % i)
            pm.percent(N_cls2[0], '%sShape.cv[1]' % i, v=0.5)
            pm.parent(N_cls1, ArcCtrlList[2])
            ArcCtrlList[2].t >> N_cls1[1].t
            ArcCtrlList[2].r >> N_cls1[1].r
            ArcCtrlList[2].s >> N_cls1[1].s

        ArcCtrlList[1].t >> N_cls2[1].t
        ArcCtrlList[1].r >> N_cls2[1].r
        ArcCtrlList[1].s >> N_cls2[1].s
        pm.parent(N_cls2[1], ArcCtrlList[1])
        pm.select(N_cls1[1])
        clsGrp1 = gn.MakeBindPreMtxCluster()
        pm.select(N_cls2[1])
        clsGrp2 = gn.MakeBindPreMtxCluster()

        CtrlGrp1 = pm.listRelatives(ArcCtrlList[0], p=1)[0]

        if 'Up' in x:
            CtrlGrp1 = pm.listRelatives(ArcCtrlList[0], p=1)[0]
        elif 'Dn' in x:
            CtrlGrp1 = pm.listRelatives(ArcCtrlList[2], p=1)[0]
        pm.parent(clsGrp1, CtrlGrp1)
        gn.PosCopy(CtrlGrp1, clsGrp1)

        CtrlGrp2 = pm.listRelatives(ArcCtrlList[1], p=1)[0]
        pm.parent(clsGrp2, CtrlGrp2)
        gn.PosCopy(CtrlGrp2, clsGrp2)
        list = [clsGrp1, clsGrp2]

        clsGrp1.visibility.set(0)
        clsGrp2.visibility.set(0)


def ArcJntMake(Crv, JntSel):
    # Chain = kb.getChildren_(JntSel[0], type_='joint')
    # segNumber=len(Chain)
    segNumber = 5
    arcJnt = gn.JntMake(Crv, segNumber, 'Arc')

    return arcJnt


def ArcRig(JntSel):
    posNCrv = ArcCurveMake(JntSel)

    UpIKCrv, DnIKCrv = posNCrv[1], posNCrv[2]
    UpArcJnt = ArcJntMake(UpIKCrv, JntSel)
    DnArcJnt = ArcJntMake(DnIKCrv, JntSel)
    results_ = ArcSplineRig(posNCrv, UpArcJnt, DnArcJnt)
    ArcHandles = results_[:2]
    IKCrvs = results_[2:]
    pm.parent(DnArcJnt[0], UpArcJnt[-1])
    ArcJnt = kb.getChildren_(UpArcJnt[0], type_='joint')
    ArcCtrls = posNCrv[-1]
    ArcCtrlRig(ArcCtrls)

    ArcPosList = posNCrv[0]
    return [UpArcJnt, DnArcJnt, ArcHandles, IKCrvs, ArcPosList]


# 스트레치 스쿼시 리깅 
def connectStretchSquash(sel):
    name_ = sel[0].replace('Jnt', '')
    stMDL = pm.PyNode(name_.replace('1', '') + 'StretchMDL')
    sqMDL = pm.PyNode(name_.replace('1', '') + 'SquashMDL')

    IKFKCtrl = pm.PyNode('%s%sIKCtrl' % (side, ob))

    # pm.addAttr(IKFKCtrl,ln="Stretch", at='double',  min=0, max=10, dv=0, k=1)
    # pm.addAttr(IKFKCtrl, ln="Squash", at='double',  min=0, max=10, dv=0, k=1)

    IKFKCtrl.Stretch >> stMDL.input1
    IKFKCtrl.Squash >> sqMDL.input1


def Spline(sel, Crv):
    crv_Jnt = st.IKStretch(sel, Crv)
    # crv_=crv_Jnt[0]
    # Jnt_=crv_Jnt[1]
    connectStretchSquash(sel)
    return crv_Jnt[0]


# IKJnt의 스트레치 

def distancBetween_(name_):
    return pm.shadingNode('distanceBetween', au=1, n='{}DB'.format(name_))

def blendTwoAttr_(name_):
    return pm.shadingNode('blendTwoAttr', au=1, n='{}BA'.format(name_))

def multiplyDivide_(name_):
    return pm.shadingNode('multiplyDivide', au=1, n='{}MD'.format(name_))

def multDoubleLinear_(name_):
    return pm.shadingNode('multDoubleLinear', au=1, n='{}MDL'.format(name_))

def transform_(name_):
    return pm.shadingNode('transform', au=1, n='{}Pos'.format(name_))

def addDoubleLinear_(name_):
    return pm.shadingNode('addDoubleLinear', au=1, n='{}AL'.format(name_))

def blendColors_(name_):
    return pm.shadingNode('blendColors', au=1, n='{}BC'.format(name_))

def condition_(name_):
    return pm.shadingNode('condition', au=1, n='{}CD'.format(name_))


# 두 포스 사이 길이 구하기 
def PosLen(pos1, pos2, DB):
    pos1_ = pm.PyNode(pos1)
    pos2_ = pm.PyNode(pos2)
    pos1_.t >> DB.point1
    pos2_.t >> DB.point2
    return DB


# 컨트롤 채널과 노드 연결
def MDConnect(Ctrl, AttrName):
    md_ = multDoubleLinear_(side + ob + AttrName)
    md_.input2.set(0.1)
    pm.connectAttr(Ctrl + '.%s' % AttrName, md_.input1)
    return md_


def IKNodeConnection(IKJnt, IKCtrl, PoleVectorCtrl):
    # 위쪽, 아래쪽, 전체 길이 구하기
    posList = []
    for x in IKJnt:
        posMake = transform_(x.replace('Jnt', ''))
        posList.append(posMake)
        pm.delete(pm.parentConstraint(x, posMake))
    pos1, pos2, pos3 = posList[0], posList[1], posList[2]
    MovePos = pm.duplicate(pos3, n=pos3.replace('Pos', 'MovePos'))[0]
    pm.parentConstraint(IKCtrl, MovePos)
    posGrp_ = pm.group(posList, MovePos, n='%s%sPosGrp' % (side, ob))
    UpLenDB = distancBetween_('%s%sUpLen' % (side, ob))
    DnLenDB = distancBetween_('%s%sDnLen' % (side, ob))
    AllLenDB = distancBetween_('%s%sAllLen' % (side, ob))
    UpLen = PosLen(pos1, pos2, UpLenDB)
    DnLen = PosLen(pos2, pos3, DnLenDB)
    AllLen = PosLen(pos1, MovePos, AllLenDB)

    adl = addDoubleLinear_('%s%sUpNDnLen' % (side, ob))
    UpLen.distance >> adl.input1
    DnLen.distance >> adl.input2

    # 디폴트 전체 길이구하기
    # AlldefLen=AllLen.attr('distance').get()
    # pm.addAttr(MovePos, ln="DefLength", at='double', dv=0, k=1)
    # MovePos.DefLength.set(AlldefLen)
    # pm.addAttr(MovePos, ln="UpDnLength", at='double', dv=0, k=1)
    # UpNDnLength=UpLen.attr('distance').get()+DnLen.attr('distance').get()
    # MovePos.UpDnLength.set(UpNDnLength)

    bc = blendColors_('%s%sAllStretch' % (side, ob))
    AllLen.distance >> bc.color1R
    adl.o >> bc.color2R

    # 갭 구하기
    gap_md = multiplyDivide_('%s%sStretchGap' % (side, ob))
    gap_md.operation.set(2)
    AllLen.distance >> gap_md.input1X
    adl.o >> gap_md.input2X
    gap_md.outputX >> bc.color1G

    # md=multiplyDivide_('%s%sAllStretchNormal'%(side,ob))
    # md.operation.set(2)
    # bc.outputR>>md.i1x
    # bc.color2.color2R>>md.i2x
    cd = condition_('%s%sAllLen' % (side, ob))
    cd.operation.set(2)

    cd_set = condition_('%s%sRatioSet' % (side, ob))
    cd_set.operation.set(5)
    cd_set.secondTerm.set(1)
    cd_set.colorIfTrueR.set(1)
    bc.outputG >> cd_set.firstTerm
    bc.outputG >> cd_set.colorIfFalseR

    cd_set.outColorR >> cd.colorIfTrueR
    bc.outputR >> cd.firstTerm
    adl.o >> cd.secondTerm

    # 폴벡터 스트레치
    PVPos = transform_('%s%sPVStretch' % (side, ob))
    pm.pointConstraint(PoleVectorCtrl, PVPos, mo=0)
    PVUpLenDB = distancBetween_('%s%sPVUpLen' % (side, ob))
    PVDnLenDB = distancBetween_('%s%sPVDnLen' % (side, ob))
    PVUpLen = PosLen(pos1, PVPos, PVUpLenDB)
    PVDnLen = PosLen(PVPos, MovePos, PVDnLenDB)

    pm.parent(PVPos, posGrp_)

    PVLens = [PVUpLen, PVDnLen]
    Lens = [UpLen, DnLen]
    JntConnectList = []
    for x in range(len(PVLens)):
        name_ = PVLens[x].replace('PV', '').replace('LenDB', '')

        pv_md = multiplyDivide_('%sPVStretchNormal' % name_)
        pv_md.operation.set(2)
        PVLens[x].distance >> pv_md.i1x
        Lens[x].distance >> pv_md.i2x

        ba = blendTwoAttr_('%sStretch' % name_)
        cd.outColorR >> ba.input[0]
        pv_md.ox >> ba.input[1]
        baMD = MDConnect(IKCtrl, 'PVStretch')
        baMD.o >> ba.attributesBlender

        # 슬라이드
        s_mdl = multDoubleLinear_('%sSlideFilter' % name_)
        s_adl = addDoubleLinear_('%sSlideFilter' % name_)
        s_mdl.input2.set(0.1)
        s_adl.input2.set(1)
        st_mdl = multDoubleLinear_('%sStretchFilter' % name_)

        pm.connectAttr(IKCtrl + '.%sSlide' % name_.replace(side + ob, ''), s_mdl + '.input1')
        s_mdl.o >> s_adl.input1
        s_adl.o >> st_mdl.input2

        ba.o >> st_mdl.input1

        # 모든 스트레치 값 합치기
        All_adl = multDoubleLinear_('%sStretchOutput' % name_)
        jointTrans = IKJnt[1 + x].attr('tx').get()
        All_adl.input2.set(jointTrans)
        st_mdl.o >> All_adl.input1

        JntConnectList.append(All_adl)

    UptretchOutputMDL = JntConnectList[0]
    DntretchOutputMDL = JntConnectList[1]

    UptretchOutputMDL.o >> IKJnt[1].tx
    DntretchOutputMDL.o >> IKJnt[2].tx

    md_ = MDConnect(IKCtrl, 'Stretch')
    md_.o >> bc.blender

    return posGrp_


# 트위스트 셋팅하기 

def PVTwistAim(DrvJnt,IKCtrlPos):
    name=side+ob
    fixGrp = pm.shadingNode('transform', au=1, n=side+ob+ 'PVFixGrp')
    aimGrp = pm.shadingNode('transform', au=1, n=side+ob+  'PVAimGrp')
    tgPos = pm.shadingNode('transform', au=1,n=side+ob+  'PVFixTgPos')
    upVec = pm.shadingNode('transform', au=1, n=side+ob+ 'PVFixUpvec')
    pos = pm.shadingNode('transform', au=1, n=side+ob+  'PVFixPos')
    FWpos = pm.shadingNode('transform', au=1, n=side + ob + 'PVFixPosFW')
    pm.parent(tgPos, upVec, aimGrp, fixGrp)
    pm.parent(pos, aimGrp)
    pm.parent(FWpos,pos)

    gn.PosCopy(DrvJnt[0], fixGrp)
    gn.PosCopy(DrvJnt[-1], tgPos)
    gn.PosCopy(DrvJnt[-1], upVec)
    pm.pointConstraint(IKCtrlPos, tgPos, mo=0)

    vp = pm.shadingNode('vectorProduct', au=1, n=DrvJnt[0].replace('DrvJnt', 'PVVP'))
    tgPos.t >> vp.input1
    vp.operation.set(1)
    vp.input2Y.set(1)
    vp.normalizeOutput.set(1)

    VPsetDriven(vp, upVec)
    PVAimConst=pm.aimConstraint(tgPos, aimGrp, mo=0, wut=2, wuo=upVec, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                worldUpVector=(0, 1, 0))
    pm.delete(pm.pointConstraint(DrvJnt[1],pos,mo=0))
    pm.delete(pm.orientConstraint(aimGrp,pos,mo=0))
    rxResult=pos.rx.get()
    pos.rx.set(rxResult+90)
    ryResult=pos.ry.get()
    pos.ry.set(rxResult+180)
    posGrp_=gn.addNPO(pos, 'Grp')
    FWpos.tz.set(-0.01)

    return fixGrp,PVAimConst

def VPsetDriven(sel1, sel2):
    driver = sel1 + '.outputX'
    driven = sel2 + '.rotateZ'

    pm.setDrivenKeyframe(driven, cd=driver, dv=-1, v=-90)
    pm.setDrivenKeyframe(driven, cd=driver, dv=0.0, v=0.0)
    pm.setDrivenKeyframe(driven, cd=driver, dv=1, v=90)


def TwistPosTop(DrvJnt, UpArcJnt):
    fixGrp = pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt', 'TwistFixGrp'))
    aimGrp = pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt', 'TwistAimGrp'))
    tgPos = pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt', 'TwistFixTgPos'))
    upVec = pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt', 'TwistFixUpvec'))
    pos = pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt', 'TwistFixPos'))
    pm.parent(tgPos, upVec, aimGrp, fixGrp)
    pm.parent(pos, aimGrp)

    pm.parent(fixGrp, UpArcJnt[0].getParent())

    gn.PosCopy(UpArcJnt[0], fixGrp)
    gn.PosCopy(UpArcJnt[-1], tgPos)
    gn.PosCopy(UpArcJnt[0], upVec)
    pm.pointConstraint(DrvJnt[1], tgPos, mo=0)

    vp = pm.shadingNode('vectorProduct', au=1, n=DrvJnt[0].replace('DrvJnt', 'TwistVP'))
    tgPos.t >> vp.input1
    vp.operation.set(1)
    if side == 'Right':
        vp.input2Y.set(-1)
    else:
        vp.input2Y.set(1)
    vp.normalizeOutput.set(1)

    VPsetDriven(vp, upVec)
    pm.aimConstraint(tgPos, aimGrp, mo=0, wut=2, wuo=upVec, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                     worldUpVector=(0, 1, 0))
    gn.Mcon(DrvJnt[0], fixGrp, t=1, mo=1, pvtCalc=1)

    return pos


def TwistPosTMid(DrvJnt, UpArcJnt, DnArcJnt):
    fixGrp = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixGrp'))
    aimGrp = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistAimGrp'))
    tgPos = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixTgPos'))

    pos = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixPos'))
    posUp = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixPosUp'))
    posDn = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixPosDn'))
    AssiA = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'AssiAPos'))
    AssiB = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'AssiBPos'))
    pm.parent(AssiB, tgPos, aimGrp, fixGrp)
    pm.parent(posUp, posDn, pos)
    pm.parent(pos, aimGrp)
    pm.parent(AssiA, DrvJnt[1])
    pm.parent(fixGrp, DrvJnt[0])
    pm.delete(pm.parentConstraint(UpArcJnt[-1], DnArcJnt[0], fixGrp, mo=0))
    tgPos.tx.set(1)

    gn.PosCopy(tgPos, AssiA)
    gn.PosCopy(tgPos, AssiB)

    pm.pointConstraint(AssiA, AssiB, tgPos, mo=1)

    pm.aimConstraint(tgPos, aimGrp, mo=0, wut=2, wuo=AssiA, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                     worldUpVector=(0, 1, 0))

    gn.PosCopy(UpArcJnt[-1], posUp)
    gn.PosCopy(DnArcJnt[0], posDn)

    gn.addNPO(posUp, 'Grp')
    gn.addNPO(posDn, 'Grp')

    return [posUp, posDn]


def TwistPosTDn(DrvJnt, DnArcJnt):
    fixGrp = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixGrp'))
    aimGrp = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistAimGrp'))
    tgPos = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixTgPos'))
    upVec = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixUpvec'))
    pos = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixPos'))
    posSub = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixSubPos'))
    AssiA = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'AssiAPos'))
    AssiB = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'AssiBPos'))
    pm.parent(AssiB, tgPos, upVec, aimGrp, fixGrp)
    pm.parent(pos, posSub, aimGrp)
    pm.parent(AssiA, DrvJnt[2])
    pm.parent(fixGrp, DrvJnt[1])

    pm.delete(pm.parentConstraint(DnArcJnt[-1], fixGrp, mo=0))
    tgPos.tx.set(1)

    gn.PosCopy(tgPos, AssiA)
    gn.PosCopy(tgPos, AssiB)

    pm.pointConstraint(AssiA, AssiB, tgPos, mo=1)

    pm.aimConstraint(tgPos, posSub, mo=0, wut=2, wuo=AssiA, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                     worldUpVector=(0, 1, 0))

    Grp_ = gn.addNPO(pos, 'Grp')
    posGrp = Grp_[0]
    pm.orientConstraint(posSub, posGrp, weight=1, mo=1)
    pm.orientConstraint(aimGrp, posGrp, weight=0.5, mo=1)

    return pos



def ArcnTwistConnect(ArcHandles, UpPos, DnPos, MidposUp, MidPosDn):
    ArcUpHandle = ArcHandles[0]
    ArcDnHandle = ArcHandles[1]

    UpPos.worldMatrix[0] >> ArcUpHandle.dWorldUpMatrix
    MidposUp.worldMatrix[0] >> ArcUpHandle.dWorldUpMatrixEnd

    MidPosDn.worldMatrix[0] >> ArcDnHandle.dWorldUpMatrix
    DnPos.worldMatrix[0] >> ArcDnHandle.dWorldUpMatrixEnd


def BindJntConnect(ArcJnt, JntSel_):
    BiJnt = gn.jntList(JntSel_, len(ArcJnt))
    for x in range(len(ArcJnt)):
        gn.Mcon(ArcJnt[x], BiJnt[x], t=1, r=1, mo=0, pvtCalc=1)


def BindJntScaleConnect(FKCtrls, UpArcJnt, DnArcJnt, JntSel, IKFKCtrl):
    FKCtrl = FKCtrls[0]
    ArcJntList = [UpArcJnt, DnArcJnt]
    JntSel_List = JntSel[:2]

    for i, j, k in zip(FKCtrl, ArcJntList, JntSel_List):
        PartJntSel = gn.jntList(k, len(j))
        for x in range(len(j)):
            F_bc = blendColors_(PartJntSel[x].replace('Jnt', 'Scale'))
            IKFKCtrl.IKFK >> F_bc.blender
            i.sy >> F_bc.color1G
            i.sz >> F_bc.color1B
            j[x].SquashScaleY >> F_bc.color2G
            j[x].SquashScaleZ >> F_bc.color2B
            F_bc.outputG >> PartJntSel[x].sy
            F_bc.outputB >> PartJntSel[x].sz

    # 손목 스케일 연결
    E_bc = blendColors_(JntSel[-1].replace('Jnt', 'Scale'))
    IKFKCtrl.IKFK >> E_bc.blender
    FKCtrl[-1].sy >> E_bc.color1G
    FKCtrl[-1].sz >> E_bc.color1B
    DnArcJnt[-1].SquashScaleY >> E_bc.color2G
    DnArcJnt[-1].SquashScaleZ >> E_bc.color2B
    E_bc.outputG >> JntSel[-1].sy
    E_bc.outputB >> JntSel[-1].sz


# 클래비클 or 힙 컨트롤 만들고 배치
def MakeHipCtrlRig(JntSel):
    Scale = gn.scaleGet()
    obj = 'LegRoot'
    Ctrl = gn.ControlMaker('%s%sCtrl' % (side, obj), 'crosspin', MainColor, exGrp=0, size=Scale)
    gn.PosCopy(JntSel[0], Ctrl[0])
    
    return Ctrl[0]

def MakeClavicleCtrlRig():
    ObjName = side + 'Clavicle'

    side_,ob_,parts_,colors_ = NameExtraction(ObjName)  
    ClavicleParts = parts_

    ClaJntSel = []
    for x in ClavicleParts[:-1]:
        jnt_=pm.PyNode('%s%sJnt'%(side,x))
        ClaJntSel.append(jnt_)

    Scale = gn.scaleGet()
    ClavicleCtrl = gn.ControlMaker('%sCtrl' %ObjName, 'circle', MainColor, exGrp=0, size=Scale*1.2)
    ClavicleSubCtrl = gn.ControlMaker('%sSubCtrl' % ObjName, 'diamond', SubColor, exGrp=0, size=Scale*1.2)
    gn.PosCopy(ClaJntSel[0], ClavicleCtrl[0])
    gn.PosCopy(ClaJntSel[1], ClavicleSubCtrl[0])
    pm.parent(ClavicleSubCtrl[0], ClavicleCtrl[0])
    gn.Mcon(ClavicleCtrl[0], ClaJntSel[0], t=1, r=1, s=1, sh=1,mo=1, pvtCalc=1)
    gn.Mcon(ClavicleSubCtrl[0], ClaJntSel[1], t=1, r=1, s=1, sh=1,mo=1, pvtCalc=1)
    gn.rotate_components(0, 0, 90, nodes=ClavicleCtrl[0])
    gn.rotate_components(0, 0, 90, nodes=ClavicleSubCtrl[0])
    pm.addAttr(ClavicleCtrl[0],ln="SubCtrlVis", at='bool', k=1)
    pm.setAttr(ClavicleCtrl[0].SubCtrlVis,0, keyable=0, channelBox=1)
    
    return ClavicleCtrl[0], ClavicleSubCtrl[0]

def AnotationRIg(PoleVectorCtrl):

    pm.annotate(PoleVectorCtrl, tx='' )



def ArmLegRig(JntSel):
    #IK 조인트, 컨트롤 
    IKJnt = DuplicateJnt(JntSel, 'IK')
    IKCtrls = IKRig(IKJnt)
    IKCtrlPos = IKCtrls[2]
    #FK 조인트, 컨트롤 
    FKJnt = DuplicateJnt(JntSel, 'FK')
    FKCtrls = FKRig(FKJnt)
    #IKFK 컨트롤과 연결
    IKFKCtrl = IKFKCtrlMake(JntSel)
    IKFKVisConnect(IKCtrls[0][1].getParent(), FKCtrls[0][0].getParent(), IKFKCtrl)
    #Drv 조인트와 IKFK 연결
    DrvJnt = DuplicateJnt(JntSel, 'Drv')
    sel = [FKJnt[0], IKJnt[0], DrvJnt[0], IKFKCtrl]
    kb.IKFKBlend(sel)
    #Arc 조인트와 포인트 
    ArcJnts = ArcRig(DrvJnt)
    ArcPosList = ArcJnts[4]

    UpArcJnt, DnArcJnt = ArcJnts[0], ArcJnts[1]
    f_UpArcJnt = pm.PyNode(UpArcJnt[0])
    e_UpArcJnt = pm.PyNode(UpArcJnt[-1])
    UpArcJntSel = [f_UpArcJnt, e_UpArcJnt]

    UpIKCrv, DnIKCrv = ArcJnts[3][0], ArcJnts[3][1]
    UpStSq = Spline(UpArcJntSel, UpIKCrv)

    f_DnArcJnt = pm.PyNode(DnArcJnt[0])
    e_DnArcJnt = pm.PyNode(DnArcJnt[-1])
    DnArcJntSel = [f_DnArcJnt, e_DnArcJnt]
    DnStSq = Spline(DnArcJntSel, DnIKCrv)
    
    #IK연결 
    IKCtrl = IKCtrls[0][0]
    PoleVectorCtrl = IKCtrls[1]
    IKPosGrp = IKNodeConnection(IKJnt, IKCtrl, PoleVectorCtrl)
    ArcHandles = ArcJnts[2]

    # 트위스트 잡는 것들
    UpPos = TwistPosTop(DrvJnt, UpArcJnt)    
    MidPosz = TwistPosTMid(DrvJnt, UpArcJnt, DnArcJnt)
    DnPos = TwistPosTDn(DrvJnt, DnArcJnt)
    MidposUp, MidPosDn = MidPosz[0], MidPosz[1]    
    PVfixGrp,PVAimConst = PVTwistAim(DrvJnt, IKCtrlPos)

    # 트위스트 잡는 것과 트위스트 스플라인 핸드 연결하기
    ArcnTwistConnect(ArcHandles, UpPos, DnPos, MidposUp, MidPosDn)
    
    # 트위스트 포스와 채널 연결
    IKFKCtrl.UpTwistFix>>UpPos.rx
    IKFKCtrl.MidTwistFix>>MidPosz[0].getParent().getParent().rx
    IKFKCtrl.DnTwistFix>>DnPos.rx
    IKCtrl.Twist>>PVAimConst.offsetX

    # 아크조인트와 바인드조인트 연결
    BindJntConnect(UpArcJnt, JntSel[0])
    BindJntConnect(DnArcJnt, JntSel[1])

    BindJntScaleConnect(FKCtrls, UpArcJnt, DnArcJnt, JntSel, IKFKCtrl)

    # 정리하기
    RigGrp = pm.createNode('transform', n='%s%sRigGrp' % (side, ob))
    SysGrp = pm.createNode('transform', n='%s%sSysGrp' % (side, ob),p=RigGrp)
    JntGrp = pm.createNode('transform', n='%s%sJntGrp' % (side, ob),p=SysGrp)
    pm.parent(UpPos.getParent().getParent(),IKJnt[0], FKJnt[0], DrvJnt[0], f_UpArcJnt, JntGrp)
    SysGrp.visibility.set(0)

    ArcCrvs = [DnStSq.getParent(), UpStSq.getParent()]
    pm.parent(PVfixGrp,  ArcHandles, IKPosGrp, ArcPosList, ArcCrvs, SysGrp)
    pm.group(ArcPosList,n='%s%sArcPos' % (side, ob))

    IKCtrl.PVctrlVis >> PoleVectorCtrl.getParent().visibility

    ConstCtrl = IKCtrls[0][1]
    IKSub = IKCtrls[0][2]
    IKSub.getParent().visibility.set(0)
    IKCtrl.ConstCtrlVis >> ConstCtrl.getShape().visibility
    
    ArcCrvGrp = pm.PyNode('%s%sArcCrvGrp' % (side, ob))
    pm.parent(ArcCrvGrp, SysGrp)

    IKHandle = pm.PyNode('%s%sIKHandle' % (side, ob))
    pm.parent(IKHandle, SysGrp)

    CtrlGrp = pm.createNode('transform', n='%s%sCtrlGrp' % (side, ob),p=RigGrp)

    arcUpCtrl = pm.PyNode('%s%sUpArcCtrlGrp' % (side, ob))
    arcMidCtrl = pm.PyNode('%s%sMidArcCtrlGrp' % (side, ob))
    arcDnCtrl = pm.PyNode('%s%sDnArcCtrlGrp' % (side, ob))

    pm.parent(PoleVectorCtrl.getParent(), ConstCtrl.getParent(), 
     arcUpCtrl, arcMidCtrl, arcDnCtrl, FKCtrls[0][0].getParent(), 
    IKFKCtrl.getParent(), CtrlGrp)
    
    IKChkCrvGrp = pm.createNode('transform', n='%s%sIKChkCrvGrp' % (side, ob) ,p=RigGrp)
    pm.parent( UpIKCrv.replace('Crv','ChkCrv'), DnIKCrv.replace('Crv','ChkCrv'), IKChkCrvGrp)
    
    pm.parent(UpIKCrv, DnIKCrv,'%s%sIKCrvGrp'% (side, ob))
    pm.parent('%s%sIKCrvGrp'% (side, ob),RigGrp)
    
    # 클래비클, 힙 컨트롤 만들기
    if ob == 'Arm':
        ObjRootCtrl, ObjRootSubCtrl = MakeClavicleCtrlRig()
        ObjRootCtrlGrp = gn.addNPO(ObjRootCtrl,'Grp')
        ObjRootSubCtrlGrp = gn.addNPO(ObjRootSubCtrl,'Grp') 
        ObjRootCtrl.SubCtrlVis>>  ObjRootSubCtrlGrp[0].visibility     
    else:
        ObjRootCtrl = MakeHipCtrlRig(JntSel)
        gn.rotate_components(180, 0, 0, nodes=ObjRootCtrl)
        ObjRootCtrlGrp = gn.addNPO(ObjRootCtrl,'Grp')
    
    for x in [CtrlGrp,SysGrp]:
        RootCNSGrp=pm.createNode('transform', n='%sCNSGrp' % (x.replace('Grp','')))
        gn.PosCopy(ObjRootCtrl,RootCNSGrp)
        pm.parent(x.getChildren(),RootCNSGrp)
        gn.Mcon(ObjRootCtrl, RootCNSGrp,t=1, r=1, s=1, sh=1,mo=1, pvtCalc=1)
        pm.parent(RootCNSGrp,x)
    pm.parent(ObjRootCtrlGrp,CtrlGrp)
    
    
    
    if ob == 'Arm':
        # 손목 로테이트 컨스트레인
        wristPB=pm.createNode('pairBlend', n= JntSel[-1] + 'RotPB')
        IKJnt[-1].r>>wristPB.ir1
        FKJnt[-1].r>>wristPB.ir2
        IKFKCtrl.IKFK>>wristPB.w
        wristPB.outRotate>>JntSel[-1].r
        gn.Mcon(IKCtrlPos, IKJnt[-1], r=1, mo=1, pvtCalc=1)
        if pm.objExists('ChestConstGrp'):   
            pm.parent(RigGrp, 'ChestConstGrp')
    elif ob == 'Leg':
        if pm.objExists('HipCtrl'):   
            pm.parent(RigGrp, 'HipCtrl')

        



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    


# 바인드 조인트의 첫번째, 중간, 마지막 조인트를 누르고 실행!

#ObjName = ['LeftArm','RightArm','LeftLeg','RightLeg']    
def ArmLegRigConvert():
    global Scale
    Scale=gn.scaleGet()
    ObjName = ['LeftArm','RightArm','LeftLeg','RightLeg']    
    for i in ObjName:
        global side,ob,parts,colors,MainColor, SubColor, fingerMainColor
        side,ob,parts,colors=NameExtraction(i)
        MainColor, SubColor, fingerMainColor = int(colors[0]), int(colors[1]), int(colors[2])
        JntSel = []
        for x in parts:
            jnt_=pm.PyNode('%s%sJnt'%(side,x))
            JntSel.append(jnt_)
        ArmLegRig(JntSel)

#ArmLegRigConvert()

tt=pm.ls(sl=1)[0]
trans = xform(tt, q=1, ws=1, rp=1 )
ii=pm.annotate(tt, tx='t', p=trans )