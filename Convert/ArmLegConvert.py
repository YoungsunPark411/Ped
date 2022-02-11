# -*- coding: cp949 -*-
import pymel.core as pm
import sys,os
if os.path.isdir('D:/Ped/Convert'):
   script_path = 'D:/Ped/Convert'
else:
   script_path = 'Z:/mvtools/scripts/rig/Script/Python3_script/Ped/Convert'
sys.path.insert(0, script_path)

import General as gn
import IKFKBlend as kb
import Seal_IKStretchSet as st
# reload(gn)
# reload(kb)

Scale=gn.scaleGet()

# ����Ʈ�����
def DuplicateJnt(JntSel,type):
    orgJnt=JntSel
    rstJnt=[]
    [ rstJnt.append( pm.createNode('joint',n='%s%sJnt'%(jnt.replace('Jnt',''),type) ) ) for jnt in orgJnt ]
    list(map( lambda a,b: gn.PosCopy(a,b), orgJnt, rstJnt ))
    for i in range(len(orgJnt)):
        if i==0: continue
        if '|' in rstJnt[i]:
            rstJnt[i]=rstJnt[i].replace('|','')
        pm.parent( rstJnt[i], rstJnt[i-1] )
        pm.makeIdentity(rstJnt[i],a=1, t=1,r=1,s=1,n=0,pn=1)

    pm.joint(rstJnt[0],e=1  ,oj ='xyz' ,secondaryAxisOrient= 'zdown',ch =1 ,zso=1)
    pm.makeIdentity(rstJnt[0],a=1, t=1,r=1,s=1,n=0,pn=1)
    pm.setAttr ("%s.jointOrientX"%rstJnt[-1], 0);
    pm.setAttr ("%s.jointOrientY"%rstJnt[-1], 0);
    pm.setAttr ("%s.jointOrientZ"%rstJnt[-1], 0);
    return rstJnt

def sideName(JntSel):
    if 'Left' in str(JntSel[0]):
        side='Left'
    elif 'Right' in str(JntSel[0]):
        side='Right'
    else:
        side='side'
    return side
def obName(JntSel):
    if 'Shoulder' in str(JntSel[0]):
        ob='Arm'
    elif 'Thigh' in str(JntSel[0]):
        ob='Leg'
    else:
        ob='ob'
    return ob


def Color(side):
    # �� ���ϱ�
    if 'Left' in side:
        MainColor = 13
        SubColor = 31
        fingerMainColor = 20
    elif 'Right' in side:
        MainColor = 6
        SubColor = 29
        fingerMainColor = 18   
    else:
        MainColor = 13
        SubColor = 31
        fingerMainColor = 20
    return [MainColor,SubColor,fingerMainColor]


# IK ��Ʈ�� �����
def IKCtrlMake(IKJnt):

    # ũ�� ���ϱ�
    Scale = gn.scaleGet()
    IKCtrl = gn.ControlMaker('%s%sIKCtrl'%(side,ob), 'circle', MainColor, exGrp=0, size=Scale)
    pm.select(IKCtrl[0])
    pm.addAttr(ln="Twist", at='double', dv=0, k=1)
    pm.addAttr(ln="Stretch", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="Squash", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="UpSlide", at='double', dv=0, k=1)
    pm.addAttr(ln="DnSlide", at='double', dv=0, k=1)
    pm.addAttr(ln="PVctrlVis", at='double', min=0, max=1, dv=0, k=1)
    pm.setAttr('%s%sIKCtrl.PVctrlVis'%(side,ob), keyable=0, channelBox=1)
    pm.addAttr(ln="PVStretch", at='double', min=0, max=10, dv=0, k=1)
    if 'Arm' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Head:Chest:Hip:Root:Fly', k=1)
        pm.setAttr(IKCtrl[0] + ".Follow", 1)
    elif 'Leg' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Hip:Root:Fly:World', k=1)
        FootFunction = ["FootRoll", "BallRoll", "BallRoll", "ToeRoll", "InOut", "HeelPivot", "BallPivot", "ToePivot"]
        for x in FootFunction:
            pm.addAttr(ln=x, at='double', min=-10, max=10, dv=0, k=1)
        pm.setAttr("%s%sIKCtrl.Follow"%(side,ob), 2)
    pm.addAttr(ln="ConstCtrlVis", at='double', min=0, max=1, dv=0, k=1)
    pm.setAttr(IKCtrl[0] + '.ConstCtrlVis', keyable=0, channelBox=1)
    IKConstCtrl = gn.ControlMaker('%s%sIKConstCtrl'%(side,ob), 'hexagon', MainColor, exGrp=0, size=Scale * 1.2)
    IKSubCtrl = gn.ControlMaker('%s%sIKSubCtrl'%(side,ob), 'circle', SubColor, exGrp=0, size=Scale * 0.8)
    gn.rotate_components(0, 0, 90, nodes=IKCtrl[0])
    gn.rotate_components(0, 0, 90, nodes=IKConstCtrl[0])
    gn.rotate_components(0, 0, 90, nodes=IKSubCtrl[0])
    return [IKCtrl[0],IKConstCtrl[0],IKSubCtrl[0]]

def IKCtrlMatch(IKJnt):
    IKCtrlList=IKCtrlMake(IKJnt)
    IKCtrl,IKConstCtrl,IKSubCtrl = IKCtrlList[0],IKCtrlList[1],IKCtrlList[2]
    pm.parent(IKCtrl, IKConstCtrl)
    pm.parent(IKSubCtrl, IKCtrl)
    gn.PosCopy(IKJnt[-1], IKConstCtrl)
    RX = IKConstCtrl.rotateX.get()
    IKConstCtrl.rotateX.set(RX -270)
    gn.addNPO(IKConstCtrl, 'Grp')
    gn.addNPO(IKCtrl, 'Grp')
    gn.addNPO(IKSubCtrl, 'Grp')
    
    return [IKCtrl,IKConstCtrl,IKSubCtrl]

