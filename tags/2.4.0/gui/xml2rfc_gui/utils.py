""" Utility classes and functions """
import os
import subprocess

# PyQT modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def getDirectorySize(dir):
    """ Returns the size, in bytes, of a directory tree rooted at `dir` """
    size = 0
    if os.path.exists(dir):
        for path, dirs, files in os.walk(dir):
            for file in files:
                size += os.path.getsize(os.path.join(path, file))
    return size


def osxSudo(cmd):
    """ Run arbitrary unix as an apple shellscript that prompts for sudo """
    return subprocess.call(['osascript', '-e', 'do shell script "%s" with administrator privileges' % cmd])

class Status:
    """ Simple message stack for a QStatusBar """
    def __init__(self, statusBar):
        self.stack_ = []
        self.statusBar = statusBar
    
    def __call__(self, msg):
        """ Set the head message """
        if len(self.stack_) > 0:
            self.stack_[-1] = msg
            self.update()
            
        else:
            self.push(msg)
        
    def push(self, msg):
        self.stack_.append(msg)
        self.update()
        
    def pop(self):
        self.stack_.pop()
        self.update()
        
    def update(self):
        # Update statusbar with head message
        if len(self.stack_) > 0:
            self.statusBar.showMessage(self.stack_[-1])
        else:
            self.statusBar.showMessage(' ')


class StreamHandler:
    """ Fakes a file-like object with write and flush using callbacks """
    def __init__(self, callback):
        self.callback = callback
        
    def write(self, data):
        # Ignore newline-only strings
        data = data.strip('\n')
        if data:
            self.callback(data)

    def flush(self):
        # Omit for this implementation
        pass
