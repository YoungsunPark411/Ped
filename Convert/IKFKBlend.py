from pymel.core import *

def getChildren_(object_, type_=None):
    """Get the childrens from top object

    Arguments:
        object_ (node): transform node
        type_ (type): node type

    Returns:
        list : childrens list

    """
    object_ = PyNode(object_)
    if not type_:
        type_ = 'transform'
    child_ = object_.listRelatives(ad=1, c=1, typ=type_)
    child_ = child_ + [object_]
    child_.reverse()
    return child_

def IKFKBlend(object_):

    FKChain = getChildren_(object_[0], type_='joint')

    IKChain = getChildren_(object_[1], type_='joint')

    DrvChain = getChildren_(object_[2], type_='joint')
    switch = object_[-1]
    
    OrigChain =getChildren_(object_[3], type_='joint')
    
    for i,drv in enumerate(DrvChain):
        name_ = drv.name()
        #print(name_, FKChain[i], IKChain[i])
        PB_ = createNode('pairBlend', n='{0}PB'.format(name_))
        BC_ = shadingNode('blendColors', au=1, n='{0}BC'.format(name_))
        FKChain[i].r >> PB_.ir2
        FKChain[i].t >> PB_.it2
        FKChain[i].s >> BC_.color1
        IKChain[i].r >> PB_.ir1
        IKChain[i].t >> PB_.it1
        IKChain[i].SquashScaleY >> BC_.color2G
        IKChain[i].SquashScaleZ >> BC_.color2B

        PB_.outTranslate >> drv.t
        PB_.outRotate >> drv.r
        BC_.output >> OrigChain[i].s

        switch.IKFK>>BC_.blender
        switch.IKFK >> PB_.weight

    return [PB_,BC_]




'''
# 첫번째 FK 최상위 조인트, IK 최상위 조인트, Drv 최상위 조인트, IKFK 스위치 선택후 실행해주세요
sel = ls(sl=1,r=1,fl=1)
IKFKBlend(sel)
sel = ls(sl=1)[0]
Chain = getChildren_(sel, type_='joint')

'''