def PolevectorMake(handle,IKJnt):

    PoleVectorCtrl = gn.ControlMaker('%s%sPoleVectorCtrl'%(side,ob), 'reverscheck', MainColor, exGrp=0, size=Scale)
    pm.select(PoleVectorCtrl[0])
    
    if ob == 'Arm':
        pm.addAttr(ln="Follow", at='enum', en='Auto:Chest:Root:Fly:World', k=1)
      
    elif ob=='Leg':
        pm.addAttr(ln="Follow", at='enum', en='Auto:Hip:Root:Fly:World', k=1)
    else:
        pass

    gn.PosCopy(IKJnt[1],PoleVectorCtrl[0])
    gn.addNPO(PoleVectorCtrl[0],'Grp')
    pm.poleVectorConstraint(PoleVectorCtrl[0], handle, n='%sPoleVectorConst' %handle.replace('IKHandle',''))
    return PoleVectorCtrl[0]


def IKRig(IKJnt):
    IKCtrlList=IKCtrlMatch(IKJnt)
    IKCtrl,IKConstCtrl,IKSubCtrl = IKCtrlList[0],IKCtrlList[1],IKCtrlList[2]
    IKHandle = pm.ikHandle(sj=IKJnt[0], ee=IKJnt[-1], n='%s%sIKHandle'%(side,ob), sol='ikRPsolver', ccv=0)
    #pm.parent(IKHandle[0], RigSysGrp)
    IKPos = pm.createNode('transform', n='%s%sIKPos'%(side,ob))
    gn.PosCopy(IKCtrl,IKPos)
    pm.parent(IKPos, IKCtrl)
    gn.Mcon(IKSubCtrl, IKHandle[0], t=1, mo=0, pvtCalc=1)
    poleCtrl=PolevectorMake(IKHandle[0],IKJnt)
    return [IKCtrlList,poleCtrl]

    
# def IKJntStretch(IKJnt):
    
    

# FK ���� �����
def FKCtrlMake(JntList,shape_,cns):
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

def FKRig(FKJnt):
    
    ctrl = FKCtrlMake(FKJnt,'RoundSquare',1)
    firstFKCtrl=ctrl[0][0]
    pm.select(firstFKCtrl)
    if 'Arm' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Clavicle:Chest:Root:Fly:World', k=1)
    elif 'Leg' in ob:
        pm.addAttr(ln="Follow", at='enum', en='Hip:Root:Fly:World', k=1)
    return ctrl

xyzList=['x','y','z']
trsList = ['t', 'r', 's']

#Drv ���� �����
def IKFKCtrlMake(JntSel):
    IKFKCtrl = gn.ControlMaker('%s%sIKFKCtrl'%(side,ob), 'switch', MainColor, exGrp=1, size=Scale)
    for i,j in zip(xyzList,trsList):
        pm.setAttr(IKFKCtrl[0]+'.'+j+i, lock=1, k=0, channelBox=0)
    pm.select(IKFKCtrl[0])
    pm.addAttr(ln="IKFK", at='double', min=0, max=1, dv=0, k=1)
    pm.addAttr(ln="Arc", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="UpTwistFix", at='double', dv=0, k=1)
    pm.addAttr(ln="DnTwistFix", at='double', dv=0, k=1)
    pm.addAttr(ln="AutoHideIKFK", at='enum', en='Off:On', k=1)
    pm.addAttr(ln="ArcCtrlVis", at='enum', en='Off:On', k=1)
    pm.setAttr(IKFKCtrl[0]+'.AutoHideIKFK', keyable=0, channelBox=1)
    pm.setAttr(IKFKCtrl[0]+'.ArcCtrlVis', keyable=0, channelBox=1)
    gn.PosCopy(JntSel[-1],IKFKCtrl[1])
    gn.Mcon(JntSel[-1],IKFKCtrl[1],t=1, r=0, s=0, sh=1, mo=1, pvtCalc=1)
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

def IKFKVisConnect(IKCtrlGrp,FKCtrlGrp,IKFKCtrl):
    switch=IKFKCtrl
    FKCtrlGrp_=FKCtrlGrp
    IKCtrlGrp_ = IKCtrlGrp
    rev = pm.createNode('reverse', n='%s%sRV'%(side,ob))
    cd = pm.createNode('condition', n='%s%sCD'%(side,ob))
    cd.secondTerm.set(1)
    switch.IKFK >> cd.colorIfTrue.colorIfTrueR
    switch.IKFK >> rev.input.inputX
    switch.AutoHideIKFK >> cd.firstTerm
    switch.AutoHideIKFK.set(1)
    rev.output.outputX >> cd.colorIfTrue.colorIfTrueG
    cd.outColor.outColorR >>FKCtrlGrp_.visibility
    cd.outColor.outColorG >> IKCtrlGrp_.visibility

#Arc ���� �����
def ArcCtrlMake():
    UpArcCtrl = gn.ControlMaker('%s%sUpArcCtrl'%(side,ob) , 'hexagon', SubColor, exGrp=0, size=Scale)
    MidArcCtrl = gn.ControlMaker('%s%sMidArcCtrl'%(side,ob) , 'hexagon', SubColor, exGrp=0, size=Scale)
    DnArcCtrl = gn.ControlMaker('%s%sDnArcCtrl'%(side,ob) , 'hexagon', SubColor, exGrp=0, size=Scale)
    #LongJnt=kb.getChildren_(JntSel[0], type_='joint')
    #ArcJntMatchList=[LongJnt[2],LongJnt[4],LongJnt[6]]
    ArcCtrlList=[UpArcCtrl[0],MidArcCtrl[0],DnArcCtrl[0]]
    for i in ArcCtrlList:
        gn.rotate_components(0, 0, 90, nodes=i)
    # for i,j in zip(ArcJntMatchList,ArcCtrlList):
    #     gn.rotate_components(0, 0, 90, nodes=j)
    #     gn.PosCopy(i,j)
    #     gn.addNPO(j,'Grp')
    return  ArcCtrlList
