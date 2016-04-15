#!/bin/env python3
from os import listdir
from os.path import isfile
import re, imp, aufgabe3


match = re.compile("^yamyams\d+.txt$")
fallen = input("fallen")=="y"
togo = int(input("togo"))
riechen = input("riechen") =="y"
files = [i for i in listdir() if isfile(i) and match.match(i)]
import sys
sys.stdout = open('ausgabe.out', 'w')
for i in sorted(files):
    print(i+':')
    imp.reload(aufgabe3)
    aufgabe3.main(i, fallen, togo, riechen)
    print()
sys.stdout.close()
