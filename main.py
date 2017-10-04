import tank
import alembic
import imath
import maya.cmds as cmds

asset_list = ['mill_model1', 'ruin_F_model7']
asset_size = len(asset_list)


# Store asset ids
assetID_A = []

for x in asset_list:
    ass_path = cmds.getAttr(x + '.definition')

    tk_ref = tank.tank_from_path(ass_path)
    context_ref = tk_ref.context_from_path(ass_path)

    if context_ref:
        if context_ref.entity:
            if context_ref.entity.get('id'):
                assetID_A.append(context_ref.entity.get('id'))

                # print context_ref.entity.get('id')

if len(assetID_A) == asset_size:

    # Set export options
    arch = alembic.Abc.OArchive("d:/delete.abc")

    root = arch.getTop()
    fps = 24.0
    start_frame = 1
    end_frame = 5
    timesamp = alembic.AbcCoreAbstract.TimeSampling(1.0 / fps, start_frame / fps)
    index = arch.addTimeSampling(timesamp)
    opoints = alembic.AbcGeom.OPoints(root, "position_cache", index)

    # # Export Extra
    # myCrazyDataContainer = opoints.getSchema().getUserProperties()
    #
    # # Export Shotgun IDs
    # prop_sg_id = alembic.Abc.OUInt64ArrayProperty(myCrazyDataContainer, "sg_id")
    # # Export Rotation
    # prop_rot = alembic.Abc.OV3fArrayProperty(myCrazyDataContainer, "rotation")
    # # Export Rotation
    # prop_scale = alembic.Abc.OV3fArrayProperty(myCrazyDataContainer, "scale")

    for i in range(start_frame, end_frame):
        opoints_sample = alembic.AbcGeom.OPointsSchemaSample()

        idA = imath.IntArray(asset_size)
        sg_idA = imath.IntArray(asset_size)
        posA = imath.V3fArray(asset_size)
        rotA = imath.V3fArray(asset_size)
        sclA = imath.V3fArray(asset_size)

        for y in range(asset_size):

            tr = cmds.xform(asset_list[y], query=True, translation=True)
            rot = cmds.xform(asset_list[y], query=True, rotation=True)
            scl = cmds.xform(asset_list[y], query=True, r=True, scale=True)

            idA[y] = y
            sg_idA[y] = assetID_A[y]
            posA[y] = imath.V3f(tr[0], tr[1], tr[2])
            rotA[y] = imath.V3f(rot[0], rot[1], rot[2])
            sclA[y] = imath.V3f(scl[0], scl[1], scl[2])

        opoints_sample.setPositions(posA)
        opoints_sample.setIds(idA)
        opoints.getSchema().set(opoints_sample)

        # prop_sg_id.setValue(sg_idA)
        # prop_rot.setValue(rotA)
        # prop_scale.setValue(sclA)







# Ez mukodik nemtom miert

def save_test_alembic(path):
    arch = alembic.Abc.OArchive(path)

    root = arch.getTop()
    fps = 24.0
    start_frame = 1
    end_frame = 5
    timesamp = alembic.AbcCoreAbstract.TimeSampling(1.0 / fps, start_frame / fps)
    index = arch.addTimeSampling(timesamp)
    opoints = alembic.AbcGeom.OPoints(root, "position_cache", index)

    for i in range(start_frame, end_frame):
        opoints_sample = alembic.AbcGeom.OPointsSchemaSample()
        points = imath.V3fArray(40)
        ids = imath.IntArray(40)
        for y in range(40):
            points[y] = imath.V3f(y * 0.01, (y + i) * 0.01, y * 0.01)
            ids[y] = y
        opoints_sample.setPositions(points)
        opoints_sample.setIds(ids)
        opoints.getSchema().set(opoints_sample)


# save_test_alembic(path='d:/delete.abc')