def CurveToPC(src,tg):
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
    cm.outputMatrix>>mm.matrixIn[0]      
    pc.result.position>>cm.inputTranslate
    src.worldSpace[0]>>pc.inputCurve
    pc.turnOnPercentage.set(1)
    pc.parameter.set(0.5)
    return pc
            
def ArcCtrlMatch(DrvJnt,UpIKCrv,DnIKCrv,ArcPointPos,bs):
    ArcCtrlList=ArcCtrlMake()
    UpArcCtrl,MidArcCtrl,DnArcCtrl=ArcCtrlList[0],ArcCtrlList[1],ArcCtrlList[2]
    for x in ArcCtrlList:
        grp_=gn.addNPO(x,'Grp')

        if x==UpArcCtrl :
            pm.delete(pm.pointConstraint(DrvJnt[0],DrvJnt[1],grp_[0],mo=0))
            #gn.Mcon(UpIKCrv,grp_[0],t=1, r=0, s=0, sh=1, mo=1, pvtCalc=1)
            tc=pm.tangentConstraint(UpIKCrv,grp_,wut=2,wuo=DrvJnt[0])
            print(tc)
            tg=grp_[0]
            src=UpIKCrv
            pc=CurveToPC(src,tg)
            bs.outputGeometry[0]>>pc.inputCurve
            bs.outputGeometry[0]>>tc.target[0].targetGeometry
            
        elif x==MidArcCtrl :
            pm.delete(pm.pointConstraint(DrvJnt[1],grp_[0],mo=0))
            pm.parentConstraint(DrvJnt[0],grp_[0],mo=1)
            PBgrp_=gn.addNPO(x,'PBGrp')
            pm.pointConstraint(ArcPointPos,PBgrp_)
            pm.orientConstraint(DrvJnt[0],PBgrp_)
            gn.PairBlend(PBgrp_[0], r=1, t=1, sh=1,mo=0,pvtCalc=1)
            PBgrp_[0].pbw.set(0.5)
        elif x==DnArcCtrl:
            pm.delete(pm.pointConstraint(DrvJnt[1],DrvJnt[2],grp_[0],mo=0))
            #gn.Mcon(DnIKCrv,grp_[0],t=1, r=0, s=0, sh=1, mo=1, pvtCalc=1)
            tc2=pm.tangentConstraint(DnIKCrv,grp_,wut=2,wuo=DrvJnt[-1])
            tg=grp_[0]
            src=DnIKCrv
            pc=CurveToPC(src,tg)
            bs.outputGeometry[1]>>pc.inputCurve
            print('ok')
            bs.outputGeometry[1]>>tc2.target[0].targetGeometry
            print('ok2')
    return ArcCtrlList
    

