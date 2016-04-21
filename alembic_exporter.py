"""
alembic_exporter @ export

Utility functions for exporting Alembic to Clarisse

    example:

    objectA = ['pCube1', 'pCylinder1']
    fileName = "/Users/hunyadijanos/Desktop/alembic/test.abc"
    export_alembic(objs=objectA, fileName=fileName, uvWrite=True)

"""

import maya.OpenMayaAnim as oma
import maya.OpenMaya as om
import maya.cmds as cmds


def get_mdagpath(nodeName):
    """

    Get the dagpath from the node name

    :param nodeName: str, name of the node to find dagPath
    :return: str, full dagPath string
    """

    selList = om.MSelectionList()
    selList.add(nodeName)
    mDagPath = om.MDagPath()
    selList.getDagPath(0, mDagPath)

    return mDagPath


def export_alembic(objs=None,
                   fileName=None,
                   minTime=None,
                   maxTime=None,
                   uvWrite=True):
    """

    Function to export object to Clarisse

    :param objs: str (list), Name of the nodes that need to be exported
    :param fileName: str, full file path
    :param minTime: int, start frame for the export
    :param maxTime: int, end frame for the export
    :param uvWrite: bool, export UVs flag
    :return:
    """

    anim = oma.MAnimControl()

    if minTime is None:
        minTime = anim.minTime().value()

    if maxTime is None:
        maxTime = anim.maxTime().value()

    if objs is None:
        cmds.warning("[Alembic exporter] No objects set for export")
        return
    if fileName is None:
        cmds.warning("[Alembic exporter] No filename set for export")
        return

    exportString = ""

    for node in objs:
        exportString += '-root %(dagPath)s ' % {"dagPath": get_mdagpath(node).fullPathName()}

    if uvWrite:
        exportString += "-uvWrite "

    exportString += '-renderableOnly -stripNamespaces -frameRange %(minTime)i %(maxTime)i -file %(fileName)s' \
                    % {"minTime": minTime, "maxTime": maxTime, "fileName": fileName}

    cmds.AbcExport(j=exportString)


def bake_camera(camRig_group=None):
    """

    :param source_camera_loc:
    :param source_camera_tr:
    :return: str, baked camera transform
    """

    if camRig_group is None:
        cmds.warning("[Alembic exporter] No cameraRig found")
        return

    source_camera_loc = None
    source_camera_tr = None

    if camRig_group:
        if cmds.nodeType(camRig_group, api=True) == 'kPluginTransformNode':
            childNodes = cmds.listRelatives(camRig_group, ad=True)

            for node in childNodes:
                if cmds.nodeType(node) == 'ccCamLocController':
                    source_camera_loc = node
                if cmds.nodeType(node) == 'camera':
                    source_camera_tr = cmds.listRelatives(node, p=True)

    if source_camera_loc is None:
        cmds.warning("[Alembic exporter] No camera Controller not found")
        return
    if source_camera_tr is None:
        cmds.warning("[Alembic exporter] No camera found")
        return

    source_camera_sh = cmds.listRelatives(source_camera_tr, ad=True, s=True)[0]

    #
    source_camera_loc_size = cmds.getAttr(source_camera_loc + '.cameraRadius')

    export_camera = cmds.camera()
    export_camera_tr = export_camera[0]
    export_camera_sh = export_camera[1]

    cmds.setAttr(export_camera_sh + '.locatorScale', source_camera_loc_size * 0.5)

    currTime = cmds.currentTime(query=True)

    for i in xrange(1, 120):
        cmds.currentTime(i)

        v_focall = cmds.getAttr(source_camera_sh + '.focalLength')
        v_filmroll = cmds.getAttr(source_camera_sh + '.filmRollValue')

        v_t = cmds.xform(source_camera_tr, query=True, t=True, ws=True, r=True)
        v_r = cmds.xform(source_camera_tr, query=True, ro=True, ws=True, r=True)

        cmds.setKeyframe(export_camera_sh, t=i, v=v_focall, at='.focalLength')
        cmds.setKeyframe(export_camera_sh, t=i, v=v_filmroll, at='.filmRollValue')

        cmds.setKeyframe(export_camera_tr, t=i, v=v_t[0], at='.tx')
        cmds.setKeyframe(export_camera_tr, t=i, v=v_t[1], at='.ty')
        cmds.setKeyframe(export_camera_tr, t=i, v=v_t[2], at='.tz')

        cmds.setKeyframe(export_camera_tr, t=i, v=v_r[0], at='.rx')
        cmds.setKeyframe(export_camera_tr, t=i, v=v_r[1], at='.ry')
        cmds.setKeyframe(export_camera_tr, t=i, v=v_r[2], at='.rz')

    cmds.currentTime(currTime)

    return export_camera_tr


def scale_export_grp(obj=None):
    """

    :param obj:
    :return:
    """

    if obj is None:
        obj = cmds.ls(sl=True, tr=True)

    if len(obj) == 0:
        return

    obj = cmds.ls(sl=True, tr=True)
    scaleGrp = cmds.group(obj[0], n='tmp_resize_grp')
    cmds.xform(scaleGrp, ztp=True)

    cmds.setAttr(scaleGrp + '.scaleX', 0.01)
    cmds.setAttr(scaleGrp + '.scaleY', 0.01)
    cmds.setAttr(scaleGrp + '.scaleZ', 0.01)
