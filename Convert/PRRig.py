# -*- coding: cp949 -*-
import pymel.core as pm
import sys
path = r'D:\MyScript\sealped'
if not path in sys.path:
    sys.path.insert(0, path)
from Material import General as gn


reload(gn)


def PosCopy_Parent(par, cha):
    gn.PosCopy(par, cha)
    pm.parent(cha, par)


def PRJntMake(sel_):

    nn = sel_.replace('Jnt', '')

    ns=['PR','PRS','PRW','PRN','PRE']
    PRJntList=[]
    for i in ns:
        Jnt_=pm.createNode('joint', n='%s%sJnt' % (nn,i))
        gn.PosCopy(sel_,Jnt_)
        PRJntList.append(Jnt_)

    jntgrp_=[]
    for y in PRJntList[1:]:
        pm.parent(y,PRJntList[0])
        grp_=gn.addNPO(objs=y, GrpName='Grp')
        jntgrp_.append(grp_[0])
        offgrp_=gn.addNPO(objs=y, GrpName='OffGrp')        
        offgrp_[0].tz.set(0.5)
    for x in PRJntList:
        pm.makeIdentity (x,apply=1,t =0,r= 1 ,s =0 ,n =0 ,pn= 1)

    jntgrp_[1].rx.set(90)
    jntgrp_[2].rx.set(180)
    jntgrp_[3].rx.set(-90)

    
    pm.parent(PRJntList[0], sel_)

    return PRJntList
#tt=pm.ls(sl=1)[0]
#PRJntMake(tt)


def PoseReaderRig(sel_):
    x = sel_
    nn = x.replace('Jnt', '')
    LocalPoseReaderLoc = pm.spaceLocator(n='%sLocalPoseReaderLoc' % nn)
    gn.PosCopy(x, LocalPoseReaderLoc)
    return LocalPoseReaderLoc


def localScaleModi(AxisLoc, size):
    list(map(lambda A: pm.setAttr(AxisLoc + '.localScale%s' % A, size), ['X', 'Y', 'Z']))


def Loc_to_LocalPoseReaderLoc(Loc, LocalPoseReaderLoc):
    DM = pm.createNode('decomposeMatrix', n=Loc + 'DM')
    Loc.worldMatrix >> DM.inputMatrix
    AB = pm.createNode('angleBetween', n=Loc + 'AB')
    DM.outputTranslate >> AB.vector2
    RV = pm.createNode('remapValue', n=Loc + 'RV')
    RV.inputMax.set(90)
    RV.outputMin.set(1)
    RV.outputMax.set(0)
    AB.angle >> RV.inputValue
    pm.addAttr(LocalPoseReaderLoc, ln='%sVec' % Loc.split('Axis')[0], at='double', dv=0, k=1)
    pm.connectAttr(RV + '.outValue', LocalPoseReaderLoc + '.%sVec' % Loc.split('Axis')[0])
    return AB


def findNodesTypeBelow(nodeType):
    pm.select(hi=1)
    sel = pm.ls(sl=1, type=nodeType)
    return sel


def AimVis_Dup(AimLoc):
    Grp1 = gn.addNPO(objs=AimLoc, GrpName='OffGrp')
    Grp2 = gn.addNPO(objs=AimLoc, GrpName='SpcGrp')
    dup_ = pm.duplicate(Grp1[0])
    pm.select(dup_)
    List = findNodesTypeBelow('transform')
    n_list = []
    for x in List:
        nn = pm.rename(x, x.replace('Aim', 'AimVisual').replace('1', ''))
        n_list.append(nn)
    n_list[1].translateX.set(1)
    pm.select(Grp1)
    o_list = findNodesTypeBelow('transform')
    n_list[0].rotate >> o_list[0].rotate
    n_list[1].translate >> o_list[1].translate
    n_list[2].translate >> o_list[2].translate

    return n_list


