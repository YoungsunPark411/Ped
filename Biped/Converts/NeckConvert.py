# -*- coding: cp949 -*-
import pymel.core as pm
import sys, os

#�����н� 
if os.path.isdir('D:\Ped\Biped\Converts'):
   script_path = 'D:\Ped\Biped\Converts'
else:
   script_path = 'Z:\mvtools\scripts\Biped\Converts'
if script_path in sys.path:
    pass
else:
    sys.path.insert(0, script_path)

import General as gn
import Spine_IKStretchSet as st
import NameExtraction as ne

from imp import reload
# reload(gn)
# reload(st)
Scale=gn.scaleGet()

# IK����Ʈ�����
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
        #pm.makeIdentity(rstJnt[0], a=1, t=1, r=1, s=1, n=0, pn=1)
        pm.setAttr("%s.jointOrientX" % rstJnt[-1], 0)
        pm.setAttr("%s.jointOrientY" % rstJnt[-1], 0)
        pm.setAttr("%s.jointOrientZ" % rstJnt[-1], 0)
    return rstJnt

# IK ��Ʈ�� �����
def CtrlMake():

    Scale = gn.scaleGet()

    HeadCtrl = gn.ControlMaker('HeadCtrl', 'circle', 21, exGrp=0, size=Scale)
    pm.addAttr(ln="Stretch", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="Squash", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="Follow", at='enum', en='Neck:Body:Root:Fly', k=1)
    pm.addAttr(ln="BendCtrlVis", at='bool', k=1)
    pm.setAttr(HeadCtrl[0].BendCtrlVis, keyable=0, channelBox=1)
    pm.addAttr(ln="HairCtrlVis", at='bool', k=1)
    pm.setAttr(HeadCtrl[0].HairCtrlVis, keyable=0, channelBox=1)
    gn.rotate_components(90, 0, 0, HeadCtrl[0])
    
    NeckMidCtrl = gn.ControlMaker('NeckMidCtrl', 'neck', 17, exGrp=0, size=Scale*0.1)
    NeckCtrl = gn.ControlMaker('NeckCtrl', 'neck', 17, exGrp=0, size=Scale*0.2)
      
    return NeckCtrl[0],NeckMidCtrl[0],HeadCtrl[0]

def space_(name_, parent_=None):
    space_ = pm.createNode('transform',
                        n='{}Grp'.format(name_),
                        p=parent_)
    return space_

        
