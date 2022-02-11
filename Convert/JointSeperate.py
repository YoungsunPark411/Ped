import pymel.core as pm


def sel_():
    return pm.ls(sl=1, r=1)

def getChildren_(object_, type_=None):
    """Get the childrens from top object

    Arguments:
        object_ (node): transform node
        type_ (type): node type

    Returns:
        list : childrens list

    """
    object_ = pm.PyNode(object_)
    if not type_:
        type_ = 'transform'
    child_ = object_.listRelatives(ad=1, c=1, typ=type_)
    child_ = child_ + [object_]
    child_.reverse()
    return child_

def get_trans(object_):
    return object_.getMatrix(worldSpace=True)[-1][:-1]

def length(v0, v1):
    v = v1 - v0
    return v.length()

def space_(name_, parent_=None):
    space_ = pm.createNode('transform',
                        n='{}GRP'.format(name_),
                        p=parent_)
    return space_

def joint_insert( joint_, name_, pos_):
    if joint_.type() == 'joint':
        JNT = joint_.insert()
        pm.joint(JNT, n=name_, e=True, co=True, p=pos_)
        return pm.PyNode(name_)

def linear_spacing_joint(joint_, num, axis='x'):
    joints = [joint_, joint_.getChildren()[0]]
    stJoint = joints[0]
    stOtherType = stJoint.getAttr('otherType')
    stSide = stJoint.getAttr('side')
    enJoint = joints[-1]
    stTrans_ = get_trans(stJoint)
    enTrans_ = get_trans(enJoint)
    length_ = length(stTrans_, enTrans_)
    divValue = length_ / (num + 1)

    if axis:
        if axis == 'x':
            value = (divValue, 0, 0)
        if axis == 'y':
            value = (0, divValue, 0)
        if axis == 'z':
            value = (0, 0, divValue)
        if axis == '-x':
            value = (-1 * divValue, 0, 0)
        if axis == '-y':
            value = (0, -1 * divValue, 0)
        if axis == '-z':
            value = (0, 0, -1 * divValue)
    else:
        value = (divValue, 0, 0)

    segJntList=[]
    insertList = [stJoint]
    for i in range(num):
        localspace = space_(stJoint.name(), parent_=insertList[i])
        localspace.setAttr('t', value)
        name_ = '{0}{1}{2}{3}'.format(stJoint.name(),'_', i + 1, 'Jnt')
        pos_ = get_trans(localspace)
        JNT = joint_insert(insertList[i], name_, pos_)
        JNT.attr('type').set(18)
        JNT.attr('otherType').set('{0}{1}'.format(stOtherType, i + 1))
        JNT.attr('side').set(stSide)
        pm.delete(localspace)
        insertList.append(JNT)
        segJntList.append(JNT)
        
    return segJntList


def linearSpacingJoint(num_,axis):

    for i in sel_():
        segJnt=linear_spacing_joint(i,
                                  num_,
                                  axis
                                  )

    return segJnt


yy=linearSpacingJoint(3,'x')

