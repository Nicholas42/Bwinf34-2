#!/bin/env python3
size = int(input("Wie groß soll das Feld werden?\n"))
filename = input("Wo soll es gespeichert werden?\n")
out = [str(size)]
for i in range(size):
    for j in range(size):
        out.append("%s %s %s %s" % (i, j, size - j - 1, size - 1 - i))
with open(filename, 'w') as f:
    f.write('\n'.join(out))