def NeckRig():
    ObjName = 'Neck'
    side,ob,parts,colors=ne.NameExtraction(ObjName)

    #�׷츸���
    RigGrp=space_(ob+'Rig')
    SysGrp=space_(ob+'Sys',RigGrp)
    CtrlGrp=space_(ob+'Ctrl',RigGrp)
    
    BindJnt = []
    for x in parts:
        jnt_=pm.PyNode('{0}{1}Jnt'.format(str(side),x))
        BindJnt.append(jnt_)

    #IK����Ʈ ����� 
    IKJnt = DuplicateJnt(BindJnt, 'IK')
    IKJntGrp=pm.createNode('transform',n=ob+'IKJntGrp')
    gn.PosCopy(IKJnt[0],IKJntGrp)
    pm.parent(IKJnt[0],IKJntGrp)
    
    #���ö��� ����
    Crv_=gn.CrvFromJnt(IKJnt)
    Crv=Crv_.rename(ObjName+'IKCrv')
    pm.rebuildCurve(Crv, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=len(IKJnt)-1, d=3, tol=0.01)

    nodeDict_=st.IKStretch(IKJnt,Crv)
    
    #���ö���Ŀ�� ����Ʈ �����
    spJnt = gn.JntMake(Crv,3, 'Sp')    

    
    #��Ʈ�� �����, ��ġ     
    NeckCtrl,NeckMidCtrl,HeadCtrl=CtrlMake()
    pm.parent(NeckCtrl,NeckMidCtrl,HeadCtrl,CtrlGrp)
    ctrls=[NeckCtrl,NeckMidCtrl,HeadCtrl]
    pm.parent(NeckMidCtrl,NeckCtrl)
    pm.parent(HeadCtrl,NeckMidCtrl)
    for x,i in zip(ctrls,spJnt):
        pm.delete(pm.pointConstraint(i,x))
        pm.parent(i,x)
        gn.addNPO(x,'Grp')

  
    #IK���ö���
    ikHandle = pm.ikHandle(sj=IKJnt[0], ee=IKJnt[-1], n='%s%sIKHandle'%(side,ob), sol='ikSplineSolver', ccv=0,c=Crv)
    pm.parent(Crv,w=1)
    handle=ikHandle[0]
    handle.dTwistControlEnable.set(1)
    handle.dWorldUpType.set(4)

    #���ö��� ������ 
    uvCtrls=[ctrls[0],ctrls[-1]]
    uv = []
    [uv.append(pm.createNode('transform', n='%sSpUvecPos' % (ctrl.replace('Ctrl', '')))) for ctrl in uvCtrls]    
    StartEndJnt=[BindJnt[0],BindJnt[-1]]
    for x,i,j in zip(uvCtrls, uv, StartEndJnt):
        pm.delete(pm.parentConstraint(j,i))        
        pm.parent(i,x)     
        gn.addNPO(i,'Grp')

    uv[0].worldMatrix[0]>>handle.dWorldUpMatrix
    uv[1].worldMatrix[0]>>handle.dWorldUpMatrixEnd
    
    #���ö��� Ŀ��� ����Ʈ ��� 
    pm.skinCluster(spJnt, Crv,tsb=True)
    
    #���ö��� ����Ʈ�� ���̵� ����Ʈ cons,����Ʈ ������ ����
    for x,i in zip(IKJnt[:-1],BindJnt[:-1] ):
        gn.Mcon(x,i,t=1, r=1,  mo=1, pvtCalc=1)
    gn.Mcon(IKJnt[-1],BindJnt[-1],t=1, mo=1, pvtCalc=1)
    gn.Mcon(HeadCtrl,BindJnt[-1],r=1, mo=1, pvtCalc=1)

    #���ö��� ä�� ����
    HeadCtrl.Stretch >> IKJnt[0].Stretch
    HeadCtrl.Squash >> IKJnt[0].Squash
    

    # ������ ������ ����
    for x in ctrls[0:-1]:
        pm.addAttr(x,ln="ScaleYZ", at='double', dv=0, k=1)
        pm.setAttr(x.sx,lock=1, keyable=0, channelBox=0)
        pm.setAttr(x.sy,lock=1, keyable=0, channelBox=0)
        pm.setAttr(x.sz,lock=1, keyable=0, channelBox=0)
        x.ScaleYZ.set(1)
    ctrlScales=[]    
    for i,j in zip(IKJnt,BindJnt ):
        if i == IKJnt[-1]:
            pass
        else:
            name_=j.replace('Jnt','')
            ctrlScale=pm.createNode('transform',n='{}CtrlScale'.format(name_),p=i)
            ctrlScales.append(ctrlScale)
            squashScale=pm.createNode('transform',n='{}SquashScale'.format(name_),p=ctrlScale)
            gn.PosCopy(i,ctrlScale)
            i.SquashScaleY>>squashScale.sy
            i.SquashScaleZ>>squashScale.sz
            pm.scaleConstraint(squashScale,j,mo=1)
        
    ctrls[0].ScaleYZ>>ctrlScales[0].sy
    ctrls[0].ScaleYZ>>ctrlScales[0].sz
    for y in ctrlScales[1:-1]:
        ctrls[1].ScaleYZ>>y.sy
        ctrls[1].ScaleYZ>>y.sz
    pm.scaleConstraint(ctrls[-1],BindJnt[-1],mo=1)
    
    
    #���� 
    pm.parent(Crv.replace('Crv','ChkCrv'),handle,SysGrp)
    pm.parent(IKJntGrp,SysGrp)
    pm.parent(CtrlGrp,RigGrp)
    if pm.objExists('RigSysGrp'):
        pm.parent(Crv,'RigSysGrp')
    else:
        pass

    if pm.objExists('ChestConstGrp'):
        pm.parent(RigGrp,'ChestConstGrp')
    else:
        pass

#NeckRig()
