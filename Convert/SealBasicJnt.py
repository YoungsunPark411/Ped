# -*- coding: cp949 -*-
import pymel.core as pm
import sys
sys.path.append(r'D:\MyScript\sealped')


from Material import General as gn
#reload(gn)


def JntAxesChange(Axes,SAO,JntList):
    for x in JntList:
        pm.select(x)
        pm.joint(e=1  ,oj =Axes ,secondaryAxisOrient= SAO,ch =1 ,zso=1)
    pm.setAttr ("%s.jointOrientX"%JntList[-1], 0)
    pm.setAttr ("%s.jointOrientY"%JntList[-1], 0)
    pm.setAttr ("%s.jointOrientZ"%JntList[-1], 0)
        
def SealSpineRig(AllCurve):

    side = gn.NameExtraction(AllCurve)[0]
    ob = gn.NameExtraction(AllCurve)[1]
    subob = gn.NameExtraction(AllCurve)[2]

  

    # 조인트만들기
           
    def AddPartsCurve(CurveName,count):
        
        pm.delete(CurveName, constructionHistory = True)
        pm.select(CurveName)
        Curve=pm.ls(sl=1)[0]       
        shape_=Curve.getShape()
        NewCurve=pm.detachCurve(shape_.ep[count], ch=True, replaceOriginal=False )
        
            
        return NewCurve
    

    def RootJnt():
        if 'UpSpine' in AllCurve:
            _subob=['Chest','Neck1','Neck2','Neck3','Neck4','Head']
            number=6
        elif 'DnSpine' in AllCurve:
            _subob=['Spine1','Spine2','Spine3','Spine4']
            number=4
        else:
            _subob=subob
            number=4
        Jnt=gn.JntMake(AllCurve,number, '')
        
        list=[]
    
        for x, y in zip(Jnt, _subob):

            if 'Up'  in AllCurve:
                new = pm.rename(x, '%sJnt' % ( y))
            elif 'Dn' in AllCurve:
                new = pm.rename(x, '%sJnt' % ( y))
            else: 
                new = pm.rename(x, '%s%sJnt' % (side, y))
                            
            list.append(new)
        JntAxesChange('xzy','ydown',list)

        Nlist = gn.jntList(list[0], '')
  
        return Nlist

    def Name_seg(JntList,seg_):
       for x in JntList:
            pm.rename(x, '%s%sJnt' % (side, seg_))                                


    def ClavicleJnt(Crv):
        Clavicle_Jnt=gn.JntMake(Crv,2, '')       
        
        JntAxesChange('xzy','zdown',Clavicle_Jnt)
        pm.delete(Clavicle_Jnt[1],Crv)
        nn=pm.rename(Clavicle_Jnt[0],side+'ClavicleJnt')
        
        return nn
            
        
    def ArmJnt():       
        Detatch_Curve=AddPartsCurve(AllCurve,1)
        UpCrv=Detatch_Curve[0]      
        DnCrv=Detatch_Curve[1]
        pm.rename(UpCrv, UpCrv.replace(side, side + 'Up'))
        pm.rename(DnCrv, DnCrv.replace(side, side + 'Dn'))
        Up_Jnt=gn.JntMake(UpCrv,5, '')       
        Dn_Jnt=gn.JntMake(DnCrv,5, '')
        JntAxesChange('xzy','zdown',Up_Jnt)
        JntAxesChange('xzy','zdown',Dn_Jnt)
        UpJnt=[]
        for x in Up_Jnt: 
            nn=pm.rename(x, x.replace(ob,ob+'Seg')) 
            UpJnt.append(nn)
        DnJnt=[]
        for x in Dn_Jnt: 
            nn=pm.rename(x, x.replace(ob,ob+'Seg')) 
            DnJnt.append(nn)
        pm.parent(DnJnt[1],UpJnt[-1])
        pm.delete(DnJnt[0])
        
        first=pm.rename(UpJnt[0],side+subob[0]+'Jnt')
        pm.rename(UpJnt[-1],side+subob[1]+'Jnt')
        pm.rename(DnJnt[-1],side+subob[2]+'Jnt')
        
        pm.delete(UpCrv,DnCrv)

        Nlist=gn.jntList(first, '') 
  
        
        if ob== 'Arm':
            Clavicle_Jnt=ClavicleJnt(side+'Clavicle_GuideCurve')
          
            pm.parent(Nlist[0],Clavicle_Jnt)
            if pm.objExists('ChestJnt'):
                pm.parent(Clavicle_Jnt,'ChestJnt')
            else:
                pass


        return Nlist
                     
        
    if 'Spine' in AllCurve:
        MakeJnt=RootJnt()
       
    else:
        MakeJnt=ArmJnt()
    return MakeJnt
        
