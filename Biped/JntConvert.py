# -*- coding: cp949 -*-
import pymel.core as pm
import sys,os,json
#파일패스
if os.path.isdir('D:\Ped\Biped'):
   script_path = 'D:\Ped\Biped'
else:
   script_path = 'Z:\mvtools\scripts\Biped'
if script_path in sys.path:
    pass
else:
    sys.path.insert(0, script_path)
    
import General_ as gn
import FilePathImport
# reload(gn)
# reload(FilePathImport)


def FromJson():      
    config_ = FilePathImport.loadConfig_("BipedName.json")
    return config_

config_=FromJson()   

def NameExtraction(Crv):
    side = []
    ob = []
    
    side_=config_["sideName"]

    for side_Value in side_:
        if side_Value in str(Crv):
            side = side_Value
        else: 
            pass
    
    obj_=config_["objName"]
    for obj_Value in obj_:
        if obj_Value in str(Crv):
            ob = obj_Value
        else: 
            pass
    
    parts_=config_["parts"]
    parts=parts_[ob]

    return side,ob,parts
    
def eqDistanceCurveDivide(curvename,segmentcurveLength):
    curveLength=pm.arclen(curvename)

    uVale=1.0/(segmentcurveLength-1)
    i=0
    posList=[]
    for x in range(segmentcurveLength):
        pointA=pm.pointOnCurve(curvename,top=True, pr=i, p=True )
        posList.append(pointA)
        i=i+uVale
    return posList


def spine_joint_make(curve_Name,spineName,joint_count,joint_start_n,type,ojVal='xzy',sawoVal='xdown'):
    jointParentName=[]
    jointPosition=eqDistanceCurveDivide(curve_Name,joint_count)

    jointList=[]
    pm.select(cl=1)
    Axis_=config_["Axis"]
    for x in jointPosition:
        createName='%s%s%sJnt'%(spineName.replace('_',''),str(joint_start_n).zfill(1),type)        
        Jnt_=pm.joint(p=x,n=createName)
        apJnt_=pm.ls(Jnt_)[0]
        jointList.append(apJnt_)
        joint_start_n+=1
    if jointList:
        pm.select(jointList[0])
        pm.makeIdentity (apply=1,t =0,r= 1 ,s =0 ,n =0 ,pn= 1)
        pm.joint(e=1  ,oj =Axis_[0] ,secondaryAxisOrient= Axis_[1],ch =1 ,zso=1)
        pm.setAttr ("%s.jointOrientX"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientY"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientZ"%jointList[-1], 0)
        pm.select(jointList)
 
    return jointList
    
def JntMake(AllCurve,segNumber, Type):
    JntList=spine_joint_make(curve_Name=AllCurve, spineName='%s'%(AllCurve.split('_')[0]), joint_count=segNumber, joint_start_n=1,type= Type)
    return JntList
    
def SplitJntMake(Crv):
    side,ob,parts=NameExtraction(Crv)
    segNumber_=len(parts)
    Jnt = JntMake(Crv, segNumber_, '')
    for x,y in zip(Jnt,parts):
        pm.rename(x,'%s%sJnt'%(side,y))    
    return Jnt

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
    pm.select(cl=1)

    for x in range(len(jointPosition)):
        
        createName='%s%sJnt'%(Crv.replace('_',''),x)        
        jointList.append(createName)
        pm.joint(p=jointPosition[x],n=createName)
    
    Axis_=config_["Axis"]
    if jointList:
        pm.parent(jointList[0],w=1)
        pm.makeIdentity (apply=1,t =0,r= 1 ,s =0 ,n =0 ,pn= 1)
        pm.select(jointList[0])
        pm.makeIdentity (apply=1,t =0,r= 1 ,s =0 ,n =0 ,pn= 1)
        pm.joint(e=1  ,oj =Axis_[0],secondaryAxisOrient= Axis_[1],ch =1 ,zso=1)
        pm.setAttr ("%s.jointOrientX"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientY"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientZ"%jointList[-1], 0)
    pm.select(jointList)

    return jointList
    
def PointJntMake(Crv):
    side,ob,parts=NameExtraction(Crv)
    Jnt = CurvePointToJnt(Crv)
    for x,y in zip(Jnt,parts):
        pm.rename(x,'%s%sJnt'%(side,y))    
    return Jnt

def MakeSplitBindJnt(Crv):
    
    side,ob,subOb=NameExtraction(Crv)
    BindJnt = SplitJntMake(Crv)
    
def MakePointBindJnt(Crv):

    side,ob,subOb=NameExtraction(Crv)
    BindJnt = PointJntMake(Crv)

def AllBindJntMake():
    SplitCrvList=['LeftClavicle_GuideCurve','LeftUpArm_GuideCurve','LeftDnArm_GuideCurve','LeftUpLeg_GuideCurve','LeftDnLeg_GuideCurve','Neck_GuideCurve','Spine_GuideCurve',
    'Tongue_GuideCurve','Jaw_GuideCurve']  
    PointCrvList=['LeftFoot_GuideCurve','LeftThumb_GuideCurve','LeftIndex_GuideCurve','LeftMiddle_GuideCurve','LeftRing_GuideCurve','LeftPinky_GuideCurve']  
    pm.select(cl=1)
    for x in SplitCrvList:
        crv_=pm.PyNode(x)
        MakeSplitBindJnt(crv_)
        
    for x in PointCrvList:
        crv_=pm.PyNode(x)
        MakePointBindJnt(crv_)

#Joint parent 정리 
def OrganizeJoint():
    pm.parent('LeftClavicleJnt','Neck1Jnt','ChestJnt')
    pm.delete('LeftClavicleTipJnt','LeftUpArmSeg4Jnt','LeftDnLegSeg4Jnt','LeftUpLegSeg4Jnt')
    wristJnt=pm.duplicate('LeftDnArmSeg4Jnt',n='LeftWristJnt')
    pm.parent(wristJnt,'LeftDnArmSeg4Jnt')
    pm.parent('LeftShoulderJnt','LeftClavicleSubJnt')
    pm.parent('LeftElbowJnt','LeftUpArmSeg3Jnt')
    pm.parent('LeftKneeJnt','LeftUpLegSeg3Jnt')
    pm.parent('LeftAnkleJnt','LeftDnLegSeg3Jnt')
    pm.parent('Tongue1Jnt','JawJnt','HeadJnt')
    pm.parent('LeftThighJnt','RootJnt')
    pm.parent('LeftThumbRootJnt','LeftIndexRootJnt','LeftMiddleRootJnt','LeftRingRootJnt','LeftPinkyRootJnt','LeftWristJnt')
    RightArmJnt=pm.mirrorJoint('LeftClavicleJnt', mirrorBehavior=1, myz=1, searchReplace=('Left', 'Right'))
    RightLegJnt=pm.mirrorJoint('LeftThighJnt', mirrorBehavior=1, myz=1, searchReplace=('Left', 'Right'))
    
    pm.setAttr('Biped_Guide.visibility',0)

def JntMake_Organize():
    AllBindJntMake()
    OrganizeJoint()

