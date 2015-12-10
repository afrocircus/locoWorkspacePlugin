__author__ = 'Natasha'

import os
import PySide.QtGui as QtGui
from gui import FileWidget


class WorkspaceWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QGridLayout())
        self.setWindowTitle('Loco Workspace Manager')
        self.setMinimumSize(450,200)
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


def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    gui = WorkspaceWidget()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
