__author__ = 'natasha'

import os
import PySide.QtGui as QtGui
from PySide.QtCore import Qt
import threading
from utils import ftrack_utils
from PySide.QtCore import Signal
#from utils import screenshot

iconPath = 'P:\\dev\\ftrack-connect-package\\resource\\ftrack_connect_nuke\\nuke_path\\NukeProResPlugin'


class BrowserDialog(QtGui.QDialog):

    winClosed = Signal(str)

    def __init__(self, taskPath, parent=None, session=None):
        QtGui.QDialog.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        self.taskPath = taskPath
        viewerBox = QtGui.QGroupBox('Ftrack')
        self.layout().addWidget(viewerBox)
        vLayout = QtGui.QVBoxLayout()
        viewerBox.setLayout(vLayout)

        projList = QtGui.QListWidget()
        self.createProjList(session, projList)
        projList.itemClicked.connect(lambda: self.projItemClicked(session, projList.currentItem()))
        self.taskList = QtGui.QListWidget()
        self.taskList.itemClicked.connect(lambda: self.taskItemClicked(session, self.taskList.currentItem()))
        hLayout1 = QtGui.QHBoxLayout()
        hLayout1.addWidget(projList)
        hLayout1.addWidget(self.taskList)
        vLayout.addLayout(hLayout1)
        self.pathEdit = QtGui.QLineEdit()
        vLayout.addWidget(self.pathEdit)

        self.setButton = QtGui.QPushButton('Set')
        self.setButton.setDisabled(True)
        cancelButton = QtGui.QPushButton('Cancel')
        self.setButton.clicked.connect(self.setTaskPath)
        cancelButton.clicked.connect(self.closeWindow)
        hLayout2 = QtGui.QHBoxLayout()
        hLayout2.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        hLayout2.addWidget(self.setButton)
        hLayout2.addWidget(cancelButton)
        vLayout.addLayout(hLayout2)
        self.projPath = ''
        if not self.taskPath == '':
            self.pathEdit.setText(self.taskPath)
            self.createTaskList(session, self.taskPath)
            if ftrack_utils.isTask(session, taskPath):
                self.setProjPath(session)

    def createProjList(self, session, projList):
        projects = ftrack_utils.getAllProjectNames(session)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("%s\\PNG\\home.png" % iconPath))
        for project in projects:
            item = QtGui.QListWidgetItem(icon, project)
            projList.addItem(item)

    def projItemClicked(self, session, item):
        self.projPath = ''
        self.pathEdit.setText(str(item.text()))
        self.createTaskList(session, str(item.text()))
        self.setButton.setDisabled(True)

    def isAllTasks(self):
        for type, name in self.childList:
            if not type == 'task':
                return False
        return True

    def setProjPath(self, session):
        if self.isAllTasks():
            self.setButton.setDisabled(False)
            if self.projPath == '':
                tmpPath = str(self.pathEdit.text())
                self.projPath = tmpPath.split(' / ')[0]
                for p in tmpPath.split(' / ')[1:-1]:
                    self.projPath = '%s / %s' % (self.projPath, p)
                self.createTaskList(session, self.projPath)

    def taskItemClicked(self, session, item):
        pathtext = str(self.pathEdit.text())
        projPath = '%s / %s' % (pathtext, str(item.text()))
        if self.isAllTasks():
            if self.projPath == '':
                self.projPath = str(self.pathEdit.text())
            projPath = '%s / %s' % (self.projPath, str(item.text()))
            self.setButton.setDisabled(False)
        self.pathEdit.setText(projPath)
        self.createTaskList(session, projPath)

    def createTaskList(self, session, projPath):
        self.childList = ftrack_utils.getAllChildren(session, projPath)
        if not len(self.childList) == 0:
            self.taskList.clear()
            for type, name in self.childList:
                if type == 'assetbuild':
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap("%s\\PNG\\box.png" % iconPath))
                    item = QtGui.QListWidgetItem(icon, name)
                elif type == 'task':
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap("%s\\PNG\\signup.png" % iconPath))
                    item = QtGui.QListWidgetItem(icon, name)
                elif type == 'sequence':
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap("%s\\PNG\\movie.png" % iconPath))
                    item = QtGui.QListWidgetItem(icon, name)
                elif type == 'folder':
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap("%s\\PNG\\folder-open.png" % iconPath))
                    item = QtGui.QListWidgetItem(icon, name)
                else:
                    item = QtGui.QListWidgetItem(name)
                self.taskList.addItem(item)

    def setTaskPath(self):
        self.winClosed.emit(self.getTaskPath())
        self.close()

    def getTaskPath(self):
        return str(self.pathEdit.text())

    def closeWindow(self):
        self.close()


