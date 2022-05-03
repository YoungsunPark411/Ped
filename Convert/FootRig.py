import maya.cmds as mc
class IKFKRig:
    def __init__(self,jnt1,jnt2,jnt3):
        self.orgJnt=[jnt1,jnt2,jnt3]
        self.drvJnt=self.DuplicateJnt('Drv')
        self.ikJnt=self.DuplicateJnt('IK')
        self.fkJnt=self.DuplicateJnt('FK')

    def DuplicateJnt(self,type):
        orgJnt=self.orgJnt
        rstJnt=[]
        [ rstJnt.append( mc.createNode('joint',n='%s%sJnt'%(jnt.replace('Jnt',''),type) ) ) for jnt in orgJnt ]
        list(map( lambda a,b: gn.PosCopy(a,b), orgJnt, rstJnt ))
        for i in range(len(orgJnt)):
            if i==0: continue
            if '|' in rstJnt[i]:
                rstJnt[i]=rstJnt[i].replace('|','')
            mc.parent( rstJnt[i], rstJnt[i-1] )
            mc.select(rstJnt[i])
            selJnt=mc.ls(sl=1)
            mc.makeIdentity(selJnt[0],a=1, t=1,r=1,s=1,n=0,pn=1)

        #mc.joint(rstJnt[0],e=1  ,oj ='xyz' ,secondaryAxisOrient= 'zdown',ch =1 ,zso=1)
        mc.makeIdentity(rstJnt[0],a=1, t=1,r=1,s=1,n=0,pn=1)
        mc.setAttr ("%s.jointOrientX"%rstJnt[-1], 0);
        mc.setAttr ("%s.jointOrientY"%rstJnt[-1], 0);
        mc.setAttr ("%s.jointOrientZ"%rstJnt[-1], 0);
        mc.parent(rstJnt[1],w=1)
        mc.delete(rstJnt[0])
        return rstJnt



