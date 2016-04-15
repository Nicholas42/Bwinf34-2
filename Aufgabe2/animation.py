#!/bin/env python3
from PyQt4 import QtGui
import gui
import sys

StrToDir = {'N': (-1, 0), 'W': (0, -1), 'S': (1, 0), 'O': (0, 1), '_': (0, 0)}
DirToStr = {(-1, 0): 'N', (0, -1): 'W', (1, 0): 'S',
            (0, 1): 'O', (0, 0): '_', None: '_'}


def lese(filename):
    feld = {}
    with open(filename) as f:
        lines = f.readlines()
    global size
    size = int(lines.pop(0).strip())
    for i in lines:
        sp = list(map(int, i.split()))
        if len(sp) < 4:
            break
        feld.update({(sp[0], sp[1]): (sp[2], sp[3])})
    return feld


def main(feldeingabe, filename=None, dirlog=None):
    feld = lese(feldeingabe)
    if dirlog is None:
        with open(filename) as f:
            lines = f.readlines()
        dirlog = {}
        for i in lines:
            if len(i.split()) < 3:
                break
            tup = (int(i.split()[0]), int(i.split()[1]))
            dirlog.update({tup: list(i.split()[2].strip())})
    log = {}
    for i in dirlog:
        log.update({i: [StrToDir[j] for j in dirlog[i]]})
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Animation")
    fenster = gui.Fenster(feld, log)
    fenster.show()
    app.exec_()

if __name__ == '__main__':
    try:
        import filechooser
    except:
        pass
    feldeingabe = input('Felddatei:\n')
    filename = input('Logdatei:\n')
    main(feldeingabe, filename)