def ArcCurveMake(DrvJnt):
    Crv=gn.CrvFromJnt(DrvJnt)

    #ArcPosConnect
    PosList=[]
    for x in range(len(DrvJnt)):        
        Pos=pm.createNode('transform',n=DrvJnt[x].replace('Jnt','ArcPos').replace('|',''))
        pm.pointConstraint(DrvJnt[x],Pos,mo=0)
        PosList.append(Pos)
        
    #Pos->ArcPointPos
    App = pm.createNode('transform', n='%s%sArcPointPos'%(side,ob))
    AUpDB = pm.createNode('distanceBetween', n='%s%sArcUpDB'%(side,ob))
    PosList[0].t>>AUpDB.point1
    PosList[1].t >> AUpDB.point2
    ADnDB = pm.createNode('distanceBetween', n='%s%sArcDnDB'%(side,ob))
    PosList[1].t >> ADnDB.point1
    PosList[2].t >> ADnDB.point2
    ADL=pm.createNode('addDoubleLinear',n='%s%sArcPointADL'%(side,ob))
    AUpDB.distance>>ADL.input1
    ADnDB.distance >> ADL.input2
    MDL=pm.createNode('multDoubleLinear',n='%s%sArcPointMDL'%(side,ob))
    ADL.output>>MDL.input1
    MDL.input2.set(3)
    PointCNS=pm.pointConstraint(PosList[0],PosList[1],PosList[2],App)
    PointCNS.offsetZ.set(-0.05)
    pm.connectAttr(ADnDB+'.distance',PointCNS+'.%sW0'%PosList[0])
    pm.connectAttr(MDL + '.output', PointCNS + '.%sW1' % PosList[1])
    pm.connectAttr(AUpDB + '.distance', PointCNS + '.%sW2' % PosList[-1])

    # ArcPointPos->...
    TPC = pm.createNode('makeThreePointCircularArc', n='%s%sTPC'%(side,ob))
    PosList[0].t >> TPC.point1
    App.t>>TPC.point2
    PosList[2].t >> TPC.point3
    ArcDT = pm.createNode('detachCurve', n='%s%sArcDetach'%(side,ob))
    TPC.outputCurve>>ArcDT.inputCurve
    #detach parameter ����
    PMP1= pm.createNode('plusMinusAverage', n='%s%sArcPos1_App'%(side,ob))
    PMP1.operation.set(2)
    App.t>>PMP1.input3D[1]
    PosList[0].t >> PMP1.input3D[0]
    PMP2 = pm.createNode('plusMinusAverage', n='%s%sApp_ArcPos3'%(side,ob))
    PMP2.operation.set(2)
    PosList[2].t >> PMP2.input3D[1]
    App.t >> PMP2.input3D[0]
    PMP3 = pm.createNode('plusMinusAverage', n='%s%sArcPos3_ArcPos1'%(side,ob))
    PMP3.operation.set(2)
    PosList[2].t >> PMP3.input3D[1]
    PosList[0].t >> PMP3.input3D[0]
    ArcInAB = pm.createNode('angleBetween', n='%s%sArcInAB'%(side,ob))
    PMP1.output3D>>ArcInAB.vector1
    PMP3.output3D>>ArcInAB.vector2
    ArcOutAB = pm.createNode('angleBetween', n='%s%sArcOutAB'%(side,ob))
    PMP2.output3D >> ArcOutAB.vector1
    PMP3.output3D >> ArcOutAB.vector2
    ArcAngleSR = pm.createNode('setRange', n='%s%sArcAngleSR'%(side,ob))
    TPC.sections>>ArcAngleSR.max.maxX
    ArcAngleADL = pm.createNode('addDoubleLinear', n='%s%sArcAngleADL'%(side,ob))
    ArcInAB.axisAngle.angle>>ArcAngleADL.input1
    ArcOutAB.axisAngle.angle >> ArcAngleADL.input2
    ArcAngleADL.output>>ArcAngleSR.oldMax.oldMaxX
    ArcOutAB.axisAngle.angle >> ArcAngleSR.value.valueX

    ArcDetach=pm.createNode('detachCurve', n='%s%sArcDetach'%(side,ob))
    ArcAngleSR.outValue.outValueX >>ArcDetach.parameter[0]
    TPC.outputCurve>>ArcDetach.inputCurve

    # Ŀ�� �ڸ���
    CrvList = pm.detachCurve("%s.ep[1]" % Crv, ch=1, cos=1,rpo=1)

    UpArcCrv = pm.rename(CrvList[1], '%s%sUpArcCrv'%(side,ob))
    DnArcCrv = pm.rename(CrvList[0], '%s%sDnArcCrv'%(side,ob))
    N_CrvList=[UpArcCrv,DnArcCrv]  

    UpIKCrv=pm.duplicate(UpArcCrv,n='%s%sUpIKCrv'%(side,ob))[0]
    DnIKCrv = pm.duplicate(DnArcCrv,n='%s%sDnIKCrv'%(side,ob))[0]
    
    
    IKCrvList=[UpIKCrv,DnIKCrv]
    for x in IKCrvList:
        cls=pm.cluster(x)
        orig=pm.listRelatives(x,s=1)[-1]
        if x == IKCrvList[0]:
            PosList[0].t >> orig.controlPoints[0]
            PosList[1].t >> orig.controlPoints[1]
        else:
            PosList[1].t >> orig.controlPoints[0]
            PosList[2].t >> orig.controlPoints[1]
        pm.delete(cls)
        pm.rebuildCurve(x, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)

        
    for i in N_CrvList:
        Rbd=pm.rebuildCurve(i, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)

    IKCrvGrp=pm.group(UpIKCrv,DnIKCrv,n='%s%sIKCrvGrp'%(side,ob))
    ArcCrvGrp=pm.group(UpArcCrv,DnArcCrv,n='%s%sArcCrvGrp'%(side,ob))
    
        
    #Ŀ�� �����彦�� 
    bs=pm.blendShape(ArcCrvGrp,IKCrvGrp,n='%s%sArcBS'%(side,ob))[0]
    ArcMDL=pm.createNode('multDoubleLinear',n='%s%sArcMDL'%(side,ob))
    ArcMDL.input2.set(0.1)
    IKFKCtrl=pm.PyNode('%s%sIKFKCtrl'%(side,ob))
    IKFKCtrl.Arc>>ArcMDL.input1
    pm.connectAttr(ArcMDL.output,bs+'.%s%sArcCrvGrp'%(side,ob))
    #ArcMDL.output>>bs.%s%sArcCrvGrp

    UpIKChkCrv = pm.duplicate(UpIKCrv, n='%s%sUpIKChkCrv'%(side,ob))[0]
    DnIKChkCrv = pm.duplicate(DnIKCrv, n='%s%sDnIKChkCrv'%(side,ob))[0]
    #IKChkCrvGrp=pm.group(UpIKChkCrv,DnIKChkCrv, n='%s%sIKChkCrvGrp')
    #pm.parent(IKChkCrvGrp,EtcGrp)
    pm.parentConstraint(DrvJnt[0], UpIKChkCrv, mo=1)
    pm.parentConstraint(DrvJnt[1], DnIKChkCrv, mo=1)


    UpArcCrvSh=pm.listRelatives(UpArcCrv,s=1)[0]
    DnArcCrvSh=pm.listRelatives(DnArcCrv,s=1)[0]
 
    ArcDetach.outputCurve[0]>>UpArcCrvSh.create
    ArcDetach.outputCurve[1] >> DnArcCrvSh.create
    
    #ArcCtrl ����� ��ġ ��Ű�� 
    ArcCtrlList=ArcCtrlMatch(DrvJnt,UpIKCrv,DnIKCrv,App,bs)
   
    for i in IKCrvList:
        Rbd=pm.rebuildCurve(i, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)

    #pm.rebuildCurve(N_CrvList[0], ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)
    #pm.rebuildCurve(N_CrvList[1], ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=2, d=3, tol=0.01)
    
    #organize
    # pm.parent(App,IKCrvGrp,ArcCrvGrp,EtcGrp)

    return [PosList,UpIKCrv,DnIKCrv,UpArcCrv,DnArcCrv,ArcCtrlList]


