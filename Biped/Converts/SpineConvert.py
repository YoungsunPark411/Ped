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
import Spine_IKStretchSet as st
import NameExtraction as ne

from imp import reload
# reload(gn)
# reload(st)
# reload(ne)
Scale=gn.scaleGet()

# IK조인트만들기
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

# IK 컨트롤 만들기
def CtrlMake():

    Scale = gn.scaleGet()

    HipCtrl = gn.ControlMaker('HipCtrl', 'hip', 14, exGrp=0, size=Scale*0.3)
    gn.rotate_components(180, 0, 0, HipCtrl[0])
    SpineFK1Ctrl = gn.ControlMaker('SpineFK1Ctrl', 'diamond', 17, exGrp=0, size=Scale*1.2)
    SpineMidCtrl = gn.ControlMaker('SpineMidCtrl', 'hexagon', 23, exGrp=0, size=Scale*1.2)
    pm.select(SpineMidCtrl[0])
    pm.addAttr(ln="SpineBlend", at='double', min=0, max=1, dv=0, k=1)
    SpineFK2Ctrl = gn.ControlMaker('SpineFK2Ctrl', 'diamond', 17, exGrp=0, size=Scale*1.2)
    BodyIKCtrl = gn.ControlMaker('BodyIKCtrl', 'hip', 14, exGrp=0, size=Scale*0.3)
    pm.select(BodyIKCtrl[0])
    pm.addAttr(ln="Stretch", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="Squash", at='double', min=0, max=10, dv=0, k=1)
    pm.addAttr(ln="Slide", at='double', min=-10, max=10, dv=0, k=1)
      
    return HipCtrl[0],SpineFK1Ctrl[0],SpineMidCtrl[0],SpineFK2Ctrl[0],BodyIKCtrl[0]

def space_(name_, parent_=None):
    space_ = pm.createNode('transform',
                        n='{}Grp'.format(name_),
                        p=parent_)
    return space_

        
