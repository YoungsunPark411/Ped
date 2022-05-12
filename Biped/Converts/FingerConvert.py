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
    
# FK 리깅 만들기
def FKCtrlMake(JntList, shape_, cns):
    ctrlList = []
    for x in JntList[:-1]:
        if 'ThumbRoot' in str(x):
            FKCtrl = gn.ControlMaker('%sCtrl' % x.replace('Jnt', '').replace('FK', ''), 'FingerRoot', fingerMainColor, exGrp=0, size=Scale*0.5)
        else:
            FKCtrl = gn.ControlMaker('%sCtrl' % x.replace('Jnt', '').replace('FK', ''), shape_, fingerMainColor, exGrp=0, size=Scale*0.5)
        gn.PosCopy(x, FKCtrl[0])
        ctrlList.append(FKCtrl[0])
        gn.rotate_components(90, 0, 90, FKCtrl[0])
    for i in range(len(ctrlList)):
        if i == 0: continue
        pm.parent(ctrlList[i], ctrlList[i - 1])

    if cns == 0:
        pass
    elif cns == 1:
        for i in range(len(ctrlList)):
            gn.Mcon(ctrlList[i], JntList[i], t=1, r=1, mo=0, pvtCalc=1)
    for y in ctrlList:
        if y == ctrlList[0]:
            gn.addNPO(y,'Grp')
            continue
        gn.addNPO(y, 'Pos')
    MotherFKCtrlGrp = pm.listRelatives(ctrlList[0], p=1)[0]
    return ctrlList, MotherFKCtrlGrp


def IKRig(IKJnt):
    #IKCtrl 만들기 
    IKCtrl_ = gn.ControlMaker('%sIKCtrl'%(side+ob), 'pyramid', MainColor, exGrp=0, size=Scale*0.5)
    IKCtrl= IKCtrl_[0]
    gn.PosCopy(IKJnt[-1],IKCtrl)
    pm.select(IKCtrl)
    gn.rotate_components(0, 0, -90, nodes=None)
    gn.translate_components(0.5, 0, 0, nodes=None)
    #IK핸들리깅 
    name_=side+ob
    AimUpVec=pm.createNode('transform', n='%sAimUpVec'%name_)
    gn.PosCopy(IKCtrl,AimUpVec)
    pm.parent(AimUpVec,IKCtrl)
    AimGrp=pm.createNode('transform', n='%sAimGrp'%name_)
    gn.PosCopy(IKJnt[1], AimGrp )
    PvPos=pm.duplicate(AimGrp,n=AimGrp.replace('AimGrp','PvPos'))
    pm.parent(PvPos,AimGrp)
    if 'Left' in str(side):
        transZ=0.5
    if 'Right' in str(side):
        transZ=-0.5
    pm.setAttr(PvPos[0]+'.translateZ',transZ)
    pm.aimConstraint(IKCtrl, AimGrp, wut=2,worldUpObject=AimUpVec,mo=1)      
    if pm.getAttr(IKJnt[1]+'.preferredAngleY') ==0:        
        pm.setAttr(IKJnt[1]+'.preferredAngleY',0.1)
    if 'Thumb' in str(IKJnt[2]):
        pm.setAttr(IKJnt[2]+'.preferredAngleY',0.1)
    IKHandle = pm.ikHandle(sj=IKJnt[0], ee=IKJnt[-1],n='%sIKHandle' % (name_), sol='ikRPsolver', ccv=0)                               
    pm.parent(IKHandle[0],IKCtrl)
    pm.poleVectorConstraint(PvPos,IKHandle[0],n='%sIKJntPoleVectorConst' % (name_))
    
    return IKCtrl, AimGrp, IKHandle[0]

