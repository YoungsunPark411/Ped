# -*- coding: cp949 -*-
import pymel.core as pm
import sys,os
if os.path.isdir('D:/Ped/Convert'):
   script_path = 'D:/Ped/Convert'
else:
   script_path = 'Z:/mvtools/scripts/rig/Script/Python3_script/Ped/Convert'
sys.path.insert(0, script_path)

import General as gn


# reload(gn)


def JntAxesChange(Axes, SAO, JntList):
    for x in JntList:
        pm.select(x)
        pm.joint(e=1, oj=Axes, secondaryAxisOrient=SAO, ch=1, zso=1)
    pm.setAttr("%s.jointOrientX" % JntList[-1], 0)
    pm.setAttr("%s.jointOrientY" % JntList[-1], 0)
    pm.setAttr("%s.jointOrientZ" % JntList[-1], 0)

def MakeShortJnt(Crv,Type):
    #조인트만들기
    shape_ = Crv.getShape()
    cv_List = shape_.getCVs()
    number=len(cv_List)
    Jnt = gn.JntMake(Crv, number, Type)

    #이름바꾸기
    side = gn.NameExtraction(Crv)[0]
    subob = gn.NameExtraction(Crv)[2]

    newJnt=[]
    for x in range(len(Jnt)):
        nm=pm.rename(Jnt[x],side+subob[x]+'Jnt')
        newJnt.append(nm)

    return newJnt

def MakeLongJnt(Crv,number,Type):
    # 조인트만들기
    Jnt = gn.JntMake(Crv, number, Type)

    # 이름바꾸기
    side = gn.NameExtraction(Crv)[0]
    ob = gn.NameExtraction(Crv)[1]

    newJnt = []
    JntRvs=Jnt.reverse 
    print(JntRvs)
    ######여기 고치는 중 
    '''
    count=len(Jnt) 
    for x in range(len(JntRvs)):
        
        nm = pm.rename(JntRvs[x], side + ob +'%s'%(count-x) +'Jnt')
        newJnt.append(nm)
    
    JntAxesChange('xzy', 'ydown', newJnt)
    print(newJnt)
    '''
    return newJnt


ShortCrvList=['LeftClavicle_GuideCurve','Neck_GuideCurve','Spine_GuideCurve','LeftWrist_GuideCurve',
              'LeftAnkle_GuideCurve','LeftFoot_GuideCurve']
LongCrvList=['LeftUpArm_GuideCurve','LeftDnArm_GuideCurve',
              'LeftUpLeg_GuideCurve','LeftDnLeg_GuideCurve']
CrvList=ShortCrvList+LongCrvList
#바인드조인트 만들기
def orgJnt(Type):
    for x in LongCrvList:
        jnt1=MakeLongJnt(x,5,Type)
        pm.mirrorJoint(jnt1[0], mirrorBehavior=1, myz=1, searchReplace=('Left', 'Right'))
    '''
    for x in ShortCrvList:
        print(type(x))
        jnt2=ShortCrvList(x,Type)
        pm.mirrorJoint(jnt2[0], mirrorBehavior=1, myz=1, searchReplace=('Left', 'Right'))
    '''


# 그외조인트 만들기
def ExtJnt(*op):
    TypeList=[op]
    for Type in TypeList:
        for x in CrvList:
            MakeShortJnt(x, Type)
            pm.mirrorJoint(jnt1[0], mirrorBehavior=1, myz=1, searchReplace=('Left', 'Right'))

def AllMakeJnt():
    BindJnt=orgJnt('')
    #TwistJnt = orgJnt('Drv')
    #ExtJnt('IK','FK','Drv')

AllMakeJnt()











