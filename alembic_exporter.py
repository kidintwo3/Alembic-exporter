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