def PoseReaderSet(sel_):
    x = sel_
    nn = x.replace('Jnt', '')
    WGrp_ = pm.createNode('transform', n='%sWorldPoseReaderGrp' % nn)

    AimLoc = pm.spaceLocator(n='%sAimLoc' % nn)
    AimDM = pm.createNode('decomposeMatrix', n='%sAimDM' % nn)
    AimLoc.worldMatrix >> AimDM.inputMatrix

    av = AimVis_Dup(AimLoc)
    OffGrpPB_=pm.createNode('pairBlend',n=av[0]+'PB')
    OffGrpPB_.weight.set(0.5)
    x.rotate>>OffGrpPB_.inRotate2
    OffGrpPB_.outRotate>>av[0].rotate

    LocalPoseReaderLoc = PoseReaderRig(sel_)

    list = ['X', 'Y', 'Z', 'RvsX', 'RvsY', 'RvsZ']
    for i in list:
        AxisLoc = pm.spaceLocator(n='%s%sAxisLoc' % (nn, i))
        localScaleModi(AxisLoc, 0.1)

        pm.parent(AxisLoc, WGrp_)
        ax = i.replace('Rvs', '')

        if 'Rvs' in i:
            mv = -1
        else:
            mv = 1
        pm.setAttr(AxisLoc + '.translate%s' % (ax), mv)
        gn.addNPO(objs=AxisLoc, GrpName='Grp')

        AB_ = Loc_to_LocalPoseReaderLoc(AxisLoc, LocalPoseReaderLoc)
        AimDM.outputTranslate >> AB_.vector1

    # organize
    PoseReaderGrp = pm.createNode('transform', n='%sPoseReaderGrp' % nn)
    AimGrp = AimLoc.getParent().getParent()
    #pm.parent(sel_, av[0])
    pm.parent(AimGrp, WGrp_)
    pm.parent(WGrp_, LocalPoseReaderLoc, PoseReaderGrp)
    gn.PosCopy(LocalPoseReaderLoc,av[0])
    pm.parent(av[0],LocalPoseReaderLoc)
    gn.addNPO(objs=AxisLoc, GrpName='Grp')
    LocalPoseReaderLoc.rotate >> WGrp_.rotate

    if not pm.objExists('PoseReaderLocGrp'):
        prlgrp_=pm.createNode('transform',n='PoseReaderLocGrp')
        pm.parent(PoseReaderGrp,prlgrp_)
        if pm.objExists('RigSysGrp'):
            pm.parent(prlgrp_,'RigSysGrp')

    return LocalPoseReaderLoc

def addValueAttr(Ctrl_):

    pm.addAttr(Ctrl_,ln="Value", at='double3',  k=1)
    list(map(lambda A: pm.addAttr(Ctrl_,ln="Value%s"%A, at='double',  k=1,parent='Value'), ['X', 'Y', 'Z']))
    

def PRCtrlMake(sel_):
    Scale = gn.scaleGet()
    x = sel_
    if 'WJ' in str(x):
       
        Ctrl = gn.ControlMaker('%sCtrl' % x.replace('Jnt', ''), 'iceStick', 18, exGrp=0, size=Scale)
        gn.PosCopy(x, Ctrl[0])
        addValueAttr(Ctrl[0])
        gn.rotate_components(0, 0, 0, nodes=None)
    elif 'SJ' in str(x):
        Ctrl = gn.ControlMaker('%sCtrl' % x.replace('Jnt', ''), 'iceStick', 18, exGrp=0, size=Scale)
        gn.PosCopy(x, Ctrl[0])
        addValueAttr(Ctrl[0])     
        gn.rotate_components(0, 0, 0, nodes=None)
    elif 'EJ' in str(x):
        Ctrl = gn.ControlMaker('%sCtrl' % x.replace('Jnt', ''), 'iceStick', 18, exGrp=0, size=Scale)
        gn.PosCopy(x, Ctrl[0])
        addValueAttr(Ctrl[0])   
        gn.rotate_components(0, 0, 0, nodes=None)
    elif 'NJ' in str(x):
        Ctrl = gn.ControlMaker('%sCtrl' % x.replace('Jnt', ''), 'iceStick', 18, exGrp=0, size=Scale)
        gn.PosCopy(x, Ctrl[0])
        addValueAttr(Ctrl[0])
        gn.rotate_components(0, 0, 0, nodes=None)
        
    else:
        Ctrl = gn.ControlMaker('%sCtrl' % x.replace('Jnt', ''), 'clover', 14, exGrp=0, size=Scale)
        gn.PosCopy(x, Ctrl[0])
        pm.addAttr(Ctrl[0],ln="Pbw", at='double', min=0, max=1, dv=0, k=1)
        gn.rotate_components(0, 0, 0, nodes=None)
    return Ctrl[0]