def ArcSplineRig(PosNCrv_,UpArcJnt,DnArcJnt):
    PosNCrv=PosNCrv_
    PosList,UpIKCrv,DnIKCrv,UpArcCrv,DnArcCrv = PosNCrv[0],PosNCrv[1],PosNCrv[2],PosNCrv[3],PosNCrv[4]

    #ArcSpline
    UpikHandle = pm.ikHandle(sj=UpArcJnt[0], ee=UpArcJnt[-1], n='%s%sUpArcHandle'%(side,ob), sol='ikSplineSolver', ccv=0,c=UpIKCrv)
    Uphandle=UpikHandle[0]
    Uphandle.dTwistControlEnable.set(1)
    Uphandle.dWorldUpType.set(4)
    DnikHandle = pm.ikHandle(sj=DnArcJnt[0], ee=DnArcJnt[-1], n='%s%sDnArcHandle'%(side,ob), sol='ikSplineSolver', ccv=0,c=DnIKCrv)
    Dnhandle = DnikHandle[0]
    Dnhandle.dTwistControlEnable.set(1)
    Dnhandle.dWorldUpType.set(4)

    #pm.parent('%s%sUpIKCrv','%s%sDnIKCrv','%s%sIKCrvGrp')

def ArcCtrlRig(ArcCtrls):
    ArcCtrlList=ArcCtrls
    N_CrvList=['%s%sUpIKCrv'%(side,ob),'%s%sDnIKCrv'%(side,ob)]
    for x in N_CrvList:
        i=pm.PyNode(x)
        N_cls1 = pm.cluster(i.cv[1:3], n='%s1Cls' % i)

        pm.percent(N_cls1[0], '%sShape.cv[1]' % i, v=0.5)
        pm.percent(N_cls1[0], '%sShape.cv[3]' % i, v=0.5)
        if 'Up' in x:
           
            N_cls2 = pm.cluster(i.cv[3:4], n='%s2Cls' % i)
            pm.percent(N_cls2[0], '%sShape.cv[3]' % i, v=0.5)
            pm.parent(N_cls1,ArcCtrlList[0])
            
            ArcCtrlList[0].t>>N_cls1[1].t
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
        pm.parent( N_cls2[1], ArcCtrlList[1])
        pm.select(N_cls1[1])
        clsGrp1=gn.MakeBindPreMtxCluster()        
        pm.select(N_cls2[1])
        clsGrp2=gn.MakeBindPreMtxCluster()

        
        CtrlGrp1=pm.listRelatives(ArcCtrlList[0],p=1)[0]
 
        if 'Up' in x:
            CtrlGrp1=pm.listRelatives(ArcCtrlList[0],p=1)[0]
        elif 'Dn' in x:
            CtrlGrp1=pm.listRelatives(ArcCtrlList[2],p=1)[0]
        pm.parent(clsGrp1,CtrlGrp1)
        gn.PosCopy(CtrlGrp1,clsGrp1)
        
        CtrlGrp2=pm.listRelatives(ArcCtrlList[1],p=1)[0]
        pm.parent(clsGrp2,CtrlGrp2)
        gn.PosCopy(CtrlGrp2,clsGrp2)
        list=[clsGrp1,clsGrp2]
        
        clsGrp1.visibility.set(0)
        clsGrp2.visibility.set(0)

def ArcJntMake(Crv,JntSel):
    # Chain = kb.getChildren_(JntSel[0], type_='joint')
    # segNumber=len(Chain)
    segNumber=5
    arcJnt=gn.JntMake(Crv,segNumber, 'Arc')
    
    return arcJnt
    
    
def ArcRig(JntSel):
    
    posNCrv=ArcCurveMake(JntSel)
    UpIKCrv,DnIKCrv=posNCrv[1],posNCrv[2]
    UpArcJnt=ArcJntMake(UpIKCrv,JntSel)
    DnArcJnt=ArcJntMake(DnIKCrv,JntSel)
    ArcSplineRig(posNCrv,UpArcJnt,DnArcJnt)
    
    pm.parent(DnArcJnt[0],UpArcJnt[-1])
    ArcJnt = kb.getChildren_(UpArcJnt[0], type_='joint')
    ArcCtrls=posNCrv[-1]
    ArcCtrlRig(ArcCtrls)
    return [UpArcJnt,DnArcJnt]
    
# ��Ʈ��ġ ������ ���� 
def connectStretchSquash(sel):
    name_=sel[0].replace('Jnt','')
    stMDL = pm.PyNode(name_.replace('1', '') + 'StretchMDL')
    sqMDL = pm.PyNode(name_.replace('1', '') + 'SquashMDL')
    
    IKFKCtrl=pm.PyNode('%s%sIKCtrl'%(side,ob))

    #pm.addAttr(IKFKCtrl,ln="Stretch", at='double',  min=0, max=10, dv=0, k=1)
    #pm.addAttr(IKFKCtrl, ln="Squash", at='double',  min=0, max=10, dv=0, k=1)

    IKFKCtrl.Stretch>>stMDL.input1
    IKFKCtrl.Squash >> sqMDL.input1

def Spline(sel):
    crv_Jnt=st.IKStretch(sel)
    # crv_=crv_Jnt[0]
    # Jnt_=crv_Jnt[1]
    connectStretchSquash(sel)



# #Bind ����
# def BindRig():
#     for (i,j) in zip(ArcJnt,orgJnt):
#         gn.Mcon(i,j,t=1, r=1, sh=1, mo=1, pvtCalc=1)

# #RootCtrl �����
# def RootCtrlMake():

#     if 'Arm' in ob:
#         result=pm.createNode('transform',n='%s%sRootGrp')
#         gn.PosCopy(orgJnt[0], result)
#         pm.parent(result, CtrlGrp)
        
#     else:
#         RootCtrl = gn.ControlMaker('%s%sRootCtrl', 'crosspin', MainColor, exGrp=0, size=Scale)
#         RootCtrl[0].sx.set(lock=1, k=0, channelBox=0)
#         RootCtrl[0].sy.set(lock=1, k=0, channelBox=0)
#         RootCtrl[0].sz.set(lock=1, k=0, channelBox=0)
#         gn.PosCopy(orgJnt[0], RootCtrl[0])
#         pm.parent(RootCtrl[0], CtrlGrp)
#         gn.addNPO(RootCtrl[0], 'Grp')
#         result=RootCtrl[0]
#     return result