def FingerCtrlMake():
    FingerCtrl = gn.ControlMaker('%sFingerCtrl'%side, 'Finger', MainColor, exGrp=0, size=Scale/8)
    gn.translate_components(7, -7, 0, nodes=FingerCtrl[0])
    WristJnt=pm.PyNode('%sWristJnt'%side)                          
    gn.PosCopy(WristJnt, FingerCtrl[0])   
    gn.addNPO(FingerCtrl[0],'Grp')
    gn.Mcon(WristJnt, FingerCtrl[0].getParent(), t=1, r=1, mo=0, pvtCalc=1) 
    
    [pm.setAttr('%sFingerCtrl.translate%s' %(side, Change), lock=1, keyable=0, channelBox=0) for Change in ['X', 'Y', 'Z']]
    [pm.setAttr('%sFingerCtrl.rotate%s' %(side, Change), lock=1, keyable=0, channelBox=0) for Change in ['X', 'Y', 'Z']]
    [pm.setAttr('%sFingerCtrl.scale%s' %(side, Change), lock=1, keyable=0, channelBox=0) for Change in ['X', 'Y', 'Z']]
    fingerList = ['Index', 'Middle', 'Ring', 'Pinky','Thumb']
    for finger in fingerList:                    
        pm.addAttr(FingerCtrl[0],ln="%sFold" % finger, at='enum', en='____________', k=1)
        pm.setAttr(FingerCtrl[0]+".%sFold" % finger, lock=1)      
        pm.setAttr(FingerCtrl[0]+".%sFold" % finger, lock=1)
        pm.addAttr(FingerCtrl[0], ln="%s1" % finger, at='double', dv=0, k=1)
        pm.addAttr(FingerCtrl[0], ln="%s2" % finger, at='double', dv=0, k=1)
        pm.addAttr(FingerCtrl[0], ln="%s3" % finger, at='double', dv=0, k=1)
    
    pm.addAttr(FingerCtrl[0], ln="Spread", at='enum', en='___________', k=1)
    pm.setAttr(FingerCtrl[0]+".Spread" , lock=1)
    for finger in fingerList:
        pm.addAttr(FingerCtrl[0], ln="%sSpread" % finger, at='double', dv=0, k=1)
    
    pm.addAttr(FingerCtrl[0], ln="Roll", at='enum', en='____________', k=1)
    pm.setAttr(FingerCtrl[0]+".Roll" , lock=1)
    for finger in fingerList:            
        pm.addAttr(FingerCtrl[0], ln="%sRoll" % finger, at='double', dv=0, k=1)
    pm.addAttr(FingerCtrl[0], ln="IKCtrlVis", at='bool', k=1)
    pm.addAttr(FingerCtrl[0], ln="FKCtrlVis", at='bool', k=1)
    pm.setAttr(FingerCtrl[0]+".IKCtrlVis" ,0, keyable=0,channelBox=1)
    pm.setAttr(FingerCtrl[0]+".FKCtrlVis" ,0, keyable=0,channelBox=1)
    
    return FingerCtrl[0]

   
def FKConnect(FKCtrl,FingerCtrl,IKJnt):

    for i in FKCtrl:
        if i == FKCtrl[0]: continue
        OffGrp = gn.addNPO(i, 'Off')           
        FKGrp= gn.addNPO(i, 'Grp')            
    
    fingerList = ['Index', 'Middle', 'Ring', 'Pinky','Thumb']  
         
    for i in fingerList:
        if i in str(FKCtrl[0]):
            finger = i
        else: pass

    pm.connectAttr(FingerCtrl+'.%s1'%finger, FKCtrl[1].getParent().getParent()+'.rotateY')
    pm.connectAttr(FingerCtrl + '.%sRoll'%finger, FKCtrl[1].getParent().getParent() + '.rotateX')
    pm.connectAttr(FingerCtrl + '.%sSpread' % finger, FKCtrl[1].getParent().getParent() + '.rotateZ')
    
    pm.connectAttr(FingerCtrl+'.%s2'%finger, FKCtrl[2].getParent().getParent()+'.rotateY')
    
    pm.connectAttr(FingerCtrl+'.%s3'%finger, FKCtrl[3].getParent().getParent()+'.rotateY')
        
    
def ConnectPos(FKCtrl):
    CntPosList = []
    for x in FKCtrl:
        CntPos=pm.createNode('transform',n=x.replace('Ctrl','CntPos'))
    
        gn.PosCopy(x, CntPos)
        CntPosList.append(CntPos)

    for i in range(len(CntPosList)):
        if i == 0: continue
        pm.parent(CntPosList[i], CntPosList[i - 1])

    for i in range(len(CntPosList)):
        if i == 0: continue
        pm.parentConstraint(CntPosList[i].replace('CntPos','IKJnt'), CntPosList[i],mo=1)

        CntPosList[i].t>> pm.PyNode(CntPosList[i].replace('CntPos','CtrlPos')).t
        CntPosList[i].r>> pm.PyNode(CntPosList[i].replace('CntPos','CtrlPos')).r

    pm.parent(CntPosList[0],FKCtrl[0])
    return CntPosList


