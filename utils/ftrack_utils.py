__author__ = 'Natasha'

import ftrack
import ftrack_api
import os
import shlex
import subprocess
import json


def startASession():
    session = ftrack_api.session.Session()
    return session


def getTaskPath(session, taskid):
    item = session.query('Task where id is %s' % taskid).one()
    taskPath = ''
    while True:
        taskPath = item['name'] + taskPath
        item = item['parent']
        if not item:
            break
        taskPath = ' / ' + taskPath
    return taskPath


def getAllProjectNames(session):
    projects = session.query('Project').all()
    projList = [proj['name'] for proj in projects]
    projList.sort()
    return projList


def getProject(session, projName):
    project = session.query('Project where name is "%s"' % projName).one()
    return project


def getNode(session, nodePath):
    nodes = nodePath.split(' / ')
    parent = getProject(session, nodes[0])
    nodes = nodes[1:]
    if nodes:
        for node in nodes:
            for child in parent['children']:
                if child['name'] == node.strip():
                    parent = child
                    break
    return parent


def getTask(session, projPath):
    parent = getNode(session, projPath)
    taskName = projPath.split(' / ')[-1]
    task = session.query('Task where parent.id is %s and name is %s' % (parent['parent']['id'], taskName)).one()
    return task


def isTask(session, taskPath):
    task = getTask(session, taskPath)
    if task['object_type']['name'] == 'Task':
        return True
    else:
        return False


def getAllChildren(session, projPath):
    parent = getNode(session, projPath)
    children = parent['children']
    childList = []
    for child in children:
        if child['name'] == 'Asset builds' or child['object_type']['name'] == 'Asset Build':
            childList.append(('assetbuild', child['name']))
        elif child['object_type']['name'] == 'Episode':
            childList.append(('episode', child['name']))
        elif child['object_type']['name'] == 'Sequence':
            childList.append(('sequence', child['name']))
        elif child['object_type']['name'] == 'Shot':
            childList.append(('shot', child['name']))
        elif child['object_type']['name'] == 'Folder':
            childList.append(('folder', child['name']))
        else:
            childList.append(('task', child['name']))
    return childList


def getAllAssets(session, projPath):
    parent = getNode(session, projPath)
    assets = session.query('Asset where parent.name is "%s"' % parent['parent']['name'])
    assetList = [asset['name'] for asset in assets]
    return assetList


def getAllStatuses(session, projPath):
    projectName = projPath.split(' / ')[0]
    project = getProject(session, projectName)
    task = getTask(session, projPath)
    projectSchema = project['project_schema']
    statuses = projectSchema.get_statuses('Task', task['type']['id'])
    return statuses


def getStatusList(session, projPath):
    statuses = getAllStatuses(session, projPath)
    statusList = [status['name'] for status in statuses]
    return statusList


def getCurrentStatus(session, projPath):
    task = getTask(session, projPath)
    status = task['status']['name']
    return status


def convertToJpg(inputFile, outfilejpg):
    jpgcmd = 'convert.exe %s %s' % (inputFile, outfilejpg)
    args = shlex.split(jpgcmd)
    result = subprocess.call(args, shell=True)
    return result


def convertMp4Files(inputFile, outfilemp4):
    mp4cmd = 'ffmpeg -y -i "%s" -ac 2 -b:v 2000k -c:a aac -c:v libx264 ' \
             '-pix_fmt yuv420p -g 30 -vf scale="trunc((a*oh)/2)*2:720" ' \
             '-b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 "%s"' % (inputFile, outfilemp4)
    args = shlex.split(mp4cmd)
    result = subprocess.call(args, shell=True)
    return result


def convertWebmFiles(inputFile, outfilewebm):
    webmcmd = 'ffmpeg -y -i "%s" -qscale:a 6 -g 30 -ac 2 -c:a libvorbis ' \
              '-c:v libvpx -pix_fmt yuv420p -b:v 2000k -vf scale="trunc((a*oh)/2)*2:720" ' \
              '-crf 5 -qmin 0 -qmax 50 -f webm "%s"' % (inputFile, outfilewebm)
    args = shlex.split(webmcmd)
    result = subprocess.call(args, shell=True)
    return result