#��Ʈ��ġ���尪����� (������ü����,����Up����,����Dn����)

def Divide(numerator, denominator): 
    nm=str(numerator)
    if 'All' in nm:
        name='All'        
    elif 'Up' in nm:
        name='Up'
    elif 'Dn' in nm:
        name='Dn'
    elif 'PV' in nm:
        name='PV'

    RatioMD = pm.createNode('multiplyDivide', n='%s%s%sRatioMD'%name)
    RatioMD.operation.set(2)
    numerator.distance >> RatioMD.input1X
    attr_='%sLength'%name
    denominator.attr(attr_) >> RatioMD.input2X
    
    return RatioMD
   



def Stretch(UpDB,DnDB,IKCtrl,IKJnt):
    pos1=IKJnt[0]
    pos3=pm.createNode('transform', n=IKJnt[-1].replace('Jnt','StretchPos'))
    IKSubCtrl=pm.PyNode('%s%sIKSubCtrl'%(side,ob))
    pm.pointConstraint(IKSubCtrl,pos3)
    #pm.parent(pos3,EtcGrp)
    
   
    AllDB = pm.createNode('distanceBetween', n='%s%sAllLengthDB'%(side,ob))
    print('ok')
    pos1.t >> AllDB.point1
    pos3.t >> AllDB.point2
    SaveLen = RigGrp
    pm.addAttr(SaveLen,ln="AllLength", at='double', dv=0, k=1)
    pm.addAttr(SaveLen, ln="UpLength", at='double', dv=0, k=1)
    pm.addAttr(SaveLen, ln="DnLength", at='double', dv=0, k=1)
    UpDB=pm.PyNode('%s%sArcUpDB'%(side,ob))
    DnDB = pm.PyNode('%s%sArcDnDB'%(side,ob))
    SaveLen.AllLength.set(AllDB.distance.get())
    SaveLen.UpLength.set(UpDB.distance.get())
    SaveLen.DnLength.set(DnDB.distance.get())

    # ��ü����
    AllRatioMD = Divide(AllDB, SaveLen)

    # PV�� Pos ����
    PVPos = pm.createNode('transform', n='%s%sPVPos'%(side,ob))
    PVCtrl = pm.PyNode('%s%sPoleVectorCtrl'%(side,ob))
    pm.pointConstraint(PVCtrl, PVPos, mo=0)
    pm.parent(PVPos, EtcGrp)
    UpPVDB = pm.createNode('distanceBetween', n='%s%sUpPVRatioDB'%(side,ob))
    pos1.t >> UpPVDB.point1
    PVPos.t >> UpPVDB.point2
    DnPVDB = pm.createNode('distanceBetween', n='%s%sDnPVRatioDB'%(side,ob))
    pos3.t >> DnPVDB.point1
    PVPos.t >> DnPVDB.point2

    # PV�� Pos �������ϱ�
    UpPVRatioMD = Divide(UpPVDB, SaveLen)
    DnPVRatioMD = Divide(DnPVDB, SaveLen)

    # �κк������ϱ�
    UpRatioMD = Divide(UpDB, SaveLen)
    DnRatioMD = Divide(DnDB, SaveLen)

    #��Ʈ��ġ ����ġ
    STSwitchBA=pm.createNode('blendTwoAttr', n='%s%sSTSwitchBA'%(side,ob))
    STSwitchBA.input[0].set(1)
    AllRatioMD.outputX>>STSwitchBA.input[1]
    STSwitchMDL = pm.createNode('multDoubleLinear', n='%s%sSTSwitchMDL'%(side,ob))
    STSwitchMDL.input2.set(0.1)
    IKCtrl.Stretch >> STSwitchMDL.input1
    STSwitchMDL.output>>STSwitchBA.attributesBlender

    #DnPV ��Ʈ��ġ ����ġ
    DnPVSwitchBA = pm.createNode('blendTwoAttr', n='%s%sDnPVSwitchBA'%(side,ob))
    STSwitchBA.output>>DnPVSwitchBA.input[0]
    DnPVRatioMD.outputX>>DnPVSwitchBA.input[1]
    DnPVSwitchMDL = pm.createNode('multDoubleLinear', n='%s%sSTDnPVSwitchL'%(side,ob))
    DnPVSwitchMDL.input2.set(0.1)
    IKCtrl.PVStretch >> DnPVSwitchMDL.input1
    DnPVSwitchMDL.output >> DnPVSwitchBA.attributesBlender

    # UpPV ��Ʈ��ġ ����ġ
    UpPVSwitchBA = pm.createNode('blendTwoAttr', n='%s%sUpPVSwitchBA'%(side,ob))
    STSwitchBA.output >> UpPVSwitchBA.input[0]
    UpPVRatioMD.outputX >> UpPVSwitchBA.input[1]
    UpPVSwitchMDL = pm.createNode('multDoubleLinear', n='%s%sSTUpPVSwitchL'%(side,ob))
    UpPVSwitchMDL.input2.set(0.1)
    IKCtrl.PVStretch >> UpPVSwitchMDL.input1
    UpPVSwitchMDL.output >> UpPVSwitchBA.attributesBlender

    # Dn�����̵� ��Ʈ��ġ ����ġ
    DnSlideSwitchMDL = pm.createNode('multDoubleLinear', n='%s%sDnSlideSwitchMDL'%(side,ob))
    DnSlideSwitchMDL.input2.set(0.1)
    IKCtrl.DnSlide >> DnSlideSwitchMDL.input1
    DnSlideSwitchADL = pm.createNode('addDoubleLinear', n='%s%sDnSlideSwitchADL'%(side,ob))
    DnSlideSwitchADL.input2.set(1)
    DnSlideSwitchMDL.output >> DnSlideSwitchADL.input1
    DnSlideXDnPVMDL = pm.createNode('multDoubleLinear', n='%s%sDnSlideXDnPVMDL'%(side,ob))
    DnSlideSwitchADL.output >> DnSlideXDnPVMDL.input1
    DnPVSwitchBA.output >> DnSlideXDnPVMDL.input2

    # Up�����̵� ��Ʈ��ġ ����ġ
    UpSlideSwitchMDL = pm.createNode('multDoubleLinear', n='%s%sUpSlideSwitchMDL'%(side,ob))
    UpSlideSwitchMDL.input2.set(0.1)
    IKCtrl.UpSlide >> UpSlideSwitchMDL.input1
    UpSlideSwitchADL = pm.createNode('addDoubleLinear', n='%s%sUpSlideSwitchADL'%(side,ob))
    UpSlideSwitchADL.input2.set(1)
    UpSlideSwitchMDL.output >> UpSlideSwitchADL.input1
    UpSlideXUpPVMDL = pm.createNode('multDoubleLinear', n='%s%sUpSlideXUpPVMDL'%(side,ob))
    UpSlideSwitchADL.output >> UpSlideXUpPVMDL.input1
    UpPVSwitchBA.output >> UpSlideXUpPVMDL.input2

    #Dn ��Ʈ��ġ ���� ����
    DnSTCD=pm.createNode('condition', n='%s%sDnSTCD'%(side,ob))
    DnSTCD.secondTerm.set(1)
    DnSTCD.operation.set(2)
    DnSlideXDnPVMDL.output>>DnSTCD.firstTerm
    DnSlideXDnPVMDL.output >> DnSTCD.colorIfTrueR
    DnSTCD.colorIfFalseR.set(1)
    DnSTFinalMDL = pm.createNode('multDoubleLinear', n='%s%sDnSTFinalMDL'%(side,ob))
    DnSTCD.outColorR>>DnSTFinalMDL.input1
    SaveLen.DnLength>>DnSTFinalMDL.input2
    DnSTFinalMDL.output >> IKJnt[-1].translateX

    # Up ��Ʈ��ġ ���� ����
    UpSTCD = pm.createNode('condition', n='%s%sUpSTCD'%(side,ob))
    UpSTCD.secondTerm.set(1)
    UpSTCD.operation.set(2)
    UpSlideXUpPVMDL.output >> UpSTCD.firstTerm
    UpSlideXUpPVMDL.output >> UpSTCD.colorIfTrueR
    UpSTCD.colorIfFalseR.set(1)
    UpSTFinalMDL = pm.createNode('multDoubleLinear', n='%s%sUpSTFinalMDL'%(side,ob))
    UpSTCD.outColorR >> UpSTFinalMDL.input1
    SaveLen.UpLength >> UpSTFinalMDL.input2
    UpSTFinalMDL.output >> IKJnt[1].translateX
    print('okok')

