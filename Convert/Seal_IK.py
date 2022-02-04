# # -*- coding: cp949 -*-
import sys
for i in sys.path:
    print(i)
from rig.
import pymel.core as pm
import sys
import General as gn
import Seal_IKStretchSet as st
import SealBasicJnt as sb
# #reload(gn)
# #reload(st)
# # 첫번째와 마지막 조인트 잡고 실행해주세요
#
# # 크기 정하기
# Scale = gn.scaleGet()
#
# def IKCtrlMake(biJnt):
#     Jnt_=biJnt
#     CtrlList=[]
#     for x in Jnt_:
#         # 색 정하기
#         if 'Left' in x:
#             MainColor = 13
#             SubColor = 20
#         elif 'Right' in x:
#             MainColor = 6
#             SubColor = 18
#         else:
#             MainColor = 21
#             SubColor = 17
#         name_=x.replace('Jnt','').replace('BI','')
#
#
#         if x == Jnt_[0]:
#             IKCtrl = gn.ControlMaker(name_+'IKCtrl', 'ThickSquare', MainColor, exGrp=0, size=Scale)
#
#             if 'Arm' in x:
#                 pm.select(IKCtrl[0])
#                 pm.addAttr(ln="Follow", at='enum', en='Clavicle:Root:Fly:World', k=1)
#
#             CtrlList.append(IKCtrl[0])
#         elif x == Jnt_[-1]:
#             IKCtrl = gn.ControlMaker(name_+'IKCtrl', 'ThickSquare', MainColor, exGrp=0, size=Scale)
#             pm.select(IKCtrl[0])
#             if 'Arm' in x:
#                 # seg vis 만들기
#                 pm.addAttr( ln="IKSegVis", at='bool', dv=0, k=1)
#                 pm.setAttr(IKCtrl[0]+'.IKSegVis', keyable=0, channelBox=1)
#                 pm.addAttr(ln="Follow", at='enum', en='Clavicle:Root:Fly:World', k=1)
#             else:
#                 pm.addAttr(ln="Follow", at='enum', en='RootSub:Root:Fly:World', k=1)
#             CtrlList.append(IKCtrl[0])
#         else:
#             IKCtrl = gn.ControlMaker(name_+'IKCtrl', 'RoundSquare', SubColor, exGrp=0, size=Scale)
#             pm.select(IKCtrl[0])
#             pm.addAttr(ln="Pbw", at='double', min=0, max=1, dv=0, k=1)
#             CtrlList.append(IKCtrl[0])
#         gn.PosCopy(x,IKCtrl[0])
#
#     return CtrlList
#
# def BIIKJntMake(crv_,_count):
#     biJnt=gn.spine_joint_make(crv_, crv_.replace('IKCrv',''), _count, 1, 'BI', ojVal='xzy', sawoVal='xdown')
#     sb.JntAxesChange('xzy', 'ydown', biJnt)
#     ctrl = IKCtrlMake(biJnt)
#
#     biJntList=[]
#     for x,y in zip(ctrl,biJnt):
#
#         gn.PosCopy(x,y)
#         pm.parent(y,x)
#         pm.setAttr(y+'.visibility',0)
#         new=pm.rename(y,x.replace('IKCtrl','BIJnt'))
#         biJntList.append(new)
#         gn.rotate_components(0, 0, 90, x)
#
#         #pm.setAttr(x.scaleX,lock=1)
#
#     return [biJntList,ctrl]
#
#
#
# def PBConnect(srcA,srcB,tg):
#     srcA_ = gn.Mcon(srcA, tg, r=1, t=1, sh=1, mo=1,pvtCalc=1)
#     find_ = tg.listConnections(d=0, s=1, p=1)[0].split('.')[0]
#     dm = pm.PyNode(find_)
#     gn.Mcon(srcB, tg, r=1, t=1,mo=1, sh=1, pvtCalc=1)
#
#     pb = gn.PairBlend(tg, r=1, t=1, sh=1,mo=1,pvtCalc=1)
#
#     tg.pbw.set(0.5)
#
#     dm.outputTranslateX >> pb.itx1
#     dm.outputTranslateY >> pb.ity1
#     dm.outputTranslateZ >> pb.itz1
#     dm.outputRotateX >> pb.irx1
#     dm.outputRotateY >> pb.iry1
#     dm.outputRotateZ >> pb.irz1
#
#
#     return pb
#
#
# def PBRig(ctrl):
#     wVale = 1.0 / (len(ctrl) - 1)
#     PBGrpList=[]
#     i = 0
#     for x in ctrl[1:-1]:
#         PBGrp_=gn.addNPO(x,'PBGrp')[0]
#         PBGrpList.append(PBGrp_)
#     if len(ctrl) == 5:
#         ValuList=[[0,-1,1],[0,2,0],[2,-1,-1]]
#         for x in ValuList:
#             vl=x
#             pb=PBConnect(ctrl[vl[0]],ctrl[vl[1]],PBGrpList[vl[2]])
#             ctrl_=PBGrpList[vl[2]].listRelatives(c=1)[0]
#             ctrl_.Pbw.set(0.5)
#             ctrl_.Pbw>>PBGrpList[vl[2]].pbw
#     else:
#         for y in PBGrpList:
#             pb=PBConnect(ctrl[0],ctrl[-1],y)
#             i = i + wVale
#             ctrl_=y.listRelatives(c=1)[0]
#             ctrl_.Pbw.set(i)
#             ctrl_.Pbw>>y.pbw
#     return PBGrpList
#
# def connectStretchSquash(ctrl,name_,Jnt_):
#
#     stMDL = pm.PyNode(name_.replace('1', '') + 'IKStretchMDL')
#     sqMDL = pm.PyNode(name_.replace('1', '') + 'IKSquashMDL')
#     for x,y in zip(Jnt_[1:],ctrl[1:]):
#         sAttr_ = x.attr('sy')
#         F_md=sAttr_.listConnections(d=0, s=1, t='multiplyDivide')[0]
#         F_md.oy//x.sy
#         F_md.oz//x.sz
#         '''
#         mm=pm.createNode('multMatrix',n=x.replace('Jnt','')+'MM')
#         dm=pm.createNode('decomposeMatrix',n=x.replace('Jnt','')+'DM')
#         y.worldMatrix>>mm.matrixIn[2]
#
#         '''
#         gn.Mcon(y,x,s=1)
#
#         sAttr_2 = x.attr('s')
#         F_dm = sAttr_2.listConnections(d=0, s=1, t='decomposeMatrix')[0]
#
#         F_dm.os//x.s
#         F_dm.outputShear//x.shear
#
#
#         #F_mm=x.listConnections(d=1, s=0, t='multMatrix')[0]
#         #x.parentInverseMatrix//F_mm.matrixIn[3]
#
#
#         F_dm.os>>F_md.input1
#         F_md.oy>>x.sy
#         F_md.oz>>x.sz
#
#
#
#     pm.addAttr(ctrl[-1],ln="Stretch", at='double',  min=0, max=10, dv=0, k=1)
#     pm.addAttr(ctrl[-1], ln="Squash", at='double',  min=0, max=10, dv=0, k=1)
#
#     ctrl[-1].Stretch>>stMDL.input1
#     ctrl[-1].Squash >> sqMDL.input1
#
#
#
#
# def ArmAimRig(ctrl):
#     pm.addAttr(ctrl[0],ln="Aim", at='double', min=0, max=10, dv=0, k=1)
#     grp_=ctrl[0].getParent()
#     makegrp_=gn.addNPO(grp_,'Change')
#     newgrp_=pm.rename(makegrp_[0],makegrp_[0].replace('Change','OffGrp').replace('1',''))
#     acon=pm.aimConstraint(ctrl[-1],grp_,mo=1,wut=2,wuo=ctrl[-1])
#     acon.constraintRotateX//grp_.rotateX
#     acon.constraintRotateY // grp_.rotateY
#     acon.constraintRotateZ // grp_.rotateZ
#     pb_=pm.createNode('pairBlend',n=ctrl[0]+'AimPB')
#     acon.constraintRotate>>pb_.inRotate2
#     pb_.outRotate>>grp_.rotate
#
#     AimML=pm.createNode('multDoubleLinear',n=ctrl[0]+'AimML')
#     AimML.input2.set(0.1)
#     ctrl[0].Aim.set(10)
#     ctrl[0].Aim>>AimML.input1
#     AimML.output>>pb_.weight
#
#
# def ArmTwistJnt(crv_):
#     dup=pm.duplicate(crv_)
#     TJnt_ = gn.spine_joint_make(dup[0], dup[0].replace('IKCrv', 'Twist').replace('1',''), 2, 1, '', ojVal='xzy', sawoVal='xdown')
#     sb.JntAxesChange('xzy', 'ydown', TJnt_)
#     pm.delete(dup)
#     return TJnt_
# def createLoc( sName):
#     nTran = pm.createNode("transform", n=sName, p=None)
#     pm.createNode("locator", n= (sName + "Shape"), p=nTran)
#     return nTran
#
# def ArmTwistRig(ctrl,crv_):
#     TJnt=ArmTwistJnt(crv_)
#     Thandle=pm.ikHandle(sj=TJnt[0], ee=TJnt[-1], n=TJnt[0].replace('Jnt','') + 'Handle', sol='ikSCsolver')
#     pm.parent(Thandle[0],ctrl[-1])
#     t1Pos=createLoc( TJnt[0].replace('Jnt','Pos'))
#
#     gn.PosCopy(ctrl[0],t1Pos)
#     pm.parent(t1Pos,TJnt[0])
#
#     t2Pos =createLoc( TJnt[-1].replace('Jnt','Pos'))
#     gn.PosCopy(ctrl[-1], t2Pos)
#     pm.parent(t2Pos, TJnt[-1])
#     PosGrp=[t1Pos,t2Pos]
#
#     if pm.objExists('RigSysGrp'):
#         pm.parent(TJnt[0],'RigSysGrp')
#
#
#     return PosGrp
#
#
# def Spline(sel,BIjoint_count):
#     crv_Jnt=st.IKStretch(sel)
#     crv_=crv_Jnt[0]
#     Jnt_=crv_Jnt[1]
#     name_ = sel[0].split('IKJnt')[0]
#     if BIjoint_count==None:
#         count_=len(Jnt_)
#     elif BIjoint_count>=1:
#         count_=BIjoint_count
#     JntnCtrl=BIIKJntMake( crv_, count_)
#
#     BIIKJnt_ = JntnCtrl[0]
#
#     pm.skinCluster(crv_, BIIKJnt_, sm=1, tsb=1, n='%sSkinCluster' % name_)
#     grp_=pm.createNode('transform',n=sel[0].replace('Jnt','').replace('1','')+'CtrlGrp')
#     ctrl=JntnCtrl[1]
#
#     pm.rebuildCurve (crv_,ch =1 ,rpo=1 ,rt =0 ,end =1 ,kr=0 ,kcp =0,kep=1 ,kt=0 ,s=4 ,d=3 ,tol=0.01)
#     SPIKHandle = pm.ikHandle(sj=Jnt_[0], ee=Jnt_[-1], n=name_+'Handle', sol='ikSplineSolver', ccv=0, c=crv_)
#     handle = SPIKHandle[0]
#     handle.visibility.set(0)
#     handle.dTwistControlEnable.set(1)
#     handle.dWorldUpType.set(4)
#
#     if BIjoint_count==None:
#         PBGrpList_=PBRig(ctrl)
#
#     else:
#         pass
#     SysGrp_=pm.PyNode(Jnt_[0].replace('Jnt','SysGrp').replace('1',''))
#
#     pm.parent(crv_,handle,SysGrp_)
#     connectStretchSquash(ctrl, name_,Jnt_)
#     pm.parent(ctrl[-1],PBGrpList_,ctrl[0],grp_)
#     for x in ctrl:
#         gn.addNPO(x,'Grp')
#         pm.setAttr(x.scaleX,lock=1)
#
#     if 'Arm' in str(Jnt_):
#         ArmAimRig(ctrl)
#         TPos=ArmTwistRig(ctrl, crv_)
#         TPos[0].worldMatrix[0] >> handle.dWorldUpMatrix
#         TPos[-1].worldMatrix[0] >> handle.dWorldUpMatrixEnd
#         for x in ctrl:
#             pm.select(x)
#             gn.rotate_components(0, 0, 90, nodes=None)
#         pm.select(ctrl[0])
#         pm.addAttr(ctrl[-1],ln="UpTwist", at='double', dv=0, k=1)
#         pm.addAttr(ctrl[-1],ln="DnTwist", at='double', dv=0, k=1)
#         ctrl[-1].UpTwist>>TPos[0].rotateX
#         ctrl[-1].DnTwist>>TPos[-1].rotateX
#
#         # seg vis 연결
#         for i in ctrl[1:-1]:
#             #print(i)
#             _grp = i.getParent()
#             ctrl[-1].IKSegVis >> _grp.visibility
#
#
#     else:
#         pass
#
#     return [grp_,SysGrp_]
#
#
# '''
# sel = pm.ls(sl=1,r=1,fl=1)
# tt=Spline(sel,BIjoint_count=None)
# '''
# ###워닝 뜬다....
#