def ctrlOrganize(ctrlList):
    prctrlgrp_ = pm.createNode('transform', n='PRCtrlGrp')
    pm.parent(ctrlList[0],prctrlgrp_)

    if pm.objExists('RootSubCtrl'):
        pm.parent(prctrlgrp_,'RootSubCtrl')

    for i in ctrlList[1:]:
        pm.parent(i,ctrlList[0])

    for x in ctrlList:
        grp_=gn.addNPO(x,'Grp')

    return prctrlgrp_




def PRCtrlLocConnect(sel_):
    prJntList=PRJntMake(sel_)
    loc=PoseReaderSet(sel_)
    ctrlList=[]
    for i in prJntList:
        ctrl_=PRCtrlMake(i)
        ctrlList.append(ctrl_)

    #컨트롤 정리
    prctrlgrp_=ctrlOrganize(ctrlList)

    gn.Mcon(prJntList[0],ctrlList[0].getParent(),t=1, r=1, s=1, sh=1, mo=1, pvtCalc=1)


    #for i in range(len(ctrlList)):
    #    offGrp_=prJntList[i].getParent()

    for x,y in zip(ctrlList[1:],prJntList[1:]):
        locSR = pm.createNode('setRange', n=x.replace('Ctrl', '').replace('PR', '') + 'LocalPoseReaderLocSR')
        locSR.oldMaxX.set(1)
        locSR.oldMaxY.set(1)
        locSR.oldMaxZ.set(1)

        x.Value>>locSR.max

        if 'WLo' in str(locSR):
            list(map(lambda A: pm.connectAttr(loc + '.%sRvsYVec' % locSR.split('WLo')[0], '%s.value%s' % (locSR, A)), ['X', 'Y', 'Z']))

        elif 'NLo' in str(locSR):
            list(map(lambda A: pm.connectAttr(loc + '.%sRvsZVec' % locSR.split('NLo')[0], '%s.value%s' % (locSR, A)), ['X', 'Y', 'Z']))

        elif 'ELo' in str(locSR):
            list(map(lambda A: pm.connectAttr(loc + '.%sYVec' % locSR.split('ELo')[0], '%s.value%s' % (locSR, A)), ['X', 'Y', 'Z']))

        elif 'SLo' in str(locSR):
            list(map(lambda A: pm.connectAttr(loc + '.%sZVec' % locSR.split('SLo')[0], '%s.value%s' % (locSR, A)), ['X', 'Y', 'Z']))

        else:
            pass

        locSR.outValue>>y.t
        
        gn.Mcon(x,y.getParent(),t=1, r=1, s=1, sh=1, mo=1, pvtCalc=1)

    #PR컨트롤 PR조인트 연결

    prPB=pm.createNode('pairBlend',n=prJntList[0]+'PB')
    ctrlList[0].Pbw>>prPB.weight
    sel_.r>>prPB.inRotate2
    prPB.outRotate>>prJntList[0].r
    
    ctrlList[0].Pbw.set(0.5)
    
    gn.Mcon(sel_,loc,t=1, mo=1, pvtCalc=1)
    



selList = pm.ls(sl=1)
for sel_ in selList:
    PRCtrlLocConnect(sel_)

### 바인드 조인트 선택하고 스크립트 돌리시오. 선택한 조인트의 로테이트값이 다 0값인지 확인할 것 




