__author__ = 'Natasha'

import os
import PySide.QtGui as QtGui
import nuke
from gui import FileWidget


class WorkspaceWidget(QtGui.QWidget):

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QGridLayout())
        self.setWindowTitle('Loco Workspace Manager')
        self.setMinimumSize(450,200)
        self.setObjectName('WorkspaceWidget')
        baseFile = os.path.join(os.environ['TEMP'], 'workspace_config.txt')
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(QtGui.QLabel('Base Path'))
        baseEdit = QtGui.QLineEdit()
        baseEdit.setReadOnly(True)
        hlayout.addWidget(baseEdit)
        self.browseButton = QtGui.QToolButton()
        self.browseButton.setText('...')
        self.browseButton.clicked.connect(lambda: self.browseDirs(baseFile, baseEdit))
        hlayout.addWidget(self.browseButton)
        self.layout().addLayout(hlayout, 0, 0)
        basedir = self.getBaseDir(baseFile)
        if not basedir == '':
            self.setPath(basedir, baseFile)
            baseEdit.setText(basedir)

    def browseDirs(self, baseFile, baseEdit):
        dialog = QtGui.QFileDialog()
        dirname = dialog.getExistingDirectory(self, "Select Directory",
                                              os.path.dirname(baseEdit.text()),
                                              options= QtGui.QFileDialog.DontUseNativeDialog)
        baseEdit.setText(str(dirname))
        self.setPath(str(dirname), baseFile)

    def setPath(self, basedir, baseFile):
        fileWidget = FileWidget.FileWidget(basedir)
        self.layout().addWidget(fileWidget, 2, 0)
        self.writePathToFile(basedir, baseFile)
        fileWidget.fileOpen.connect(self.openNukeFile)
        fileWidget.screenShot.connect(self.takeScreenshot)

    def takeScreenshot(self, fileName):
        fileName = fileName.replace('\\', '/')
        viewer = nuke.activeViewer()
        actInput = nuke.ViewerWindow.activeInput(viewer)
        viewNode = nuke.activeViewer().node()
        selInput = nuke.Node.input(viewNode, actInput)
        write = nuke.nodes.Write(file=fileName, name='tmpWrite', file_type='jpg')
        write.setInput(0, selInput)
        curFrame = int(nuke.knob("frame"))
        nuke.execute(write.name(), curFrame, curFrame)
        nuke.delete(write)

    def openNukeFile(self, filename):
        filename = filename.replace('\\', '/')
        filebase, ext = os.path.splitext(filename)
        if ext == '.nk':
            nuke.scriptOpen(filename)
        else:
            nuke.message('Invalid nuke script. Please open a .nk script only')

    def writePathToFile(self, basedir, baseFile):
        f = open(baseFile, 'w')
        f.write(('Base Dir=%s' % basedir))
        f.close()

    def getBaseDir(self, baseFile):
        if os.path.exists(baseFile):
            f = open(baseFile, 'r')
            line = f.readline()
            basedir = line.split('=')[-1]
            return basedir
        else:
            return ''
