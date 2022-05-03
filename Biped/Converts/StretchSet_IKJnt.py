# -*- coding: cp949 -*-
from pymel.core import *

def distancBetween_(name_):
    return shadingNode('distanceBetween', au=1, n='{}DB'.format(name_))

def blendTwoAttr_(name_):
    return shadingNode('blendTwoAttr', au=1, n='{}BA'.format(name_))

def multiplyDivide_(name_):
    return shadingNode('multiplyDivide', au=1, n='{}MD'.format(name_))

def multDoubleLinear_(name_):
    return shadingNode('multDoubleLinear', au=1, n='{}MDL'.format(name_))
    
def transform_(name_):
    return shadingNode('transform', au=1, n='{}Pos'.format(name_))
    
def addDoubleLinear_(name_):
    return shadingNode('addDoubleLinear', au=1, n='{}AL'.format(name_))

def blendColors_(name_):
    return shadingNode('blendColors', au=1, n='{}BC'.format(name_))
    
def condition_(name_):
    return shadingNode('condition', au=1, n='{}CD'.format(name_))

 #두 포스 사이 길이 구하기 
def PosLen(pos1,pos2):
    Len=distancBetween_('%s%sUpLen'%(side,ob))
    pos1.t>>Len.point1
    pos2.t>>Len.point2
    return Len
    
    
def IKNodeConnection( IKJnt, IKCtrl,PoleVectorCtrl):
    #위쪽, 아래쪽, 전체 길이 구하기 
    posList=[]
    for x in IKJnt:
        posMake=transform_(x.replace('Jnt','Pos'))
        posList.append(posMake)
        pm.delete(pm.parentConstraint(x,posMake))
    pos1,pos2,pos3=posList[0],posList[1],posList[2]
    MovePos=pm.duplicate(pos3,n=pos3.replace('Pos','MovePos'))
    pm.parent(mp,IKCtrl)
    pm.group(posList,n='%s%sPosGrp'%(side,ob))
    
    UpLen=distancBetween_('%s%sUpLen'%(side,ob))
    DnLen=distancBetween_('%s%sDnLen'%(side,ob))
    AllLen=distancBetween_('%s%sAllLen'%(side,ob))
    
    UpLen=PosLen(pos1,pos2)
    DnLen=PosLen(pos2,pos3)
    AllLen=PosLen(pos1,MovePos)

    adl=addDoubleLinear_('%s%sDefAllLen'%(side,ob))
    UpLen.distance>>adl.input1
    DnLen.distance>>adl.input2
    
    bc=blendColors_('%s%sAllStretch'%(side,ob))
    AllLen.distance>>bc.color1
    adl.o>>bc.color2
    
    md=multiplyDivide_('%s%sAllStretchNormal'%(side,ob))
    bc.outputR>>md.i1x
    bc.color2.color2R>>md.i2x
    
    cd=condition_('%s%sAllLen'%(side,ob))
    cd.operation.set(2)
    md.o>>cd.colorIfTrue
    bc.outputR>>cd.firstTerm
    bc.color2.color2R>>cd.secondTerm
    
    #폴벡터 스트레치 
    PVPos=transform_('%s%sPVStretch'%(side,ob))
    pm.pointConstraint(PoleVectorCtrl,PVStretchPos,mo=0)
    PVUpLen=PosLen(pos1,PVPos)
    PVDnLen=PosLen(PVPos,pos3)
    
    
    PVLens=[PVUpLen,PVDnLen]
    Lens=[UpLen,DnLen]
    
    for x in range(len(PVLens)):
        name_=PVLens[x].replace('Pos','')
        
        pv_md=multiplyDivide_('%sPVStretchNormalMD'%name_)
        PVLens[x].distance>>pv_md.i1x
        Lens[x].distance>>pv_md.i2x
        
        ba=blendTwoAttr_('%sPVStretchNormalMD'%name_)
        cd.outColorR>>ba.input[0]
        pv_md.ox>>ba.input[1]
        
        #슬라이드 
        s_mdl=multDoubleLinear_('%sSlideFilterMDL'%name_)    
        s_adl=addDoubleLinear_('%sSlideFilterADL'%name_)
        st_mdl=multDoubleLinear_('%sStretchFilterMDL'%name_)  
        pm.connectAttr(IKCtrl+'.%sSlide'%name_.replace(side+ob,''),s_mdl+'.input1')  
        s_mdl.o>>s_adl.input1
        s_adl.o>>st_mdl.input2
        
        ba.o>>st_mdl.input1
        
        
        
        
        #모든 스트레치 값 합치기 
        All_adl=multDoubleLinear_('%sStretchOutputMDL'%name_)
        jointTrans=IKJnt[1+x].attr('tx').get()
        All_adl.input2.set(jointTrans)
        st_mdl.o>>All_adl.input1
        
        JntConnectList=[]
        JntConnectList.append(All_adl)
        
    UptretchOutputMDL=JntConnectList[0]
    DntretchOutputMDL=JntConnectList[1]
    
    UptretchOutputMDL.o>>IKJnt[1]
    DntretchOutputMDL.o>>IKJnt[2]
        



# 첫번째와 마지막 조인트 잡고 실행해주세요
sel = ls(sl=1,r=1,fl=1)
tt=IKStretch(sel)