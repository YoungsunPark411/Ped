# -*- coding: utf-8 -*-

import sys
"""
import pymel.core as pm
import sys
from Material import General as gn
from Material import IKFKBlend as kb
from BasicJnt import SealBasicJnt as sb
from Material import Seal_IK as si
from Material import FKCtrlMake as fm


'''
'''
reload(gn)
reload(kb)
reload(sb)
reload(si)
reload(fm)

# print (sys.path)
# sys.path.remove(sys.path[0])
Scale = gn.scaleGet()


def JntIVScale_disconnect(JntList):
    JntList.reverse()
    for x in range(len(JntList)):
        if x == range(len(JntList))[-1]: continue
        JntList[x + 1].scale // JntList[x].inverseScale

def type_JntMake(orgJnt, type):
    guideCrv = gn.CrvFromJnt(orgJnt)

    type_Jnt = gn.JntMake(guideCrv, len(orgJnt), type)
    pm.delete(guideCrv)
    n_type_Jnt = []
    for x, y in zip(orgJnt, type_Jnt):
        nj = pm.rename(y, x.replace('Jnt', type + 'Jnt'))
        n_type_Jnt.append(nj)

    sb.JntAxesChange('xzy', 'ydown', n_type_Jnt)
    return n_type_Jnt


def switchMake(obj_, DrvJnt):
    if 'Left' in str(DrvJnt[-1]):

        MainColor = 13
    elif 'Right' in str(DrvJnt[-1]):

        MainColor = 6
    else:

        MainColor = 17

    switch = gn.ControlMaker(obj_ + 'IKFKCtrl', 'switch', MainColor, exGrp=0, size=Scale)
    return switch[0]


def switchSet(switch):
    at = ['translate', 'rotate', 'scale']
    at2 = ['X', 'Y', 'Z']
    for x in at:
        for y in at2:
            ct_ = switch + '.' + x + y
            pm.setAttr(ct_, lock=1, keyable=0, channelBox=0)
    # pm.setAttr(x + '.visibility', lock=1)
    pm.addAttr(switch, ln="IKFK", at='double', min=0, max=1, dv=0, k=1)
    pm.addAttr(switch, ln="AutoHideIKFK", at='enum', en='off:on', k=1)
    pm.setAttr(switch + ".AutoHideIKFK", keyable=0, channelBox=1)
    switch.AutoHideIKFK.set(1)


def IKFKVisConnect(name_, IKCtrlGrp, FKCtrlGrp, IKFKCtrl):
    switch = IKFKCtrl
    FKCtrlGrp_ = FKCtrlGrp
    IKCtrlGrp_ = IKCtrlGrp
    rev = pm.createNode('reverse', n='{0}RV'.format(name_))
    cd = pm.createNode('condition', n='{0}CD'.format(name_))
    cd.secondTerm.set(1)
    switch.IKFK >> cd.colorIfTrue.colorIfTrueR
    switch.IKFK >> rev.input.inputX
    switch.AutoHideIKFK >> cd.firstTerm
    rev.output.outputX >> cd.colorIfTrue.colorIfTrueG
    cd.outColor.outColorR >> FKCtrlGrp_.visibility
    cd.outColor.outColorG >> IKCtrlGrp_.visibility


def IKFK_JntRig_Make(orgJnt):
    IKJnt = type_JntMake(orgJnt, 'IK')
    FKJnt = type_JntMake(orgJnt, 'FK')
    DrvJnt = type_JntMake(orgJnt, 'Drv')

    # IKRig

    IKCtrl_ = si.Spline(IKJnt, BIjoint_count=None)

    # FKRig 

    txlist = []
    for x in orgJnt:
        rr = str(x)
        txlist.append(rr)
    txCombined = ''.join(txlist)
    obj = []
    objList = ['Spine', 'Neck', 'LeftArm', 'RightArm']
    for i in objList:
        if i in txCombined:
            obj.append(i)
        else:
            pass
    if len(obj) > 1:
        pm.error('부위별 조인트가 2개이상입니다. 조인트 다시 선택하세요!')
        obj_ = ''
    else:
        obj_ = obj[0]

    # 스위치 만들기 
    switch = switchMake(obj_, DrvJnt)

    if obj_ == 'Neck' or 'Spine':
        shape_ = 'RoundSquare'

    elif obj_ == 'LeftArm' or 'RightArm':
        shape_ = 'RoundSquare'
        pm.delete(pm.pointConstraint(DrvJnt[0], switch))

    else:
        shape_ = 'pin'

    switchSet(switch)

    FKCtrl_ = fm.FKCtrlMake(FKJnt, shape_, cns=1)[1]
    Jnt_sel = [FKJnt[0], IKJnt[0], DrvJnt[0], orgJnt[0], switch]
    kb.IKFKBlend(Jnt_sel)


    #그룹 정리
    JntGrp=pm.createNode('transform',n=obj_+'JntGrp')
    JntGrp.visibility.set(0)
    pm.parent(IKJnt[0],FKJnt[0],DrvJnt[0],JntGrp)
    CtrlGrp = pm.createNode('transform', n=obj_ + 'CtrlGrp')
    pm.parent(FKCtrl_, IKCtrl_[0],switch,CtrlGrp)
    gn.addNPO(switch,'Grp')
    SysGrp=pm.createNode('transform', n=obj_ + 'SysGrp')
    pm.parent(JntGrp,CtrlGrp,IKCtrl_[1],SysGrp)
    if pm.objExists('RootSubCtrl'):
        pm.parent(SysGrp,'RootSubCtrl')
    else:
        print('RootSubCtrl이 필요해요!')
        pass
    if pm.objExists('RigSysGrp'):
        pm.parent(obj_ +'IKSysGrp','RigSysGrp')
    else:
        print('RigSysGrp이 필요해요!')
        pass

    #바인드 조인트 연결하기 
    for x,y in zip(orgJnt,DrvJnt):
        gn.Mcon(y, x, r=1, t=1, s=1,sh=1,mo=1)

    #스위치 위치시키기

    gn.PosCopy(orgJnt[-1], switch.getParent())
    gn.Mcon(orgJnt[-1], switch.getParent(), r=1, t=1, sh=1, mo=0, pvtCalc=1)

    #IKFKVis 연결하기
    name_=obj_
    IKCtrlGrp=IKCtrl_[0]
    FKCtrlGrp=FKCtrl_
    IKFKVisConnect(name_,IKCtrlGrp, FKCtrlGrp, switch)

    #inverseScale 끊기
    JntIVScale_disconnect(orgJnt)
    JntIVScale_disconnect(IKJnt)
    JntIVScale_disconnect(FKJnt)
    JntIVScale_disconnect(DrvJnt)
 


# reload(si)


# 준비물: 전체 컨트롤러~RootSubCtrl, 바인드용 조인트
### 팔 싸이클 엄청 걸린다...!!!!/ 새창에서는 안 그러네...?

# 바인드용 팔 조인트 차례대로 선택 후 실행하세요
orgJnt = pm.ls(sl=1)
IKFK_JntRig_Make(orgJnt)

"""