import tank
import alembic
import imath
import math
import maya.cmds as cmds
import maya.OpenMaya as om

def euler_to_quat(rot):
    """
    Converts euler to quaternion
    :param rot:
    :return:
    """

    # This is our rotation order
    rotOrder = om.MEulerRotation.kXYZ

    # Create the MEulerRotation
    euler = om.MEulerRotation(math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]), rotOrder)

    # Get the quaternion equivalent
    quaternion = euler.asQuaternion()

    # Access the components
    return [quaternion.x, quaternion.y, quaternion.z, quaternion.w]

def get_idA(objA=[]):
    """
    Store asset ids
    :return:
    """

    assetID_A = []

    for x in objA:
        ass_path = cmds.getAttr(x + '.definition')

        tk_ref = tank.tank_from_path(ass_path)
        context_ref = tk_ref.context_from_path(ass_path)

        if context_ref:
            if context_ref.entity:
                if context_ref.entity.get('id'):
                    assetID_A.append(int(context_ref.entity.get('id')))

    return assetID_A


def save_pos_cache(path=None, start_frame=0, end_frame=1, fps=24.0, objA=[]):
    """

    :param path:
    :param objA:
    :return:
    """

    if not objA:
        return

    idA = get_idA(objA=objA)
    # print idA

    if not idA:
        return

    if len(objA) != len(idA):
        return

    cmds.currentTime(start_frame, update=True)

    arch = alembic.Abc.OArchive(path)

    root = arch.getTop()

    timesamp = alembic.AbcCoreAbstract.TimeSampling(1.0 / fps, start_frame / fps)

    # print timesamp

    index = arch.addTimeSampling(timesamp)
    opoints = alembic.AbcGeom.OPoints(root, "position_cache", index)

    # Export Extra
    myCrazyDataContainer = opoints.getSchema().getArbGeomParams()


    # Export Shotgun IDs
    prop_sg_id = alembic.Abc.OUInt64ArrayProperty(myCrazyDataContainer, "sg_id")
    # Export Rotation
    prop_rot = alembic.Abc.OQuatfArrayProperty(myCrazyDataContainer, "rotation")
    # Export Scale
    prop_scale = alembic.Abc.OV3fArrayProperty(myCrazyDataContainer, "scale")

    prop_rot.setTimeSampling(timesamp)
    prop_scale.setTimeSampling(timesamp)

    for i in range(start_frame, end_frame + 1):

        sg_idA = imath.IntArray(len(objA))
        posA = imath.V3fArray(len(objA))
        rotA = imath.QuatfArray(len(objA))
        sclA = imath.V3fArray(len(objA))

        cmds.currentTime(i, update=True)
        opoints_sample = alembic.AbcGeom.OPointsSchemaSample()
        ids = imath.IntArray(len(objA))

        for y in range(0, len(objA)):
            ids[y] = y

            tr = cmds.xform(objA[y], query=True, translation=True)
            rt = cmds.xform(objA[y], query=True, rotation=True)
            scl = cmds.xform(objA[y], query=True, r=True, scale=True)


            quat = euler_to_quat(rt)

            sg_idA[y] = idA[y]
            posA[y] = imath.V3f(tr[0], tr[1], tr[2])

            rotA[y] = imath.Quatf(quat[0], quat[1], quat[2], quat[3])
            sclA[y] = imath.V3f(scl[0], scl[1], scl[2])

            # print sclA[y]



        opoints_sample.setPositions(posA)
        opoints_sample.setIds(ids)
        opoints.getSchema().set(opoints_sample)



        prop_sg_id.setValue(sg_idA)
        prop_rot.setValue(rotA)
        prop_scale.setValue(sclA)

    arch = None
    del arch

    print 'Done...'


objA = ['mill_model1', 'ruin_F_model7']
save_pos_cache(path="d:/delete.abc", objA=objA, start_frame=1000, end_frame=1132)
