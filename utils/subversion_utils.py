__author__ = 'Natasha'

import pysvn
import subprocess
import os
import logging

tortoiseSVN = 'C:\\Program Files\\TortoiseSVN\\bin\\TortoiseProc.exe'
outfile = os.path.join(os.environ['TEMP'], 'repo.txt')
client = pysvn.Client()


def openRepoBrowser():
    cmd = '"%s" /command:repobrowser /outfile:%s' % (tortoiseSVN, outfile)
    result = subprocess.Popen(cmd)
    result.wait()


def getSelectedRepo():
    f = open(outfile, 'r')
    repoPath = f.readline()
    return repoPath.strip()


def checkout(url, path):
    try:
        client.checkout(url, path)
    except ValueError:
        logging.error('SVN Checkout error: url=%s path=%s' % (url, path))


def add(path):
    try:
        client.add(path)
    except ValueError:
        logging.error('SVN Add error: path=%s' % path)


def commit(path, message):
    try:
        client.checkin(path, message)
    except ValueError:
        logging.error('SVN checkin error: path=%s' % path)


def status(path):
    stats = 'Error'
    try:
        stats = client.status(path, recurse=False)[0]
        textStatus = str(stats['text_status'])
        if textStatus == 'normal':
            textStatus = 'versioned'
    except:
        textStatus = "unversioned"
    return textStatus


def update(path):
    try:
        client.update(path)
    except ValueError:
        logging.error('SVN update error: path=%s' % path)


def getVersionNumber(path):
    revNo = None
    try:
        info = client.info(path)
        rev = info['commit_revision']
        revNo = rev.number
    except ValueError:
        logging.error('SVN version error: path=%s' % path)
    return revNo