def createThumbnail(inputFile, outputFile):
    cmd = 'ffmpeg -y -i "%s" -vf  "thumbnail,scale=640:360" -frames:v 1 "%s"' % (inputFile, outputFile)
    args = shlex.split(cmd)
    result = subprocess.call(args, shell=True)
    return result


def getAsset(session, filePath, assetName):
    task = getTask(session, filePath)
    assetType = session.query('AssetType where name is Upload').one()
    try:
        asset = session.query('Asset where name is "%s" and parent.name is "%s"' %
                              (assetName, task['parent']['name'])).one()
    except:
        asset = session.create('Asset', {
            'name': assetName,
            'parent': task['parent'],
            'type': assetType
        })
        session.commit()
    return asset


def createAttachment(session, version, name, outfile, framein, frameout, framerate):
    server_location = session.query('Location where name is "ftrack.server"').one()
    component = version.create_component(
        path=outfile,
        data={
            'name': name
        },
        location=server_location
    )
    component['metadata']['ftr_meta'] = json.dumps({
        'frameIn': framein,
        'frameOut': frameout,
        'frameRate': framerate
    })
    component.session.commit()

def createVersion(session, filePath, asset, comment):
    task = getTask(session, filePath)
    status = task['status']
    version = session.create('AssetVersion', {
        'asset': asset,
        'status': status,
        'comment': comment,
        'task': task
    })
    return task, version


def addMetadata(session, version, metadict):
    for key in metadict.keys():
        version['metadata'][key] = metadict[key]
    session.commit()


def createAndPublishVersion(session, filePath, comment, asset, outfilemp4, outfilewebm, thumbnail, framein, frameout, framerate):
    task, version = createVersion(session, filePath, asset, comment)
    createAttachment(session, version, 'ftrackreview-mp4', outfilemp4, framein, frameout, framerate)
    createAttachment(session, version, 'ftrackreview-webm', outfilewebm, framein, frameout, framerate)
    session.commit()
    if os.path.exists(thumbnail):
        attachThumbnail(thumbnail, task, asset, version)
    return version


def publishImage(session, filePath, comment, asset, outfilejpg):
    task, version = createVersion(session, filePath, asset, comment)
    server_location = session.query('Location where name is "ftrack.server"').one()
    component = version.create_component(
        path=outfilejpg,
        data={
            'name': 'ftrackreview-image'
        },
        location=server_location
    )
    component['metadata']['ftr_meta'] = json.dumps({
        'format': 'image'
    })
    component.session.commit()
    attachThumbnail(outfilejpg, task, asset, version)
    return version


def attachThumbnail(thumbnail, task, asset, version):
    # Currently, it is not possible to set thumbnails using new API
    # This is a workaround using the old API.
    task_old_api = ftrack.Task(id=task['id'])
    asset_old_api = ftrack.Asset(id=asset['id'])
    for vers in asset_old_api.getVersions():
        if vers.getId() == version['id']:
            version_old_api = vers
            attachment = version_old_api.createThumbnail(thumbnail)
            task_old_api.setThumbnail(attachment)
            break


def getStatus(session, statusName):
    status = session.query('Status where name is "%s"'  % statusName).one()
    return status


def setTaskStatus(session, filePath, version, statusName):
    task = getTask(session, filePath)
    status = getStatus(session, statusName)
    task['status'] = status
    version['status'] = status
    session.commit()


def getProjectFromShot(session, id):
    project = session.query('Project where descendants.id is %s' % id).one()
    return project['name']


def getProjectName(session, taskPath):
    task = getTask(session, taskPath)
    projectName = getProjectFromShot(session, task['id'])
    return projectName


def checkLogname(session, username):
    try:
        os.environ['LOGNAME']= username
        user = session.query('User where username is "%s' % username)
        return True
    except:
        return False