class MyLabel(QtGui.QLabel):
    def paintEvent( self, event ):
        painter = QtGui.QPainter(self)

        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideMiddle, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)


class PublishWidget(QtGui.QDialog):

    uploadComplete = Signal(str)
    pubClosed = Signal(str)
    screenshot = Signal(str)

    def __init__(self, parent=None, filename=None):
        QtGui.QDialog.__init__(self, parent)
        self.setLayout(QtGui.QGridLayout())
        self.filename = filename
        self.frameIn = 0
        self.frameOut = 150
        frameBox = QtGui.QWidget()
        frameLayout = QtGui.QGridLayout()
        frameBox.setLayout(frameLayout)
        frameBox.setMaximumSize(500, 350)
        frameLayout.addWidget(QtGui.QLabel('Media:'))
        frameLayout.addWidget(QtGui.QLabel('Link To:'), 1, 0)
        self.mediaList = QtGui.QListWidget()
        frameLayout.addWidget(self.mediaList, 0, 1)
        vlayout = QtGui.QVBoxLayout()
        addButton = QtGui.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("%s\\PNG\\plus.png" % iconPath))
        addButton.setIcon(icon)
        addButton.clicked.connect(lambda: self.addMedia(self.mediaList))
        vlayout.addWidget(addButton)
        removeButton = QtGui.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("%s\\PNG\\remove.png" % iconPath))
        removeButton.setIcon(icon)
        removeButton.clicked.connect(self.removeMedia)
        vlayout.addWidget(removeButton)
        vlayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        frameLayout.addLayout(vlayout, 0, 2)
        if os.environ.has_key('FTRACK_TASKID'):
            taskid = os.environ['FTRACK_TASKID']
        else:
            taskid = None
        taskPath = ''
        session = ftrack_utils.startASession()
        if taskid:
            taskPath = ftrack_utils.getTaskPath(session, taskid)
        self.taskEdit = QtGui.QLineEdit(taskPath)
        self.taskEdit.setReadOnly(True)
        frameLayout.addWidget(self.taskEdit, 1, 1)
        self.taskEdit.textChanged.connect(lambda: self.updateAssetDrop(session))
        self.browseButton = QtGui.QPushButton('Browse')
        self.browseButton.clicked.connect(lambda: self.openBrowserDialog(session))
        frameLayout.addWidget(self.browseButton, 1, 2)

        frameLayout.addWidget(QtGui.QLabel('Assets:'), 2, 0)
        hlayout = QtGui.QHBoxLayout()
        self.assetDrop = QtGui.QComboBox()
        self.assetDrop.addItem('Select')
        self.assetDrop.addItem('new')
        self.assetDrop.setMinimumWidth(100)
        self.assetDrop.activated[str].connect(self.assetSelected)
        hlayout.addWidget(self.assetDrop)
        hlayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        frameLayout.addLayout(hlayout, 2, 1)

        frameLayout.addWidget(QtGui.QLabel('Asset Name:'), 3, 0)
        self.assetEdit = QtGui.QLineEdit()
        self.assetEdit.setDisabled(True)
        frameLayout.addWidget(self.assetEdit)

        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(QtGui.QLabel('Comment'))
        vLayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        frameLayout.addLayout(vLayout, 4, 0)
        self.commentBox = QtGui.QTextEdit()
        frameLayout.addWidget(self.commentBox, 4, 1)

        frameLayout.addWidget(QtGui.QLabel('Status:'), 5, 0)
        hlayout1 = QtGui.QHBoxLayout()
        self.statusDrop = QtGui.QComboBox()
        self.statusDrop.setMinimumWidth(100)
        hlayout1.addWidget(self.statusDrop)
        hlayout1.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        frameLayout.addLayout(hlayout1, 5, 1)
        self.framerate = '24'

        frameLayout.addWidget(QtGui.QLabel('Thumbnail:'), 6, 0)
        self.thumbnailEdit = QtGui.QLineEdit()
        frameLayout.addWidget(self.thumbnailEdit, 6, 1)
        thumbBrowse = QtGui.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("%s\\PNG\\folder-open.png" % iconPath))
        thumbBrowse.setIcon(icon)
        thumbBrowse.clicked.connect(lambda: self.addMedia(self.thumbnailEdit))
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(thumbBrowse)
        screenshotButton = QtGui.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("%s\\PNG\\tv.png" % iconPath))
        screenshotButton.setIcon(icon)
        screenshotButton.clicked.connect(self.takeScreenshot)
        hlayout.addWidget(screenshotButton)
        hlayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        frameLayout.addLayout(hlayout, 6, 2)

        self.uploadButton = QtGui.QPushButton('Publish')
        self.uploadButton.setDisabled(True)
        self.uploadButton.clicked.connect(lambda: self.publishMedia(session))
        frameLayout.addWidget(self.uploadButton, 7, 0)
        self.layout().addWidget(frameBox)
        self.layout().addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding), 1, 0)
        if not taskPath == '':
            self.updateAssetDrop(session)

    def addMedia(self, widget):
        dialog = QtGui.QFileDialog()
        filename, state = dialog.getOpenFileName(self, "Select Media",
                                                 options=QtGui.QFileDialog.DontUseNativeDialog)
        if type(widget) == QtGui.QListWidget:
            widget.addItem(str(filename))
        elif type(widget) == QtGui.QLineEdit:
            widget.setText(str(filename))

    def removeMedia(self):
        selection = self.mediaList.selectedItems()
        if selection:
            selected = selection[0]
            row = self.mediaList.row(selected)
            self.mediaList.takeItem(row)

    def takeScreenshot(self):
        #app = screenshot.ScreenShot(0)
        #app.MainLoop()
        import uuid
        fileName = os.path.join(os.environ['TEMP'], str(uuid.uuid4()) + '.jpg')
        self.thumbnailEdit.setText(fileName)
        self.screenshot.emit(fileName)

    def setFrameCount(self, framein, frameout):
        self.frameIn = framein
        self.frameOut = frameout

    def setFrameRate(self, framerate):
        self.framerate = framerate

    def setMoviePath(self, moviePath):
        self.movieLabel.setText(str(moviePath))

    def setPath(self, newPath):
        self.taskEdit.setText(newPath)

    def assetSelected(self, assetName):
        if assetName == 'Select':
            self.assetEdit.setDisabled(True)
            self.uploadButton.setEnabled(False)
        elif assetName == 'new' :
            self.assetEdit.setDisabled(False)
            self.assetEdit.textChanged.connect(self.enableUploadButton)
        else:
            self.assetEdit.setDisabled(True)
            self.enableUploadButton()

    def updateAssetDrop(self, session):
        newPath = str(self.taskEdit.text())
        self.assetDrop.clear()
        self.assetDrop.addItem('Select')
        self.assetDrop.addItem('new')
        self.assetEdit.setDisabled(False)
        assetList = ftrack_utils.getAllAssets(session, newPath)
        self.assetDrop.addItems(assetList)
        self.updateStatusDrop(session, newPath)

    def updateStatusDrop(self, session, projectPath):
        statusList = ftrack_utils.getStatusList(session, projectPath)
        self.statusDrop.clear()
        self.statusDrop.addItems(statusList)
        currentStatus = ftrack_utils.getCurrentStatus(session, projectPath)
        self.statusDrop.setCurrentIndex(statusList.index(currentStatus))

    def openBrowserDialog(self, session):
        taskpath = str(self.taskEdit.text())
        self.gui = BrowserDialog(taskpath, parent=self, session=session)
        self.gui.show()
        self.gui.winClosed.connect(self.setPath)

    def enableUploadButton(self):
        self.uploadButton.setEnabled(True)

    def getAllMediaItems(self):
        mediaItems = []
        for index in range(self.mediaList.count()):
            mediaItems.append(self.mediaList.item(index))
        return mediaItems

    def archiveFile(self, session):
        taskpath = str(self.taskEdit.text())
        projName = ftrack_utils.getProjectName(session, taskpath)
        src = self.filename.split(projName)[1]
        dest = 'P:\\%s%s' % (projName, src)
        destDir = os.path.dirname(dest)
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        import shutil
        shutil.copy(self.filename, dest)

    def publishMedia(self, session):
        self.archiveFile(session)
        comment = str(self.commentBox.toPlainText())
        from utils import subversion_utils
        subversion_utils.commit(self.filename, comment)
        metadata = {
            'filename':self.filename,
            'revision':subversion_utils.getVersionNumber(self.filename)
        }
        mediaItems = self.getAllMediaItems()
        for media in mediaItems:
            name = media.text()
            filepath, ext = os.path.splitext(name)
            if ext == '.mov':
                self.uploadMovie(session, name, metadata)
            elif self.isImgExt(ext):
                self.uploadImage(session, name, metadata)
        else:
            self.updateMetadata(session, metadata)
        self.close()

    def isImgExt(self, ext):
        if ext == '.exr' or ext == '.bmp' or ext == '.png' or \
           ext == '.jpg' or ext == '.jpeg' or ext == '.tiff':
                return True
        else:
            return False

    def updateMetadata(self, session, metadata):
        taskPath, asset, comment = self.getUploadDetails(session)
        task, version = ftrack_utils.createVersion(session, taskPath, asset, comment)
        ftrack_utils.addMetadata(session, version, metadata)
        thumbnail = str(self.thumbnailEdit.text())
        if not thumbnail=='':
            ftrack_utils.attachThumbnail(thumbnail, task, asset, version)
        ftrack_utils.setTaskStatus(session, taskPath, version, str(self.statusDrop.currentText()))

    def uploadMovie(self, session, inputFile, metadata):
        self.uploadButton.setDisabled(True)
        self.uploadButton.setText('Publishing ...')
        outfilemp4 =  os.path.splitext(inputFile)[0] + '.mp4'
        outfilewebm = os.path.splitext(inputFile)[0] + '.webm'
        thumnbail = os.path.join(os.path.split(inputFile)[0], 'thumbnail.png')
        threading.Thread( None, self.newThreadUpload, args=[session, inputFile, outfilemp4, outfilewebm, thumnbail, metadata]).start()

    def newThreadUpload(self, session, inputFile, outfilemp4, outfilewebm, thumnbail, metadata):
        result = self.convertFiles(inputFile, outfilemp4, outfilewebm)
        if result:
            thumbresult = ftrack_utils.createThumbnail(outfilemp4, thumnbail)
            taskPath, asset, comment = self.getUploadDetails(session)
            version = ftrack_utils.createAndPublishVersion(session, taskPath, comment, asset,
                                                outfilemp4, outfilewebm, thumnbail,
                                                self.frameIn, self.frameOut, self.framerate)
            ftrack_utils.setTaskStatus(session, taskPath, version, str(self.statusDrop.currentText()))
            ftrack_utils.addMetadata(session, version, metadata)
        self.deleteFiles(outfilemp4, outfilewebm, thumnbail)

    def uploadImage(self, session, inputFile, metadata):
        self.uploadButton.setDisabled(True)
        self.uploadButton.setText('Publishing ...')
        threading.Thread( None, self.newThreadJpg, args=[inputFile, session, metadata]).start()

    def newThreadJpg(self, inputFile, session, metadata):
        ext = os.path.splitext(inputFile)[1]
        if (ext == '.jpg') or (ext == '.jpeg'):
            outfilejpg = inputFile
        else:
            outfilejpg =  os.path.splitext(inputFile)[0] + '.jpg'
            result = ftrack_utils.convertToJpg(inputFile, outfilejpg)
        taskPath, asset, comment = self.getUploadDetails(session)
        version = ftrack_utils.publishImage(session, taskPath, comment, asset, outfilejpg)
        ftrack_utils.setTaskStatus(session, taskPath, version, str(self.statusDrop.currentText()))
        ftrack_utils.addMetadata(session, version, metadata)
        self.uploadButton.setEnabled(True)
        self.uploadButton.setText('Publish')
        self.uploadComplete.emit('Publish Complete!')

    def getUploadDetails(self, session):
        taskPath = str(self.taskEdit.text())
        assetName = str(self.assetDrop.currentText())
        if assetName == 'new':
            assetName = str(self.assetEdit.text())
        asset = ftrack_utils.getAsset(session, taskPath, assetName)
        comment = str(self.commentBox.toPlainText())
        return taskPath, asset, comment

    def deleteFiles(self, outfilemp4, outfilewebm, thumbnail):
        if os.path.exists(outfilemp4):
            os.remove(outfilemp4)
        if os.path.exists(outfilewebm):
            os.remove(outfilewebm)
        if os.path.exists(thumbnail):
            os.remove(thumbnail)
        self.uploadButton.setEnabled(True)
        self.uploadButton.setText('Publish')
        self.uploadComplete.emit('Publish Complete!')

    def convertFiles(self, inputFile, outfilemp4, outfilewebm):
        mp4Result = ftrack_utils.convertMp4Files(inputFile, outfilemp4)
        webmResult = ftrack_utils.convertWebmFiles(inputFile, outfilewebm)

        if mp4Result == 0 and webmResult == 0:
            return True
        else:
            return False

'''def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    gui = PublishWidget()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()'''