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
# reload(gn)
# reload(kb)
# reload(st)

def VPsetDriven(sel1,sel2):

   driver = sel1 + '.outputX'
   driven = sel2 + '.rotateZ'

   pm.setDrivenKeyframe(driven, cd=driver, dv=-1, v=-90)
   pm.setDrivenKeyframe(driven, cd=driver, dv=0.0, v=0.0)
   pm.setDrivenKeyframe(driven, cd=driver, dv=1, v=90)

def TwistPosTop(DrvJnt,UpArcJnt):

   fixGrp=pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt','TwistFixGrp'))
   aimGrp=pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt','TwistAimGrp'))
   tgPos=pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt','TwistFixTgPos'))
   upVec=pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt','TwistFixUpvec'))
   pos=pm.shadingNode('transform', au=1, n=DrvJnt[0].replace('DrvJnt','TwistFixPos'))
   pm.parent(tgPos,upVec,aimGrp,fixGrp)
   pm.parent(pos,aimGrp)

   pm.parent(fixGrp,UpArcJnt[0].getParent())

   gn.PosCopy(UpArcJnt[0],fixGrp)
   gn.PosCopy(UpArcJnt[-1], tgPos)
   gn.PosCopy(UpArcJnt[0], upVec)
   pm.pointConstraint(DrvJnt[1],tgPos,mo=0)

   vp=pm.shadingNode('vectorProduct', au=1, n=DrvJnt[0].replace('DrvJnt','TwistVP'))
   tgPos.t>>vp.input1
   vp.operation.set(1)
   vp.input2Y.set(1)
   vp.normalizeOutput.set(1)

   VPsetDriven(vp, upVec)
   pm.aimConstraint(tgPos, aimGrp, mo=0, wut=2, wuo=upVec, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                    worldUpVector=(0, 1, 0))
   gn.Mcon(DrvJnt[0], fixGrp, t=1, mo=1, pvtCalc=1)

   return pos
#TwistPosTop(DrvJnt,UpArcJnt)

def TwistPosTMid(DrvJnt, UpArcJnt,DnArcJnt):
   fixGrp = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixGrp'))
   aimGrp = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistAimGrp'))
   tgPos = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixTgPos'))
   
   pos = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixPos'))
   posUp = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixPosUp'))
   posDn = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'TwistFixPosDn'))
   AssiA=pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'AssiAPos'))
   AssiB = pm.shadingNode('transform', au=1, n=DrvJnt[1].replace('DrvJnt', 'AssiBPos'))
   pm.parent(AssiB,tgPos, aimGrp, fixGrp)
   pm.parent(posUp,posDn,pos)
   pm.parent(pos, aimGrp)
   pm.parent(AssiA, DrvJnt[1])
   pm.parent(fixGrp, DrvJnt[0])
   pm.delete(pm.parentConstraint(UpArcJnt[-1],DnArcJnt[0], fixGrp,mo=0))
   tgPos.tx.set(1)

   gn.PosCopy(tgPos, AssiA)
   gn.PosCopy(tgPos, AssiB)

   pm.pointConstraint(AssiA,AssiB, tgPos, mo=1)

   pm.aimConstraint(tgPos, aimGrp, mo=0, wut=2, wuo=AssiA, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                    worldUpVector=(0, 1, 0))

   gn.PosCopy(UpArcJnt[-1], posUp)
   gn.PosCopy(DnArcJnt[0], posDn)

   gn.addNPO(posUp, 'Grp')
   gn.addNPO(posDn, 'Grp')

   return [posUp,posDn]
#TwistPosTMid(DrvJnt, UpArcJnt,DnArcJnt)

def TwistPosTDn(DrvJnt, DnArcJnt):
   fixGrp = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixGrp'))
   aimGrp = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistAimGrp'))
   tgPos = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixTgPos'))
   upVec = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixUpvec'))
   pos = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixPos'))
   posSub=pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'TwistFixSubPos'))
   AssiA=pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'AssiAPos'))
   AssiB = pm.shadingNode('transform', au=1, n=DrvJnt[-1].replace('DrvJnt', 'AssiBPos'))
   pm.parent(AssiB,tgPos, upVec, aimGrp, fixGrp)
   pm.parent(pos,posSub, aimGrp)
   pm.parent(AssiA, DrvJnt[2])
   pm.parent(fixGrp, DrvJnt[1])

   pm.delete(pm.parentConstraint(DnArcJnt[-1], fixGrp,mo=0))
   tgPos.tx.set(1)

   gn.PosCopy(tgPos, AssiA)
   gn.PosCopy(tgPos, AssiB)

   pm.pointConstraint(AssiA,AssiB, tgPos, mo=1)

   pm.aimConstraint(tgPos, posSub, mo=0, wut=2, wuo=AssiA, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                    worldUpVector=(0, 1, 0))

   Grp_=gn.addNPO(pos, 'Grp')
   posGrp=Grp_[0]
   pm.orientConstraint(posSub,posGrp,weight=1,mo=1)
   pm.orientConstraint(aimGrp, posGrp, weight=0.5, mo=1)

   return pos

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
   pm.aimConstraint(tgPos, aimGrp, mo=0, wut=2, wuo=upVec, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                    worldUpVector=(0, 1, 0))
   pm.delete(pm.pointConstraint(DrvJnt[1],pos,mo=0))
   pm.delete(pm.orientConstraint(aimGrp,pos,mo=0))
   rxResult=pos.rx.get()
   pos.rx.set(rxResult+90)
   ryResult=pos.ry.get()
   pos.ry.set(rxResult+180)
   posGrp_=gn.addNPO(pos, 'Grp')
   FWpos.tz.set(-0.01)

   return [fixGrp,pos]

PVTwistAim(DrvJnt,IKCtrlPos)

sell=pm.ls(sl=1)
DrvJnt=sell[0:3]
UpArcJnt=sell[3:8]
DnArcJnt=sell[8:]
TwistPosTop(DrvJnt,UpArcJnt)
TwistPosTMid(DrvJnt, UpArcJnt,DnArcJnt)
TwistPosTDn(DrvJnt, DnArcJnt)
PVTwistAim(DrvJnt,IKCtrlPos)