# -*- coding: cp949 -*-
from pymel.core import *

def get_transform(object_):
    _name = object_.name()
    trans = xform(_name, q=1, ws=1, rp=1 )
    rot = xform(_name, q=1, ws=1, ro=1 )
    return trans, rot

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

def createNodes(name_, names_, crvs_, divNumList):
    names_ = names_[1:]
    dict_ = {}
    dict_['db'] = distancBetween_('{0}DB'.format(name_))
    dict_['al'] = addDoubleLinear_('{0}DefAllLenADL'.format(name_))
    dict_['bc'] = blendColors_('{0}BC'.format(name_))

    return dict_
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
        All_adl.input2.set()
        st_mdl.o>>All_adl.input1
    
    
    
    
    
    
    
        

    
    
    for p,pc in enumerate(dict_['pc']):
        pc.attr('parameter').set(divNumList[p])
        dict_['chkpc'][p].attr('parameter').set(divNumList[p])
        if pc in dict_['pc'][:-1]:
            pc.position >> dict_['db'][p].point1
            dict_['chkpc'][p].position >> dict_['chkdb'][p].point1
            dict_['md'][p].attr('operation').set(2)
            dict_['md1'][p].attr('operation').set(3)
            dict_['md2'][p].attr('operation').set(2)
            dict_['md2'][p].attr('i1x').set(1)
            dict_['md2'][p].attr('i1y').set(1)
            dict_['md2'][p].attr('i1z').set(1)
            dict_['db'][p].distance >> dict_['ba'][p].input[1]
            dict_['stml'].o >> dict_['ba'][p].attributesBlender
            dict_['sqml'].o >> dict_['md1'][p].i2x
            dict_['ba'][p].o >> dict_['md'][p].i1x
            dict_['md'][p].ox >> dict_['ml'][p].i1
            dict_['md'][p].ox >> dict_['md1'][p].i1x
            dict_['md1'][p].ox >> dict_['md2'][p].i2y
            dict_['md1'][p].ox >> dict_['md2'][p].i2z
            dict_['chkdb'][p].distance >> dict_['ba'][p].input[0]
            dict_['chkdb'][p].distance >> dict_['md'][p].i2x
        if p>0:
            pc.position >> dict_['db'][p-1].point2
            dict_['chkpc'][p].position >> dict_['chkdb'][p-1].point2
    
    #dict_['md2'][0].oy >> joints_[0].sy
    #dict_['md2'][0].oz >> joints_[0].sz
    for i,db in enumerate(dict_['db']):
        dist_ = db.getAttr('distance')
        dict_['ml'][i].attr('i2').set(dist_)
        dict_['ml'][i].o >> joints_[1:][i].tx
        addAttr(joints_[1:][i],ln="SquashScaleY", at='double',  dv=0, k=1)
        addAttr(joints_[1:][i],ln="SquashScaleZ", at='double',  dv=0, k=1)
        dict_['md2'][i].oy >> joints_[1:][i].SquashScaleY
        dict_['md2'][i].oz >> joints_[1:][i].SquashScaleZ
    
    dict_['stml'].attr('i1').set(10)
    dict_['stml'].attr('i2').set(0.1)
    dict_['sqml'].attr('i1').set(10)
    dict_['sqml'].attr('i2').set(0.1)

  
def IKJntStretch(object_):
    name_ = object_[0].split('Jnt')[0].replace('1','')
    stJnt, enJnt, = object_[0], object_[-1]
    joints_ = searchJoint(stJnt, enJnt)
    names_ = [jnt.name().split('Jnt')[0].replace('1','') for jnt in joints_]
    number = int(len(joints_))
    divNumList = division(number-1)
    crvs_ = [object_cv_curve(n, joints_) for n in [name_, '{0}Chk'.format(name_)]]
    nodeDict_ = createNodes(name_, names_, crvs_, divNumList)
    IKNodeConnection(nodeDict_, joints_, divNumList)
    [parent(crv, nodeDict_['SysGrp']) for crv in crvs_]
   
    return (crvs_[0],joints_)
    


# 으아ㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏ

# 첫번째와 마지막 조인트 잡고 실행해주세요
sel = ls(sl=1,r=1,fl=1)
tt=IKStretch(sel)