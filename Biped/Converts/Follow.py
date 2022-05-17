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


import json
import FilePathImport


#파일패스 
if os.path.isdir('D:\Ped\Biped\Converts'):
   script_path = 'D:\Ped\Biped\Converts'
else:
   script_path = 'Z:\mvtools\scripts\Biped\Converts'
if script_path in sys.path:
    pass
else:
    sys.path.insert(0, script_path)

def CnsMake(cns,pa,ch):
    if cns == 'scale':
        cns_=pm.scaleConstraint(pa,ch,mo=1)
    elif cns == 'orient':
        cns_ = pm.orientConstraint(pa, ch,mo=1)
    elif cns == 'point':
        cns_ = pm.pointConstraint(pa, ch,mo=1)
    elif cns == 'parent':
        cns_ = pm.parentConstraint(pa, ch,mo=1)
    else:
        pass
    return cns_

# 드라이브 들(컨트롤) 선택 후 드리븐(컨트롤-Follow 채널이 있어야한다) 선택
def FollowMake(sel,cnsType):
    driven=sel[-1]
    driver=sel[:-1]

    #드라이브 그룹, 스페이스 널 만들기
    spaceList=[]
    for x in driver:
        dirGrp=x+'FollowGrp'
        if not pm.objExists(dirGrp):
            dir_Grp=pm.createNode('transform',n=dirGrp)
            pm.delete(pm.parentConstraint(x,dir_Grp))
            pm.parent(dir_Grp,x)
        else:
            dir_Grp=dirGrp
        space = pm.createNode('transform', n=x.split('Ctrl')[0]+driven.split('Ctrl')[0]+'Space')
        spaceList.append(space)
        pm.delete(pm.parentConstraint(driven, space))
        pm.parent(space,dir_Grp)

    drnGrp=pm.PyNode(driven).getParent()

    CNS_=CnsMake(cnsType, spaceList, drnGrp)

    attrlist = []
    for i in range(len(sel[:-1])):
        find = CNS_.attr('target[%s].targetWeight' % i)
        Str_find = str(find)
        F_attr = find.listConnections(d=0, s=1, p=1)[0]
        Str_attr = str(F_attr)
        attrlist.append(Str_attr)

    set_names=attrlist
    for i, set_name in enumerate(set_names):
        set_members = [set_name] or []
        for member in set_members:
            for j in range(len(set_names)):
                pm.setDrivenKeyframe(member, cd="{}.Follow".format(driven), dv=j, v=i == j)
    
    
def ArmLegRigConvert():
    ObjName = ['LeftArm','RightArm','LeftLeg','RightLeg']    
    for i in ObjName:
        global side,ob,parts,colors,MainColor, SubColor, fingerMainColor
        side,ob,parts,colors=NameExtraction(i)


def FollowRig():
    config_ = FilePathImport.loadConfig_("BipedName.json")
    
    drive=[]
    cns=[]
    
    follow_=config_["follow"]
    
    channel=list(config_["follow"].keys())
    
    for x in list(config_["follow"].values()):
        cns.append(x[0])
        drive.append(x[1])
        
    #드라이브들 잡고 채널있는 컨트롤 잡기 
    for i,x in enumerate(channel):
        sel=drive[i]+[x]	
        FollowMake(sel,cns[i])    

    return follow_


#드라이브들 잡고 채널있는 컨트롤 잡기 
# sel=pm.ls(sl=1)				
# FollowMake(sel,'orient')

