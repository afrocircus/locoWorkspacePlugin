__author__ = 'Natasha'

import os
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
from utils import subversion_utils
from gui import PublishWidget
from PySide.QtCore import Signal


class LocoFileSystemModel(QtGui.QFileSystemModel):

    def columnCount(self, parent = QtCore.QModelIndex()):
        return super(LocoFileSystemModel, self).columnCount()+1

    def data(self, index, role):
        if index.column() == self.columnCount() - 1:
            if role == QtCore.Qt.DisplayRole:
                status = self.getSVNStatus(self.filePath(index))
                return status
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignHCenter

        return super(LocoFileSystemModel, self).data(index, role)

    def getSVNStatus(self, filepath):
        status = subversion_utils.status(filepath)
        return status


class FileWidget(QtGui.QWidget):

    fileOpen = Signal(str)
    screenShot = Signal(str)

    def __init__(self, basedir):
        super(FileWidget, self).__init__()
        self.setLayout(QtGui.QGridLayout())
        self.model = LocoFileSystemModel()
        self.model.setRootPath(basedir)
        self.basedir = basedir
        self.view = QtGui.QTreeView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(basedir))
        self.view.hideColumn(1)
        self.view.hideColumn(2)
        self.view.hideColumn(3)
        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.showContextMenu)
        self.layout().addWidget(self.view)
        self.view.clicked.connect(self.itemClicked)
        self.createActions()

    def createActions(self):
        self.open = QtGui.QAction("Open", self,
            statusTip="Open File",
            triggered=self.openFile)
        self.checkout = QtGui.QAction("Checkout", self,
            statusTip="Checkout from Repo",
            triggered=self.checkoutRepo)
        self.add = QtGui.QAction("Add", self,
            statusTip="Add File to Repo",
            triggered=self.addTosvn)
        self.commit = QtGui.QAction("Commit", self,
            statusTip="Commit File to Repo",
            triggered=self.commitTosvn)
        self.publish = QtGui.QAction("Publish", self,
            statusTip="Publish File to Repo",
            triggered=self.publishTosvn)
        self.update = QtGui.QAction("Update", self,
            statusTip="Update File",
            triggered=self.updateFromsvn)

    def itemClicked(self):
        indexes = self.view.selectedIndexes()
        if indexes:
            filename = self.model.filePath(indexes[0])
        else:
            filename = self.basedir
        return filename

    def showContextMenu(self, position):
        menu = QtGui.QMenu()
        menu.addAction(self.open)
        menu.addAction(self.checkout)
        menu.addAction(self.add)
        menu.addAction(self.commit)
        menu.addAction(self.publish)
        menu.addAction(self.update)
        menu.exec_(self.view.mapToGlobal(position))

    def openFile(self):
        filename = self.itemClicked()
        self.fileOpen.emit(filename)

    def checkoutRepo(self):
        subversion_utils.openRepoBrowser()
        url = subversion_utils.getSelectedRepo()
        projName = url.split('/')[-1]
        path = self.itemClicked()
        path = os.path.join(path, projName)
        if not os.path.exists(path):
            os.mkdir(path)
        subversion_utils.checkout(url, path)

    def addTosvn(self):
        filename = self.itemClicked()
        subversion_utils.add(filename)

    def commitTosvn(self):
        filename = self.itemClicked()
        comment, ok = QtGui.QInputDialog.getText(self, 'Commit Message', 'Comment:')
        subversion_utils.commit(filename, comment)

    def publishTosvn(self):
        filename = self.itemClicked()
        publishWidget = PublishWidget.PublishWidget(parent=self, filename=filename)
        publishWidget.show()
        publishWidget.screenshot.connect(self.emitScreenShotSignal)

    def emitScreenShotSignal(self, filename):
        self.screenShot.emit(filename)

    def updateFromsvn(self):
        filename = self.itemClicked()
        subversion_utils.update(filename)
