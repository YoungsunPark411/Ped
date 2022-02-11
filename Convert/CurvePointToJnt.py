import pymel.core as pm


def CurvePoint(Curve):
    shape_ = Curve.getShape()
    shape_List= shape_.getCVs()
    posList=[]
    for x in range(len(shape_List)):
        posList.append(x)
    return posList


def CurvePointToJnt(Curve):
    shape_ = Curve.getShape()
    jointPosition= shape_.getCVs()
    jointList=[]
    i=0
    pm.select(cl=1)
    for x in jointPosition:
        i+=1
        createName='%s%sJnt'%(Curve.replace('_Curve',''),i)
        jointList.append(createName)
        pm.joint(p=x,n=createName)

    if jointList:
        pm.parent(jointList[0],w=1)
        pm.makeIdentity (apply=1,t =0,r= 1 ,s =0 ,n =0 ,pn= 1)
        pm.joint(e=1  ,oj ='xzy' ,secondaryAxisOrient= 'zdown',ch =1 ,zso=1)
        pm.setAttr ("%s.jointOrientX"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientY"%jointList[-1], 0)
        pm.setAttr ("%s.jointOrientZ"%jointList[-1], 0)
    pm.select(jointList)

    return jointList

    
# curveList=pm.ls(sl=1)
# for x in curveList:
#     print(x)
#     CurvePointToJnt(x)