def distancBetween_(name_):
    return shadingNode('distanceBetween', au=1, n='{}DB'.format(name_))

def transform_(name_):
    return shadingNode('transform', au=1, n='{}Pos'.format(name_))
    
def StretchPractice(IKJnt):
    posList=[]
    for x in IKJnt:
        posMake=transform_(x.replace('Jnt','Pos'))
        posList.append(posMake)
        pm.delete(pm.parentConstraint(x,posMake))
    pos1,pos2,pos3=posList[0],posList[1],posList[2]
    pm.group(posList,n='%s%sPosGrp'%(side,ob))
    
    UpLen=distancBetween_('%s%sUpLen'%(side,ob))
    DnLen=distancBetween_('%s%sDnLen'%(side,ob))
    
    pos1.t>>UpLen.point1
    pos2.t>>UpLen.point2
    pos2.t>>DnLen.point1
    pos3.t>>DnLen.point2

    IKCtrl=pm.PyNode('%s%sIKCtrl'%(side,ob))
    Stretch(UpLen,DnLen,IKCtrl,IKJnt)


# def TwistUpEnd():
#     #TwistUpPos1 �����
#     TwistUpPos1=pm.createNode('transform',n='%s%s%sTwistUpPos'%subob[0])
#     IKFKCtrl=pm.PyNode('%s%sIKFKCtrl')
#     if side == 'Left':
#         TwistUpPosMDL=pm.createNode('multDoubleLinear',n='%s%sTwistUpPosMDL')
#         TwistUpPosMDL.input2.set(-1)
#         IKFKCtrl.UpTwistFix>>TwistUpPosMDL.input1
#     else:
#         IKFKCtrl.UpTwistFix>>TwistUpPos1.rotateX
#     TwistUpPos1Grp=gn.addNPO(TwistUpPos1, 'Grp')[0]
#     TwistUpAimPos = pm.createNode('transform', n='%s%s%sTwistUpAimPos' % subob[0])
#     TwistUpVecPos = pm.createNode('transform', n='%s%s%sTwistUpVecPos' % subob[0])
#     gn.PosCopy(DrvJnt[1],TwistAimPos1,t=1,r=1,mo=0)
#     gn.PosCopy(TwistUpPos1Grp, TwistAimPos1, t=1, r=1,mo=0)
#     TwistUpFixGrp = pm.createNode('transform', n='%s%s%sTwistUpFixGrp' % subob[0])
#     pm.parent(TwistUpVecPos,TwistUpAimPos,sTwistUpPos1FixGrp)