def FootIkJntRig(AnkleFixJnt):
    
    orgJnt = gn.jntList(AnkleFixJnt,3)
    
    #IKFKRigJnt=IKFKRig(orgJnt[0], orgJnt[1], orgJnt[2])
    #print(IKFKRigJnt)
    
    # mc.parent(orgJnt[1].replace('Jnt','IKJnt'),orgJnt[0].replace('Jnt','IKJnt'))
    # mc.parent(orgJnt[1].replace('Jnt','FKJnt'),orgJnt[0].replace('Jnt','FKJnt'))
    # mc.parent(orgJnt[1].replace('Jnt','DrvJnt'),orgJnt[0].replace('Jnt','DrvJnt'))
    
    IKHandle1 = mc.ikHandle(sj=orgJnt[0].replace('Jnt','IKJnt'), ee=orgJnt[1].replace('Jnt','IKJnt'), n='%sIKHandle' % orgJnt[0], sol='ikSCsolver',ccv=0)
    IKHandle2 = mc.ikHandle(sj=orgJnt[1].replace('Jnt','IKJnt'), ee=orgJnt[2].replace('Jnt','IKJnt'), n='%sIKHandle' % orgJnt[1], sol='ikSCsolver', ccv=0)

    ToeIKSubCtrlGrp=mc.createNode('transform',n='%sToeIKSubCtrlGrp'%side)
    mc.setAttr(ToeIKSubCtrlGrp+'.visibility',0)
    gn.PosCopy('%sLegIKCtrl'%side,ToeIKSubCtrlGrp)
    mc.parent(ToeIKSubCtrlGrp,'%sLegIKCtrl'%side)
    ToeIKSDKGrp=mc.createNode('transform',n='%sToeIKSDKGrp'%side)
    ToeIKSDKPivotGrp=mc.createNode('transform',n='%sToeIKSDKPivotGrp'%side)
    mc.parent(ToeIKSDKGrp,ToeIKSDKPivotGrp,ToeIKSubCtrlGrp)
    FList=['Back','In','Out','EndRoll','','Bend','Roll']
    ToeGrpList=[]
    for x in FList:
        a=mc.createNode('transform',n='%sToe%s'%(side,x))
        mc.parent(a,ToeIKSDKGrp)
        ToeGrpList.append(a)
        b = mc.createNode('transform', n='%sToe%sPivot' % (side, x))
        mc.parent(b,ToeIKSDKPivotGrp)
        mc.connectAttr(b+'.center',a+'.rotatePivot')
        mc.connectAttr(b + '.center', a + '.scalePivot')
        mc.setAttr (b+'.displayHandle',1)

    for i in range(len(ToeGrpList)):
        if i==0:continue
        mc.parent(ToeGrpList[i],ToeGrpList[i-1])
    mc.parent(ToeGrpList[-1],ToeGrpList[-3])
    
    mc.parent(IKHandle1[0],'%sToeBend'%side)
    mc.parent(IKHandle2[0],'%sToeRoll'%side)
    
    mc.poleVectorConstraint('%sLegPoleVectorCtrl'%side,IKHandle1[0])
    IKCtrl='%sLegIKCtrl'%side
    #FootRoll
    mc.setDrivenKeyframe('%sToeBack' % side+'.rotateX', cd=IKCtrl + '.FootRoll', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeBack'%side+'.rotateX',cd=IKCtrl+'.FootRoll',dv=-10, v=-50 )
    mc.setDrivenKeyframe('%sToeBend' % side + '.rotateX', cd=IKCtrl + '.FootRoll', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeBend' % side + '.rotateX', cd=IKCtrl + '.FootRoll', dv=10, v=50)

    #BallRoll
    mc.setDrivenKeyframe('%sToeRoll' % side + '.rotateX', cd=IKCtrl + '.BallRoll', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeRoll' % side + '.rotateX', cd=IKCtrl + '.BallRoll', dv=-10, v=-50)
    mc.setDrivenKeyframe('%sToeRoll' % side + '.rotateX', cd=IKCtrl + '.BallRoll', dv=10, v=50)
    #ToeRoll
    mc.setDrivenKeyframe('%sToeEndRoll' % side + '.rotateX', cd=IKCtrl + '.ToeRoll', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeEndRoll' % side + '.rotateX', cd=IKCtrl + '.ToeRoll', dv=-10, v=-50)
    mc.setDrivenKeyframe('%sToeEndRoll' % side + '.rotateX', cd=IKCtrl + '.ToeRoll', dv=10, v=50)

    #InOut
    mc.setDrivenKeyframe('%sToeOut' % side + '.rotateZ', cd=IKCtrl + '.InOut', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeOut' % side + '.rotateZ', cd=IKCtrl + '.InOut', dv=10, v=-50)
    mc.setDrivenKeyframe('%sToeIn' % side + '.rotateZ', cd=IKCtrl + '.InOut', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeIn' % side + '.rotateZ', cd=IKCtrl + '.InOut', dv=-10, v=50)
    #HeelPivot
    mc.setDrivenKeyframe('%sToeBack' % side + '.rotateY', cd=IKCtrl + '.HeelPivot', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeBack' % side + '.rotateY', cd=IKCtrl + '.HeelPivot', dv=-10, v=50)
    mc.setDrivenKeyframe('%sToeBack' % side + '.rotateY', cd=IKCtrl + '.HeelPivot', dv=10, v=-50)
    #BallPivot
    mc.setDrivenKeyframe('%sToe' % side + '.rotateY', cd=IKCtrl + '.BallPivot', dv=0, v=0)
    mc.setDrivenKeyframe('%sToe' % side + '.rotateY', cd=IKCtrl + '.BallPivot', dv=-10, v=50)
    mc.setDrivenKeyframe('%sToe' % side + '.rotateY', cd=IKCtrl + '.BallPivot', dv=10, v=-50)
    #ToePivot
    mc.setDrivenKeyframe('%sToeEndRoll' % side + '.rotateY', cd=IKCtrl + '.ToePivot', dv=0, v=0)
    mc.setDrivenKeyframe('%sToeEndRoll' % side + '.rotateY', cd=IKCtrl + '.ToePivot', dv=-10, v=50)
    mc.setDrivenKeyframe('%sToeEndRoll' % side + '.rotateY', cd=IKCtrl + '.ToePivot', dv=10, v=-50)
    
    #mc.connectAttr('%sLegIKCtrl'%side+'.ConstCtrlVis','%sLegIKConstCtrlShape.visibility'%side)
def OneParentCNS(Par_sel,Kid_sel):
    Kid=[]
    Par=[]
    pm.select(Par_sel)
    parAdd=pm.ls(sl=1)
    pm.select(Kid_sel)
    kidAdd=pm.ls(sl=1)
    for i in xrange(len(parAdd)):
        Par.append(parAdd[i])
        Kid.append(kidAdd[i])
        pnt=pm.parentConstraint(Par[i],Kid[i],mo=1).rename('%sParentConst'%Kid[i])      
def FKFootRig(AnkleFixJnt):
    orgJnt = gn.jntList(AnkleFixJnt,3)
    
    for x in orgJnt:
        print(x.replace('Jnt','DrvJnt'),x)
        OneParentCNS(x.replace('Jnt','DrvJnt'),x)
        #mc.parentConstraint(x.replace('Jnt','DrvJnt'),x,mo=1)
    #OneParentCNS(orgJnt[0].replace('Jnt','FKCtrl'),orgJnt[0].replace('Jnt','FKJnt'))
    OneParentCNS(orgJnt[1].replace('Jnt', 'FKCtrl'), orgJnt[1].replace('Jnt', 'FKJnt'))

    FKJnt = gn.jntList(AnkleFixJnt,3)

    IKJnt = gn.jntList(AnkleFixJnt,3)

    RigJnt = gn.jntList(AnkleFixJnt,2)
    for x,i in zip(FKJnt,IKJnt):
        BC= mc.createNode('pairBlend',n='%sPB'%x.replace('FkJnt',''))
        mc.connectAttr('%sLegIKFKCtrl'%side+'.IKFK',BC+'.weight')
        mc.connectAttr((x+'.rotate'), BC + '.inRotate2')
        mc.connectAttr((x+'.translate'), BC + '.inTranslate2')
        mc.connectAttr((i+'.rotate'), BC + '.inRotate1')
        mc.connectAttr((i+'.translate'), BC + '.inTranslate1')
        
        if 'Ball' in x:
            mc.connectAttr(BC+'.outRotate',RigJnt[0]+'.rotate')
            mc.connectAttr(BC + '.outTranslate', RigJnt[0] + '.translate')
            
        if 'ToeTip' in x:
            mc.connectAttr(BC+'.outRotate',RigJnt[1]+'.rotate')
            mc.connectAttr(BC + '.outTranslate', RigJnt[1] + '.translate')
side='Right'                
AnkleFixJnt=mc.ls(sl=1)[0]          
FootIkJntRig(AnkleFixJnt)
FKFootRig(AnkleFixJnt)
