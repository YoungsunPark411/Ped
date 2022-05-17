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
import json
import FilePathImport
import IKFKBlend as kb
# reload(gn)


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


def DuplicateJnt(JntSel, type):
    orgJnt = JntSel
    rstJnt = []
    [rstJnt.append(pm.createNode('joint', n='%s%sJnt' % (side+part, type))) for part in parts]

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
    

def FootIkJntRig(IKJnt,IKCtrl):
    
    IKHandle1 = pm.ikHandle(sj=IKJnt[0], ee=IKJnt[1], n='%sIKHandle' % IKJnt[0].replace('IKJnt',''), sol='ikSCsolver',ccv=0)
    IKHandle2 = pm.ikHandle(sj=IKJnt[1], ee=IKJnt[2], n='%sIKHandle' % IKJnt[1].replace('IKJnt',''), sol='ikSCsolver', ccv=0)

    FootSysGrp=pm.createNode('transform',n='%sFootSysGrp'%side)
    pm.setAttr(FootSysGrp+'.visibility',0)
    gn.PosCopy(IKCtrl,FootSysGrp)
    pm.parent(FootSysGrp,IKCtrl)
    ToeMovePivGrp=pm.createNode('transform',n='%sToeMovePivGrp'%side)
    pm.parent(ToeMovePivGrp,FootSysGrp)
    NameList=['InRoll','OutRoll','HeelRollPiv','ToeRollPiv','BallPiv','FootRoll','BallRoll']
    ToeGrpList=[]
    MovePosList=[]
    for x in NameList:
        a=pm.createNode('transform',n='%s%sPos'%(side,x))
        pm.parent(a,FootSysGrp)
        ToeGrpList.append(a)
        b = pm.createNode('transform', n='%s%sMovePos' % (side, x))
        MovePosList.append(b)
        pm.parent(b,ToeMovePivGrp)
        pm.connectAttr(b+'.center',a+'.rotatePivot')
        pm.connectAttr(b + '.center', a + '.scalePivot')
        pm.setAttr (b+'.displayHandle',1)

    for i in range(len(ToeGrpList)):
        if i==0:continue
        pm.parent(ToeGrpList[i],ToeGrpList[i-1])
    pm.parent(ToeGrpList[-1],ToeGrpList[-3])
    
    pm.parent(IKHandle1[0],ToeGrpList[-2])
    pm.parent(IKHandle2[0],ToeGrpList[-1])
    
    #pm.poleVectorConstraint('%sLegPoleVectorCtrl'%side,IKHandle1[0])
    InRoll, OutRoll, HeelRollPiv, ToeRollPiv, BallPiv, FootRoll, BallRoll = ToeGrpList[0],ToeGrpList[1],ToeGrpList[2],ToeGrpList[3],ToeGrpList[4],ToeGrpList[5],ToeGrpList[6]
    InRollMV, OutRollMV, HeelRollPivMV, ToeRollPivMV, BallPivMV, FootRollMV, BallRollMV = MovePosList[0],MovePosList[1],MovePosList[2],MovePosList[3],MovePosList[4],MovePosList[5],MovePosList[6]

    #FootRoll
    pm.setDrivenKeyframe(HeelRollPiv+'.rotateX', cd=IKCtrl + '.FootRoll', dv=0, v=0)
    pm.setDrivenKeyframe(HeelRollPiv+'.rotateX',cd=IKCtrl+'.FootRoll',dv=-10, v=-50 )
    pm.setDrivenKeyframe(FootRoll+ '.rotateX', cd=IKCtrl + '.FootRoll', dv=0, v=0)
    pm.setDrivenKeyframe(FootRoll+ '.rotateX', cd=IKCtrl + '.FootRoll', dv=10, v=50)
   
    #BallRoll
    pm.setDrivenKeyframe(BallRoll + '.rotateX', cd=IKCtrl + '.BallRoll', dv=0, v=0)
    pm.setDrivenKeyframe(BallRoll + '.rotateX', cd=IKCtrl + '.BallRoll', dv=-10, v=-50)
    pm.setDrivenKeyframe(BallRoll+ '.rotateX', cd=IKCtrl + '.BallRoll', dv=10, v=50)
    
    #ToeRoll
    pm.setDrivenKeyframe(ToeRollPiv + '.rotateX', cd=IKCtrl + '.ToeRoll', dv=0, v=0)
    pm.setDrivenKeyframe(ToeRollPiv + '.rotateX', cd=IKCtrl + '.ToeRoll', dv=-10, v=-50)
    pm.setDrivenKeyframe(ToeRollPiv + '.rotateX', cd=IKCtrl + '.ToeRoll', dv=10, v=50)
    
    #InOut
    pm.setDrivenKeyframe(OutRoll + '.rotateZ', cd=IKCtrl + '.InOut', dv=0, v=0)
    pm.setDrivenKeyframe(OutRoll + '.rotateZ', cd=IKCtrl + '.InOut', dv=10, v=-50)
    pm.setDrivenKeyframe(InRoll + '.rotateZ', cd=IKCtrl + '.InOut', dv=0, v=0)
    pm.setDrivenKeyframe(InRoll + '.rotateZ', cd=IKCtrl + '.InOut', dv=-10, v=50)

    #HeelPivot
    pm.setDrivenKeyframe(HeelRollPiv + '.rotateY', cd=IKCtrl + '.HeelPivot', dv=0, v=0)
    pm.setDrivenKeyframe(HeelRollPiv + '.rotateY', cd=IKCtrl + '.HeelPivot', dv=-10, v=50)
    pm.setDrivenKeyframe(HeelRollPiv + '.rotateY', cd=IKCtrl + '.HeelPivot', dv=10, v=-50)
       
    #BallPivot
    pm.setDrivenKeyframe(BallPiv + '.rotateY', cd=IKCtrl + '.BallPivot', dv=0, v=0)
    pm.setDrivenKeyframe(BallPiv + '.rotateY', cd=IKCtrl + '.BallPivot', dv=-10, v=50)
    pm.setDrivenKeyframe(BallPiv + '.rotateY', cd=IKCtrl + '.BallPivot', dv=10, v=-50)
    
    #ToePivot
    pm.setDrivenKeyframe(ToeRollPiv + '.rotateY', cd=IKCtrl + '.ToePivot', dv=0, v=0)
    pm.setDrivenKeyframe(ToeRollPiv + '.rotateY', cd=IKCtrl + '.ToePivot', dv=-10, v=50)
    pm.setDrivenKeyframe(ToeRollPiv + '.rotateY', cd=IKCtrl + '.ToePivot', dv=10, v=-50)
    
    LegIKPos=pm.PyNode(side+'LegIKPos')
    gn.Mcon(FootRoll, LegIKPos, t=1, mo=1, pvtCalc=1)
    
    return InRollMV, OutRollMV, HeelRollPivMV, ToeRollPivMV, BallPivMV, FootRollMV, BallRollMV
    
    
 