def SpineRig():
    ObjName = 'Spine'
    side,ob,parts,colors=ne.NameExtraction(ObjName)

    MainColor, SubColor, fingerMainColor = int(colors[0]), int(colors[1]), int(colors[2])
    #그룹만들기
    RigGrp=space_(ob+'Rig')
    SysGrp=space_(ob+'Sys',RigGrp)
    CtrlGrp=space_(ob+'Ctrl',RigGrp)
    
    BindJnt = []
    for x in parts:
        jnt_=pm.PyNode('{0}{1}Jnt'.format(str(side),x))
        BindJnt.append(jnt_)

    #IK조인트 만들기 
    IKJnt = DuplicateJnt(BindJnt, 'IK')
    IKJntGrp=pm.createNode('transform',n=ob+'IKJntGrp')
    gn.PosCopy(IKJnt[0],IKJntGrp)
    pm.parent(IKJnt[0],IKJntGrp)
    
    #스플라인 셋팅
    Crv_=gn.CrvFromJnt(IKJnt)
    Crv=Crv_.rename(ObjName+'IKCrv')
    pm.rebuildCurve(Crv, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=len(IKJnt)-1, d=3, tol=0.01)

    nodeDict_=st.IKStretch(IKJnt,Crv)
    
    #컨트롤 만들기, 배치     
    HipCtrl,SpineFK1Ctrl,SpineMidCtrl,SpineFK2Ctrl,BodyIKCtrl=CtrlMake()
    pm.parent(HipCtrl,SpineFK1Ctrl,SpineMidCtrl,SpineFK2Ctrl,BodyIKCtrl,CtrlGrp)
    ctrls=[HipCtrl,SpineFK1Ctrl,SpineMidCtrl,SpineFK2Ctrl,BodyIKCtrl]
    for x,i in zip(ctrls,IKJnt):
        pm.delete(pm.pointConstraint(i,x))
    pm.parent(SpineFK2Ctrl,SpineMidCtrl,SpineFK1Ctrl)
    pm.parent(BodyIKCtrl,SpineFK2Ctrl)
    for x in ctrls:
        gn.addNPO(x,'Grp')
   
        
    #스플라인커브 조인트 만들기
    spCtrls=[HipCtrl,SpineMidCtrl,BodyIKCtrl]
    spJnt = []
    [spJnt.append(pm.createNode('joint', n='%sSpJnt' % (ctrl.replace('Ctrl', '')))) for ctrl in spCtrls]    
    for x,i in zip(spCtrls, spJnt):
        pm.delete(pm.parentConstraint(x,i))
        pm.parent(i,x)
        gn.addNPO(i,'Grp')
  
    #IK스플라인
    ikHandle = pm.ikHandle(sj=IKJnt[0], ee=IKJnt[-1], n='%s%sIKHandle'%(side,ob), sol='ikSplineSolver', ccv=0,c=Crv)
    pm.parent(Crv,w=1)
    handle=ikHandle[0]
    handle.dTwistControlEnable.set(1)
    handle.dWorldUpType.set(4)

    #스플라인 업벡터 
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
    
    #스플라인 커브와 조인트 잡기 
    pm.skinCluster(spJnt, Crv,tsb=True)
    
    #스플라인 조인트와 바이드 조인트 cons,조인트 스쿼시 연결
    for x,i in zip(IKJnt,BindJnt ):
        gn.Mcon(x,i,t=1, r=1,  mo=1, pvtCalc=1)

    #스플라인 채널 연결
    BodyIKCtrl.Stretch >> IKJnt[0].Stretch
    BodyIKCtrl.Squash >> IKJnt[0].Squash
    
    #스쿼시 스케일 연결
    for x,i,j in zip(ctrls,IKJnt,BindJnt ):
        pm.addAttr(x,ln="ScaleYZ", at='double', dv=0, k=1)
        pm.setAttr(x.sx,lock=1, keyable=0, channelBox=0)
        pm.setAttr(x.sy,lock=1, keyable=0, channelBox=0)
        pm.setAttr(x.sz,lock=1, keyable=0, channelBox=0)
        x.ScaleYZ.set(1)
        name_=j.replace('Jnt','')
        ctrlScale=pm.createNode('transform',n='{}CtrlScale'.format(name_),p=i)
        squashScale=pm.createNode('transform',n='{}SquashScale'.format(name_),p=ctrlScale)
        gn.PosCopy(i,ctrlScale)
        x.ScaleYZ>>ctrlScale.sy
        x.ScaleYZ>>ctrlScale.sz
        i.SquashScaleY>>squashScale.sy
        i.SquashScaleZ>>squashScale.sz
        pm.scaleConstraint(squashScale,j,mo=1)
            
    
    #슬라이드 연결 
    pc_=nodeDict_['pc'][1:-1]
    pm.setDrivenKeyframe(pc_[0].parameter, cd=BodyIKCtrl.Slide, dv=-10, v=0.125)
    pm.setDrivenKeyframe(pc_[0].parameter, cd=BodyIKCtrl.Slide, dv=0.0, v=0.25)
    pm.setDrivenKeyframe(pc_[0].parameter, cd=BodyIKCtrl.Slide, dv=10, v=0.6)
    
    pm.setDrivenKeyframe(pc_[1].parameter, cd=BodyIKCtrl.Slide, dv=-10, v=0.25)
    pm.setDrivenKeyframe(pc_[1].parameter, cd=BodyIKCtrl.Slide, dv=0.0, v=0.5)
    pm.setDrivenKeyframe(pc_[1].parameter, cd=BodyIKCtrl.Slide, dv=10, v=0.7)
    
    pm.setDrivenKeyframe(pc_[2].parameter, cd=BodyIKCtrl.Slide, dv=-10, v=0.375)
    pm.setDrivenKeyframe(pc_[2].parameter, cd=BodyIKCtrl.Slide, dv=0.0, v=0.75)
    pm.setDrivenKeyframe(pc_[2].parameter, cd=BodyIKCtrl.Slide, dv=10, v=0.8)
    
    #Spine 블랜드
    pbGrp=gn.addNPO(SpineMidCtrl,'PBGrp')
    MidPbGrp=pbGrp[0]
    cns=pm.parentConstraint(BodyIKCtrl,HipCtrl,MidPbGrp,mo=1)
    pb=gn.PairBlend(MidPbGrp,t=1,r=1)
    SpineMidCtrl.SpineBlend>>MidPbGrp.pbw
    
    #정리 
    pm.parent(Crv.replace('Crv','ChkCrv'),handle,SysGrp)
    pm.parent(IKJntGrp,SysGrp)
    pm.parent(CtrlGrp,RigGrp)
    if pm.objExists('RigSysGrp'):
        pm.parent(Crv,'RigSysGrp')
    else:
        pass

    if pm.objExists('RootCtrl'):
        pm.parent(RigGrp,'RootCtrl')
        ChestConstGrp=pm.createNode('transform',n='ChestConstGrp',p='RootCtrl')
        gn.PosCopy(IKJnt[-1],ChestConstGrp)
        gn.Mcon(IKJnt[-1],ChestConstGrp,mo=1,t=1)
        gn.Mcon(spJnt[-1],ChestConstGrp,mo=1,r=1)
        
    else:
        pass
    
    



#SpineRig()









