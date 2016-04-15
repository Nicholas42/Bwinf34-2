#!/bin/env python3
import random


def main(size):
    l = [(x, y) for x in range(size) for y in range(size)]
    l1 = l[:]
    random.shuffle(l1)
    out = [str(size), '\n']
    for i in range(len(l)):
        out.append("%d %d %d %d\n" % (l[i] + l1[i]))
    return out

if __name__ == "__main__":
    size = int(input("Wie groß soll das Feld werden?\n"))
    f = input("Wo soll es gespeichert werden?\n")
    out = main(size)
    with open(f, 'w') as fi:
        fi.write(''.join(out))