def FKFootRig(JntSel,FKJnt,IKJnt,DrvJnt):

    for x,i in zip(FKJnt,IKJnt):
        BC= pm.createNode('pairBlend',n='%sPB'%x.replace('FkJnt',''))
        pm.connectAttr('%sLegIKFKCtrl'%side+'.IKFK',BC+'.weight')
        pm.connectAttr((x+'.rotate'), BC + '.inRotate2')
        pm.connectAttr((x+'.translate'), BC + '.inTranslate2')
        pm.connectAttr((i+'.rotate'), BC + '.inRotate1')
        pm.connectAttr((i+'.translate'), BC + '.inTranslate1')
        
        if 'Ball' in x:
            pm.connectAttr(BC+'.outRotate',DrvJnt[0]+'.rotate')
            pm.connectAttr(BC + '.outTranslate', DrvJnt[0] + '.translate')
            
        if 'ToeTip' in x:
            pm.connectAttr(BC+'.outRotate',DrvJnt[1]+'.rotate')
            pm.connectAttr(BC + '.outTranslate', DrvJnt[1] + '.translate')


def FootConvert():
    #global Scale
    Scale=gn.scaleGet()
    ObjName = ['LeftAnkle','RightAnkle']
    for i in ObjName:
        global side,ob,parts,colors,MainColor, SubColor, fingerMainColor
        side,ob,parts,colors=NameExtraction(i)
        MainColor, SubColor, fingerMainColor = int(colors[0]), int(colors[1]), int(colors[2])

        JntSel = []
        for x in parts:
            jnt_=pm.PyNode('%s%sJnt'%(side,x.replace('Foot','')))
            JntSel.append(jnt_)
            

        IKJnt = DuplicateJnt(JntSel, 'IK')
        FKJnt = DuplicateJnt(JntSel, 'FK')
        DrvJnt = DuplicateJnt(JntSel, 'Drv')
        
        FootRigGrp=pm.createNode('transform',n='%sFootRigGrp'%side)
        AnkleCnsGrp=pm.createNode('transform',n='%sAnkleCnsGrp'%side,p=FootRigGrp)
        gn.PosCopy(FKJnt[-1],AnkleCnsGrp)
        IKScaleGrp=pm.createNode('transform',n='%sAnkleIKScaleGrp'%side,p=AnkleCnsGrp)
        IKCtrl=pm.PyNode('%sLegIKCtrl'%side)
        gn.PosCopy(IKCtrl,IKScaleGrp)
        JntGrp=pm.createNode('transform',n='%sFootJntGrp'%side,p=IKScaleGrp)
        gn.PosCopy(JntSel[-1],IKScaleGrp)
        IKJntGrp=pm.createNode('transform',n='%sFootIKJntGrp'%side,p=JntGrp)
        gn.PosCopy(JntSel[-1],IKJntGrp)
        pm.parent(FKJnt[0],DrvJnt[0],JntGrp)
        pm.parent(IKJnt[0],IKJntGrp)
        
        LastDrvJnt=pm.PyNode(JntSel[0].replace('Jnt','DrvJnt'))
        LastIKJnt=pm.PyNode(JntSel[0].replace('Jnt','IKJnt'))
        
        gn.Mcon(LastDrvJnt, AnkleCnsGrp, t=1, r=1, mo=1, pvtCalc=1)
        gn.Mcon(LastIKJnt, IKJntGrp, t=1, r=1, mo=1, pvtCalc=1)
        
        #Drv 조인트와 IKFK 연결
        IKFKCtrl=pm.PyNode(side+'LegIKFKCtrl')
        sel = [FKJnt[0], IKJnt[0], DrvJnt[0], IKFKCtrl]
        kb.IKFKBlend(sel)
        
        #Drv조인트와 바인드 조인트 연결
        for x,y in zip(DrvJnt,JntSel):
            gn.Mcon(x, y, t=1, r=1, mo=1, pvtCalc=1)

        # IK 리깅 , Foot 채널 연결
        InRollMV, OutRollMV, HeelRollPivMV, ToeRollPivMV, BallPivMV, FootRollMV, BallRollMV = FootIkJntRig(IKJnt,IKCtrl)
        
        # FKBallCtrl 만들기 
        shape = 'diamond'
        FKBallCtrl_ = gn.ControlMaker('%sBallFKCtrl' % (side), shape, MainColor, exGrp=0, size=Scale)
        FKBallCtrl=FKBallCtrl_[0]
        gn.PosCopy(FKJnt[1],FKBallCtrl)
        [pm.setAttr(FKBallCtrl+'.'+ss, keyable=0, channelBox=0) for ss in ['scaleX','scaleY','scaleZ']]
        pm.parent(FKBallCtrl,IKScaleGrp)
        gn.addNPO(FKBallCtrl,'Grp')
        gn.Mcon(FKBallCtrl, FKJnt[1], t=1, r=1, mo=1, pvtCalc=1)
        gn.rotate_components(90, 90, 0, nodes=FKBallCtrl)
        
        #IKBallCtrl 만들기 
        IKBallCtrl_ = pm.duplicate(FKBallCtrl,n=FKBallCtrl.replace('FK','IK'))
        IKBallCtrl=IKBallCtrl_[0]
        pm.parent(IKBallCtrl,IKJntGrp)
        
        IKBallCnsGrp=gn.addNPO(IKBallCtrl,'CnsGrp')
        IKBallGrp=gn.addNPO(IKBallCtrl,'Grp')
        gn.Mcon(IKJnt[0],IKBallCnsGrp[0], t=1, r=1, mo=1, pvtCalc=1)
        gn.Mcon(IKJnt[1],IKBallGrp[0], t=1, r=1, mo=1, pvtCalc=1)
        
        
        #BallDrvJnt의 translate랑 rotate 끊기 
        pb=DrvJnt[1].t.inputs()
        tt=DrvJnt[1].t.inputs(p=1)
        tt[0]//DrvJnt[1].t
        rr=DrvJnt[1].r.inputs(p=1)
        rr[0]//DrvJnt[1].r

        #trans 매트릭스 연결
        name=DrvJnt[1].replace('DrvJnt','')
        tmm=pm.createNode('multMatrix',n='%sTransMM'% name)
        tdm=pm.createNode('decomposeMatrix',n='%sTransDM'% name)

        IKBallCtrl.m >> tmm.i[0]
        IKBallGrp[0].m >> tmm.i[1]
        tmm.o >> tdm.imat
        
        
        tdm.outputTranslate>>pb[0].inTranslate1

        #rotate 매트릭스 연결
        rmm=pm.createNode('multMatrix',n='%sRotMM'% name)
        rdm=pm.createNode('decomposeMatrix',n='%sRotDM'% name)

        IKBallCtrl.m >> rmm.i[0]
        IKBallGrp[0].m >> rmm.i[1]
        rmm.o >> rdm.imat
        
        tdm.outputRotate>>pb[0].inRotate1
        
        gn.Mcon(IKBallCtrl,DrvJnt[1], t=1, r=1, mo=1, pvtCalc=1)

        #Auto 하이드 연결 
        cd_= IKFKCtrl.AutoHideIKFK.outputs()
        cd= cd_[0]
        cd.ocr >> FKBallCtrl.getParent().v
        cd.ocg >> IKBallCtrl.getParent().v
        
        #발 로테이트 가이드 위치로
        InGuide=pm.PyNode(side+'Foot_In_Guide')
        OutGuide=pm.PyNode(side+'Foot_Out_Guide')
        BackGuide=pm.PyNode(side+'Foot_Back_Guide')
        
        guide_=[InGuide,OutGuide,BackGuide]
        RotMVPos_=[InRollMV,OutRollMV,HeelRollPivMV]
        for i,x in zip(guide_,RotMVPos_):
            trans_=pm.xform(i, t=True, q=True, ws=True)
            pm.xform(x, t=(trans_[0],trans_[1],trans_[2]))
        
        for x in [ToeRollPivMV]:            
            trans_=pm.xform(JntSel[-1], t=True, q=True, ws=True)
            pm.xform(x, t=(trans_[0],trans_[1],trans_[2]))   

        for x in [BallPivMV, FootRollMV, BallRollMV]:
            trans_=pm.xform(JntSel[1], t=True, q=True, ws=True)
            pm.xform(x, t=(trans_[0],trans_[1],trans_[2]))

        
        #정리
        pm.parent(FootRigGrp,side+'LegRigGrp')
        [pm.setAttr(x+'.visibility', 0) for x in [IKJnt[0],FKJnt[0],DrvJnt[0]]]
    
#FootConvert() 

    
    
    
    