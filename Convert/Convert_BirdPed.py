# -*- coding: cp949 -*-
import pymel.core as pm
import sys,os
if os.path.isdir('D:/Ped/Convert'):
   script_path = 'D:/Ped/Convert'
else:
   script_path = 'Z:/mvtools/scripts/rig/Script/Python3_script/Ped/Convert'
sys.path.insert(0, script_path)

import General as gn
import JointSeperate as js


# reload(gn)


def JntAxesChange(Axes, SAO, JntList):
    #pm.joint(JntList[0],e=1, oj=Axes, secondaryAxisOrient=SAO, ch=1, zso=1)
    for x in JntList:
        pm.select(x)
        pm.joint(e=1, oj=Axes, secondaryAxisOrient=SAO, ch=1, zso=1)
    pm.setAttr("%s.jointOrientX" % JntList[-1], 0)
    pm.setAttr("%s.jointOrientY" % JntList[-1], 0)
    pm.setAttr("%s.jointOrientZ" % JntList[-1], 0)

def CurvePoint(Crv):
    shape_ = Crv.getShape()
    shape_List= shape_.getCVs()
    posList=[]
    for x in range(len(shape_List)):
        posList.append(x)
    return posList


def CurvePointToJnt(Crv):
    shape_ = Crv.getShape()
    jointPosition= shape_.getCVs()
    jointList=[]
    i=0
    pm.select(cl=1)
    for x in jointPosition:
        i+=1
        createName='%s%sJnt'%(Crv.replace('_Curve',''),i)
        jointList.append(createName)
        pm.joint(p=x,n=createName)

    if jointList:
        pm.parent(jointList[0],w=1)
        pm.makeIdentity (apply=1,t =0,r= 1 ,s =0 ,n =0 ,pn= 1)
        pm.joint(e=1  ,oj ='xzy' ,secondaryAxisOrient= 'zdown',ch =1 ,zso=1)
        pm.setAttr ("%s.jointOrientX"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientY"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientZ"%jointList[-1], 0)

    return jointList

def JntNameChange(Jnt_,newName):
    Jnt_.reverse()
    jntList=[]
    for x in range(len(Jnt_)):
        nm=pm.rename(x,newName[x])
        jntList.append(nm)
    jntList.reverse()
    return jntList
    
    
def JntNameSet(Jnt_,Crv,Type):
    #이름바꾸기
    if 'Left' in str(Crv):
        side = 'Left'
    elif 'Right' in str(Crv):
        side = 'Right'
    else:
        side = ''
    nmJntlist=[]
    if 'Arm' in str(Jnt_):
        ob = ['Clavicle','Shoulder', 'Elbow', 'Wrist', 'WristTip']
        for x in range(len(Jnt_)):
            nm=pm.rename(Jnt_[x],side+ob[x]+Type+'Jnt')
            nmJntlist.append(nm)
    elif 'Leg' in str(Jnt_):
        ob = ['Thigh', 'Knee', 'Ankle']
        for x in range(len(Jnt_)):
            nm=pm.rename(Jnt_[x],side+ob[x]+Type+'Jnt')
            nmJntlist.append(nm)

    else:
        i=0
        if '_Curve' in str(Crv):
            ob=Crv.split('_Curve')[0]
        else:
            ob=str(Crv)
        for x in range(len(Jnt_)):
            i+=1
            nm=pm.rename(Jnt_[x],ob+'%s%sJnt'%(i,Type))
            nmJntlist.append(nm)

    return nmJntlist

def SegJntNameSet(segJnt):
    #이름바꾸기
    if 'Left' in str(segJnt[0]):
        side = 'Left'
    elif 'Right' in str(segJnt[0]):
        side = 'Right'
    else:
        side = ''
    
    if 'Thigh' in str(segJnt[0]):
        ob = 'LegUp'    
    elif 'Knee' in str(segJnt[0]):
        ob= 'LegDn'
    elif 'Shoulder' in str(segJnt[0]):
        ob= 'ArmUp'
    elif 'Elbow' in str(segJnt[0]):
        ob= 'ArmDn'
    
    
    nmJntlist=[]
    i=0
    for x in range(len(segJnt)):
        i+=1
        nm=pm.rename(segJnt[x],side+ob+'%sJnt'%i)
        nmJntlist.append(nm)
    
    return nmJntlist

    
def TypeChange(Jnt_,Type):
    nmJntlist=[]
    if op:
        for x in Jnt_:
            pm.rename(x,x.replace('Jnt','%sJnt'%Type))
            


def BindJntMake(Crv,*op):
    fJnt_=CurvePointToJnt(Crv)
    nJnt=JntNameSet(fJnt_,Crv,'')
    if 'Arm' in str(Crv):
        JntAxesChange('xyz', 'xup', nJnt)
    elif 'Hip' in str(Crv):
        JntAxesChange('xyz', 'xdown', nJnt)
    elif 'spine' or 'Neck' or 'Toe' in str(Crv):
        JntAxesChange('xzy', 'yup', nJnt)
    else:
        JntAxesChange('xyz', 'yup', nJnt)

    if 'Left' in str(Crv) :
        RightJnt=pm.mirrorJoint(nJnt[0], mirrorBehavior=1, myz=1, searchReplace=('Left', 'Right'))
    else:
        pass
    if 'Arm' in str(Crv):
        for x in RightJnt[1:3]:
            pm.select(x)
            R_segJnt=js.linearSpacingJoint(3,'-x')	
            SegJntNameSet(R_segJnt)
        for x in nJnt[1:3]:
            pm.select(x)
            L_segJnt=js.linearSpacingJoint(3,'x')
            SegJntNameSet(L_segJnt)	
    
    elif  'Leg' in str(Crv):

        for x in RightJnt[0:2]:
            pm.select(x)
            R_segJnt=js.linearSpacingJoint(3,'-x')	
            SegJntNameSet(R_segJnt)
        for x in nJnt[0:2]:
            pm.select(x)
            L_segJnt=js.linearSpacingJoint(3,'x')	
            SegJntNameSet(L_segJnt)
            
# 머리조인트나 꼬리등 더 넣어야할 조인트가 있지만 일단 수동으로!
selCrv=pm.ls(sl=1)
for x in selCrv:
    BindJntMake(x,'')











