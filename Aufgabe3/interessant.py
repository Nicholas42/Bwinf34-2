#!/bin/env python3

import aufgabe3, sys

modes = [(0, False, -1, True), (1, True, -1, False), (2, False, 13, False), (4, True, -1, True), (5, True, -1, False)]

f = open('interessant','w')
sys.stdout = f

for i in modes:
    s = "yamyams%s.txt"%i[0]
    t = (s, i[1], i[2], i[3])
    if i[1]:
        s+=', fallen'
    if i[2] >-1:
        s+=', max%s'%i[2]
    if i[3]:
        s+=', riechen'
    s+=':'
    print(s)
    aufgabe3.main(*t)
    print()
