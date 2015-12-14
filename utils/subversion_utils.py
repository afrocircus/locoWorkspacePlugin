__author__ = 'Natasha'

import subprocess
import os
import logging

tortoiseSVN = 'C:\\Program Files\\TortoiseSVN\\bin\\TortoiseProc.exe'
svn = 'C:\\Program Files\\Apache-Subversion-1.9.2\\bin\\svn.exe'
outfile = os.path.join(os.environ['TEMP'], 'repo.txt')


def openRepoBrowser():
    cmd = '"%s" /command:repobrowser /outfile:%s' % (tortoiseSVN, outfile)
    result = subprocess.Popen(cmd)
    result.wait()


def getSelectedRepo():
    f = open(outfile, 'r')
    repoPath = f.readline()
    return repoPath.strip()


def checkout(url, path):
    cmd = '"%s" checkout "%s" "%s"' % (svn, url, path)
    try:
        subprocess.Popen(cmd)
    except ValueError:
        logging.error('SVN Checkout error: url=%s path=%s' % (url, path))


def add(path):
    cmd = '"%s" add "%s"' % (svn, path)
    try:
        subprocess.Popen(cmd)
    except ValueError:
        logging.error('SVN Add error: path=%s' % path)


def commit(path, message):
    cmd = '"%s" commit -m "%s" "%s"' % (svn, message, path)
    try:
        subprocess.Popen(cmd)
    except ValueError:
        logging.error('SVN checkin error: path=%s' % path)


def status(path):
    textStatus = ''
    if os.path.isdir(path):
        cmd = '"%s" status --depth empty -v "%s"' % (svn, path)
    else:
        cmd = '"%s" status -v "%s"' % (svn, path)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    out, err = process.communicate()
    process.kill()
    fields = out.split()
    if fields:
        if not fields[0].isdigit():
            if fields[0] == 'M':
                textStatus = 'modified'
            elif fields[0] == 'A':
                textStatus = 'added'
            elif fields[0] == '?':
                textStatus = 'unversioned'
        else:
            textStatus = 'versioned'
    if err:
        textStatus = 'unversioned'
    return textStatus


def update(path):
    cmd = '"%s" update "%s"' % (svn, path)
    try:
        subprocess.Popen(cmd)
    except ValueError:
        logging.error('SVN update error: path=%s' % path)


def getVersionNumber(path):
    revNo = None
    cmd = '"%s" status -v "%s"' % (svn, path)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    out, err = process.communicate()
    process.kill()
    fields = out.split()
    for f in fields:
        if f.isdigit():
            revNo = f
            break
    return revNo