def FingerRig(JntSel,FingerCtrl):
    
    #RigGrp 만들기
    RigGrp=pm.createNode('transform',n='%s%sRigGrp'%(side,ob))
    CtrlGrp=pm.createNode('transform',n='%s%sCtrlGrp'%(side,ob),p=RigGrp)
    gn.PosCopy(JntSel[1],CtrlGrp)
    #IK 조인트 만들기 
    IKJnt = DuplicateJnt(JntSel, 'IK')
    #Bind 조인트에 FK 컨트롤 달기
    FKCtrl, MotherFKCtrlGrp = FKCtrlMake(JntSel, 'pin', 1)
    #IK컨트롤, 핸들
    IKCtrl, AimGrp, IKHandle=IKRig(IKJnt)
    # FingerCtrl이랑 FKCtrl 연결
    FKConnect(FKCtrl,FingerCtrl,IKJnt)
    #Ctrl Pos 만들고 연결 
    ConnectPos(FKCtrl)

    #정리
    for x in FKCtrl:
        FingerCtrl.FKCtrlVis>>x.getShape().visibility
    
    gn.addNPO(IKCtrl,'Grp')
    FingerCtrl.IKCtrlVis>>IKCtrl.getParent().visibility
    pm.parent(CtrlGrp,RigGrp)
    pm.parent(IKJnt[0],IKCtrl.getParent(),AimGrp,FKCtrl[0])
    pm.parent(FKCtrl[0].getParent(),CtrlGrp)
    IKHandle.v.set(0)
    IKJnt[0].v.set(0)
    
    return RigGrp


def FingerConvert():
    global Scale
    Scale=gn.scaleGet()
    ObjName = ['LeftIndex','LeftMiddle','LeftRing','LeftPinky','LeftThumb',
    'RightIndex','RightMiddle','RightRing','RightPinky','RightThumb']    
    FingerRigList=[]
    for i in ObjName:
        global side,ob,parts,colors,MainColor, SubColor, fingerMainColor
        side,ob,parts,colors=NameExtraction(i)
        MainColor, SubColor, fingerMainColor = int(colors[0]), int(colors[1]), int(colors[2])
        if 'Index' in i:
            FingerCtrl=FingerCtrlMake()
        if 'RightIndex' in i:
            FingerRigList=[]
        JntSel = []
        for x in parts:
            jnt_=pm.PyNode('%s%sJnt'%(side,x))
            JntSel.append(jnt_)
        RigGrp=FingerRig(JntSel,FingerCtrl)
        FingerRigList.append(RigGrp)
        
        if 'Thumb' in i:
            #정리
            FingerRigGrp=pm.createNode('transform',n='%sFingerRigGrp'%(side))
            WristCnsGrp=pm.createNode('transform',n='%sWristCnsGrp'%(side),p=FingerRigGrp)
            WristJnt=pm.PyNode('%sWristJnt'%side)                          
            gn.PosCopy(WristJnt, WristCnsGrp) 
            if pm.objExists(side+'WristDrvJnt'):  
                LastDrvJnt=pm.PyNode(side+'WristDrvJnt')
                gn.Mcon(LastDrvJnt, WristCnsGrp, t=1, r=1, mo=1, pvtCalc=1) 
                # 스케일 하다 말음...
                # for i,drv in enumerate(DrvChain):
                #     name_ = side+'HandScaleBC'
                #     BC_ = pm.shadingNode('blendColors', au=1, n='{0}BC'.format(name_))

                #     FKChain[i].r >> PB_.ir2
                #     FKChain[i].t >> PB_.it2
                #     FKChain[i].s >> BC_.color1
                #     IKChain[i].r >> PB_.ir1
                #     IKChain[i].t >> PB_.it1
                #     #IKChain[i].SquashScaleY >> BC_.color2G
                #     #IKChain[i].SquashScaleZ >> BC_.color2B

                #     PB_.outTranslate >> drv.t
                #     PB_.outRotate >> drv.r
                #     #BC_.output >> OrigChain[i].s

                #     switch.IKFK>>BC_.blender
                #     switch.IKFK >> PB_.weight
                #스케일은 차후 해보자,....
            pm.parent(FingerCtrl.getParent(),FingerRigList,WristCnsGrp)
            if pm.objExists(side+'ArmRigGrp'):  
                pm.parent(FingerRigGrp, side+'ArmRigGrp')
    
    

#FingerConvert()