#     # TwistUpPos1 ����
#     pm.pointConstraint(DrvJnt[0],TwistUpAimPos,mo=1)
#     TwistVP=pm.createNode('vectorProduct',n='%s%sTwistVP')
#     TwistUpAimPos.translate>>TwistVP.input1
#     pm.setDrivenKeyframe(TwistUpVecPos + '.rotateZ', cd=TwistVP + '.outputX', dv=-1, v=-90)
#     pm.setDrivenKeyframe(TwistUpVecPos + '.rotateZ', cd=TwistVP + '.outputX', dv=0, v=0)
#     pm.setDrivenKeyframe(TwistUpVecPos + '.rotateZ', cd=TwistVP + '.outputX', dv=1, v=90)
#     pm.aimConstraint(TwistUpAimPos,TwistUpPos1Grp,wut=2,worldUpObject= TwistUpVecPos)
#     pm.parent(TwistUpFixGrp,RigSysGrp)

#     # TwistUpPos2 �����
#     if side == 'Left':
#         TwistUpPos1=pm.createNode('transform',n='%s%s%sTwistUpPos'%subob[0])
#     else:
#         IKFKCtrl.UpTwistFix>>TwistUpPos1.rotateX




# def Organize():
#     RootCtrl=RootCtrlMake()
#     CtrlList=['%s%sIKConstCtrl','side_subob1_FKCtrl','%s%sUpArcCtrl','%s%sMidArcCtrl','%s%sDnArcCtrl','%s%sIKFKCtrl','%s%sPoleVectorCtrl']
#     for x in CtrlList:
#         if pm.objExists(x):
#             grp=pm.PyNode(x+'Grp')
#             pm.parent(grp,RootCtrl)
#         else:
#             pass
#     SysList=[DrvJnt[0].replace('DrvJnt','ArcPos'),DrvJnt[1].replace('DrvJnt','ArcPos'),DrvJnt[2].replace('DrvJnt','ArcPos'),'%s%sUpArcHandle','%s%sDnArcHandle','%s%sUpArcCurve','%s%sDnArcCurve']
#     for x in SysList:
#         if pm.objExists(x):
#             sys=pm.PyNode(x)
#             pm.parent(sys,EtcGrp)
#         else:
#             pass

#     gn.Mcon(RootCtrl,IKJnt[0],t=1, r=1, sh=1, mo=1, pvtCalc=1)
#     pm.parent(AllCrv,UpCurve,DnCurve,EtcGrp)

    
# def NameChange():
#     SideSel=pm.ls('*side_*')
#     ObSel=pm.ls('*ob_*')
#     subob1Sel=pm.ls('*subob1_*')
#     subob2Sel=pm.ls('*subob2_*')
#     subob3Sel=pm.ls('*subob3_*')
#     for x in SideSel:
#         pm.rename(x,x.replace('side_',side))          
#     for y in ObSel:
#         pm.rename(y,y.replace('ob_',ob))
#     for i,j,k in zip(subob1Sel,subob2Sel,subob3Sel):
#         pm.rename(i,i.replace('subob1_',subob[0]))
#         pm.rename(j,j.replace('subob2_',subob[1]))
#         pm.rename(k,k.replace('subob3_',subob[2]))
#     # �����彦�� Ÿ�� ���̹� ����
#     BS = pm.ls('%s%sArcBS' % (side, ob), type='blendShape')[0]
#     pm.aliasAttr('%s%sArcCrvGrp' % (side, ob), BS.w[0])
#     # ����Ʈ���� ��� ��Ʈ����Ʈ ���̹� ����
#     CNSList = ['pointConstraint', 'parentConstraint', 'orientConstraint','aimConstraint']
#     for x in CNSList:
#         cns = pm.ls(type=x)
#         for i in cns:
#             find = i.attr('target[0].targetWeight')
#             Str_find = str(find)
#             F_attr = find.listConnections(d=0, s=1, p=1)[0]
#             Str_attr = str(F_attr).split('.')[-1]
#             if 'ob_' in Str_attr:
#                 pm.renameAttr(F_attr, Str_attr.replace('side_', side).replace('ob_', ob))
#             else:
#                 pass
def ArmLegRig(JntSel):
    IKJnt=DuplicateJnt(JntSel,'IK')
    IKCtrls=IKRig(IKJnt)
    FKJnt=DuplicateJnt(JntSel,'FK')
    FKCtrls=FKRig(FKJnt)
    IKFKCtrl=IKFKCtrlMake(JntSel)
    
    IKFKVisConnect(IKCtrls[1].getParent(),FKCtrls[0][0].getParent(),IKFKCtrl)
    DrvJnt=DuplicateJnt(JntSel,'Drv')
    sel=[FKJnt[0],IKJnt[0],DrvJnt[0],IKFKCtrl]
    kb.IKFKBlend(sel)
    #IKFKVisSet()
    ArcJnts=ArcRig(DrvJnt)

    UpArcJnt,DnArcJnt=ArcJnts[0],ArcJnts[1]
    f_UpArcJnt=pm.PyNode(UpArcJnt[0])
    e_UpArcJnt=pm.PyNode(UpArcJnt[-1])
    UpArcJntSel=[f_UpArcJnt,e_UpArcJnt]

    UpStSq=Spline(UpArcJntSel)
    
    
    f_DnArcJnt=pm.PyNode(DnArcJnt[0])
    e_DnArcJnt=pm.PyNode(DnArcJnt[-1])
    DnArcJntSel=[f_DnArcJnt,e_DnArcJnt]
    DnStSq=Spline(DnArcJntSel)
    
    StretchPractice(IKJnt)

    
    
    
    
    # ArcRig()
    # BindRig()
    # StretchPractice()
    # Organize()
    # NameChange()
   

    ###### ������ �����, Ʈ����Ʈ �ֱ� , �ٸ� �ȵȴ�.... , ����Ʈ ������Ʈ ���� ���߱�!
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
JntSel=pm.ls(sl=1)
side=sideName(JntSel)
ob=obName(JntSel) 
colors=Color(side)
MainColor,SubColor,fingerMainColor=colors[0],colors[1],colors[2]

LeftArmRig=ArmLegRig(JntSel)