def ElseJnt(AllCurve):
    Crv_=pm.PyNode(AllCurve)
    cvNum = int(len(Crv_.getShape().getCVs()))
    Jnt_=gn.JntMake(Crv_,cvNum, 'Fix')      
    JntAxesChange('xzy','ydown',Jnt_)
    Nlist=[] 
    for x in range(len(Jnt_)):       
        nn=pm.rename(Jnt_[x],AllCurve.split('_')[0]+'%sJnt'%(x+1))
        Nlist.append(nn)     
    return Nlist
    
def LegJnt(AllCurve):
    sideList=['Left','Right']
    for sd in sideList:
        if sd in AllCurve:
            side=sd
    LegList=['Leg','Knee','Foot']
    Jnt_=ElseJnt('LeftLeg_GuideCurve')
    Nlist=[] 
    for x in range(len(Jnt_)):       
        nn=pm.rename(Jnt_[x],side+LegList[x]+'Jnt')
        Nlist.append(nn) 
    if pm.objExists('Spine4Jnt'):
        pm.parent(Nlist[0],'Spine4Jnt')
    else:
        pass

    return Nlist
    
    
  

def FingerJntList(obj='Finger'):
    if obj=='Finger':
        FingerList=['Index','Middle','Ring','Pinky']
    elif obj=='Toe':
        FingerList=['BigToe','SecondToe','ThirdToe','LittleToe']
    JntList=[]
    for x in FingerList:
        Jnt_=ElseJnt('Left'+x+'_GuideCurve')
        JntAxesChange('xzy','yup',Jnt_)
        JntList.append(Jnt_)
    if obj=='Finger':
        if pm.objExists('LeftWristJnt'):
            for i in FingerList:
                pm.parent('Left%s1Jnt'%(i),'LeftWristJnt')    
        else:
            pass
    if obj=='Toe':
        if pm.objExists('LeftFootJnt'):
            for i in FingerList:
                pm.parent('Left%s1Jnt'%(i),'LeftFootJnt')    
        else:
            pass
    

    return JntList
        
        
def MirrorJnt(LeftJnt):
    pm.mirrorJoint(LeftJnt,mirrorBehavior=1,myz=1,searchReplace=('Left', 'Right') )

    



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def BasicJnt():

    UpSpineJnt = SealSpineRig('UpSpine_GuideCurve')
 
    DnSpineJnt = SealSpineRig('DnSpine_GuideCurve')
  
    LeftArmJnt = SealSpineRig(AllCurve='LeftArm_GuideCurve')
    LeftFingerJnt=FingerJntList('Finger')
    RightArmJnt = MirrorJnt('LeftClavicleJnt')
    LeftLegJnt = LegJnt('LeftLeg_GuideCurve')
    LeftToeJnt = FingerJntList('Toe')
    RightLegJnt = MirrorJnt(LeftLegJnt[0])

    
    #rootJnt_=pm.PyNode('RootJnt')
    RJ=pm.createNode('joint',n='RootJnt')
    gn.PosCopy(UpSpineJnt[0],RJ)
    pm.parent(DnSpineJnt[0],UpSpineJnt[0],RJ)
    pm.delete('Sealped_Guide')


#BasicJnt()



    
    





