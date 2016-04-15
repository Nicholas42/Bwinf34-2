#!/bin/env python3
from datetime import datetime, timedelta
import fortschritt

DirToStr = {(0, 1): 'O', (1, 0): 'S', (0, -1): 'W', (-1, 0): 'N', (0, 0): '_'}
StrToDir = {'N': (-1, 0), 'W': (0, -1), 'S': (1, 0), 'O': (0, 1), '_': (0, 0)}

twoxtwo = [{(0, 1): (0, 1), (1, 0): (1, 1), (0, 0): (0, 0), (1, 1): (1, 0)},
           {(0, 1): (0, 0), (1, 0): (1, 0), (0, 0): (0, 1), (1, 1): (1, 1)},
           {(0, 1): (1, 1), (1, 0): (0, 0), (0, 0): (1, 0), (1, 1): (0, 1)},
           {(0, 1): (1, 1), (1, 0): (0, 0), (0, 0): (0, 1), (1, 1): (1, 0)},
           {(0, 1): (0, 1), (1, 0): (1, 0), (0, 0): (0, 0), (1, 1): (1, 1)},
           {(0, 1): (1, 1), (1, 0): (1, 0), (0, 0): (0, 0), (1, 1): (0, 1)},
           {(0, 1): (0, 0), (1, 0): (1, 1), (0, 0): (1, 0), (1, 1): (0, 1)},
           {(0, 1): (0, 1), (1, 0): (0, 0), (0, 0): (1, 0), (1, 1): (1, 1)},
           {(0, 1): (0, 0), (1, 0): (1, 1), (0, 0): (0, 1), (1, 1): (1, 0)}]

diff = lambda y, x: (x[0] - y[0], x[1] - y[1])


def lese(filename, turned=False):
    ''' Liest das Feld aus einer Datei, gegebenenfalls auch die gespiegelte Variante '''
    with open(filename) as f:
        lines = f.readlines()
    global size
    size = int(lines.pop(0).strip())
    feld = {}
    for i in lines:
        sp = list(map(int, i.split()))
        if len(sp) < 4:
            # Falls am Ende eine Leerzeile ist
            break
        if turned:
            feld.update({(sp[1], sp[0]): (sp[3], sp[2])})
        else:
            feld.update({(sp[0], sp[1]): (sp[2], sp[3])})
    return feld


def schreibe(feld):
    ''' Gibt das Feld in die Konsole aus '''
    out = ["\t(y, %d)" % i for i in range(size)]
    # Die obere Koordinatenleiste
    out.append("\n")
    for i in range(size):
        out.append("(%d, x)\t" % i)
        # Die Koordinate an der linken Seite
        for j in range(size):
            out.append("%s\t" % str(feld[(i, j)]))
        out.append("\n")
    print("".join(out))


def wert(t):
    ''' Berechnet den Wert einer Position '''
    ret = t[0] * size
    ret += t[1] if t[0] % 2 == 0 else (size - t[1] - 1)
    return ret


def oddeven(tosort, start):
    '''
    Führt auf tosort eine Odd- oder einen Even-Durchgang aus.
    Dabei ist start = 0 ein Even-Durchgang und
    start = 1 ein Odd-Durchgang
    '''
    ret = tosort.copy()
    keys = [i for i in sortedkeys if i in tosort]
    # Dadurch hat man die Schlüssel in O(n) sortiert und muss
    # nur einmal die O(n*log(n)) sorted-Methode benutzen
    ausg = {}
    for i in range(start, len(keys) - 1, 2):
        if wert(tosort[keys[i]]) > wert(tosort[keys[i + 1]]):
            ret[keys[i]], ret[keys[i + 1]] = tosort[keys[i + 1]], tosort[keys[i]]
            ausg.update({keys[i]: DirToStr[diff(keys[i], keys[i + 1])]})
            ausg.update({keys[i + 1]: DirToStr[diff(keys[i + 1], keys[i])]})
    return ret, ausg


def hor(feld):
    ''' Führt einen Spaltensortiervorgang aus. '''
    ausg = {}  # Hier wird der Log gespeichert
    endfeld = {}  # Hier wird das Feld gespeichert
    for i in range(size):
        column = dict(((j, i), feld[j, i]) for j in range(size))
        # column enthält nun alle Positionen aus der i-ten Spalte von feld
        a = oddeven(column, 0)  # Der Even-Durchgang
        b = oddeven(column, 1)  # Der Odd-Durchgang
        m = min(a, b, key=lambda x: bewertefeld(x[0]))
        ausg.update(m[1])
        endfeld.update(m[0])
    return endfeld, ausg


def square(fe, lo):
    ''' Hier wird die Quadratsortierung durchgeführt '''
    f = fe.copy()
    log = dict((i, lo[i][-1]) for i in lo)
    # Die jeweils letzten Änderungen wurden aus dem Log extrahiert
    for x in range(0, size - 1):
        for y in range(0, size - 1):
            doit = log[x, y] in ['S', 'O', '_']
            doit = doit and log[x + 1, y] in ['N', 'O', '_']
            doit = doit and log[x, y + 1] in ['S', 'W', '_']
            doit = doit and log[x + 1, y + 1] in ['N', 'W', '_']
            # doit ist genau dann wahr, wenn alle Veränderungen in diesem
            # 2x2 Quadrat innerhalb von ihm durchgeführt wurden
            if not doit:
                # Wenn es auch Veränderungen nach Außen gab lässt sich
                # der Log nicht sicher manipulieren
                continue
            if x % 2 == 0:
                # So sind die Positionen nach ihrem Wert sortiert
                bereich = [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)]
            else:
                bereich = [(x, y + 1), (x, y), (x + 1, y), (x + 1, y + 1)]
            if wert(f[bereich[0]]) <= wert(f[bereich[1]]) <= wert(
                    f[bereich[2]]) <= wert(f[bereich[3]]):
                # Dann ist alles schon optimal sortiert
                continue
            # Hier werden die letzten Änderungen rückgängig gemacht
            # Da die anderen Algorithmen ausschließlich Paartausche ausführen,
            # impliziert ein 'S' der nördlichen Position ein 'N' der südlichen
            # und deswegen ist klar, dass ein Tausch zwischen diesen beiden
            # stattgefunden hat
            if log[x, y] == 'S':
                f[x, y], f[x + 1, y] = f[x + 1, y], f[x, y]
            elif log[x, y] == 'O':
                f[x, y], f[x, y + 1] = f[x, y + 1], f[x, y]
            if log[x + 1, y + 1] == 'W':
                f[x + 1, y], f[x + 1, y + 1] = f[x + 1, y + 1], f[x + 1, y]
            elif log[x + 1, y + 1] == 'N':
                f[x, y + 1], f[x + 1, y + 1] = f[x + 1, y + 1], f[x, y + 1]
            allsq = allsquares(f, x, y)
            m = min(allsq, key=lambda t: bewertefeld(t[0]))
            # m ist die der Bewertung nach beste Umsortierung
            for i in m[1]:
                # Der Log wird angepasst
                log[i] = DirToStr[(m[1][i][0] - i[0], m[1][i][1] - i[1])]
            f.update(m[0])  # Das Feld wird auf Vordermann gebracht
    return f, log, bewertefeld(f)


def allsquares(f, x, y):
    '''
    Hier werden alle gültigen Züge für ein 2x2-Quadrat mit
    der linken, oberen Ecke (x, y) berechnet.
    '''
    allsq = []
    for m in twoxtwo:
        logtmp = {}
        ftmp = {}
        for n in m:
            k = m[n]  # eckige Klammern sind nervig zu tippen
            logtmp.update({(n[0] + x, n[1] + y): (k[0] + x, k[1] + y)})
            ftmp.update({(k[0] + x, k[1] + y): f[(n[0] + x, n[1] + y)]})
        allsq.append((ftmp, logtmp))
    return allsq


def shearsort(filename):
    '''
    Der Shearsort-Algorithmus wird ausgeführt
    '''
    feld = lese(filename)
    print("Das ist das Feld:")
    schreibe(feld)
    print("Der Shearsort-Algorithmus wird durchgeführt:\n")
    global sortedkeys
    sortedkeys = sorted(feld, key=lambda x: wert(x))
    maxdiff = max(abs(diff(i, feld[i])[0]) +
                  abs(diff(i, feld[i])[1]) for i in feld)
    from math import log2
    log = dict((i, []) for i in feld)
    balken = fortschritt.balken(2 * int(log2(size) + 1) + 1, size=60)
    for n in range(int(log2(size)) + 1):
        while True:
            newlog = {}
            newlog1 = {}
            for j in range(size):
                row = dict(((j, k), feld[j, k]) for k in range(size))
                a, b = oddeven(row, 0)
                feld.update(a)
                newlog.update(b)
                row = dict(((j, k), feld[j, k]) for k in range(size))
                c, d = oddeven(row, 1)
                feld.update(c)
                newlog1.update(d)
            if len(newlog) + len(newlog1) == 0:
                break
            if len(newlog) > 0:
                for i in log:
                    log[i].append(newlog.get(i, '_'))
            if len(newlog1) > 0:
                for i in log:
                    log[i].append(newlog1.get(i, '_'))
        balken.update(2 * n + 1)
        while True:
            newlog = {}
            newlog1 = {}
            for j in range(size):
                col = dict(((k, j), feld[k, j]) for k in range(size))
                a, b = oddeven(col, 0)
                feld.update(a)
                newlog.update(b)
                col = dict(((k, j), feld[k, j]) for k in range(size))
                a, b = oddeven(col, 1)
                feld.update(a)
                newlog1.update(b)
            if len(newlog) + len(newlog1) == 0:
                break
            if len(newlog) > 0:
                for i in log:
                    log[i].append(newlog.get(i, '_'))
            if len(newlog1) > 0:
                for i in log:
                    log[i].append(newlog1.get(i, '_'))
        balken.update(2 * n + 2)
    while True:
        newlog = {}
        newlog1 = {}
        for j in range(size):
            row = dict(((j, k), feld[j, k]) for k in range(size))
            a, b = oddeven(row, 0)
            feld.update(a)
            newlog.update(b)
            row = dict(((j, k), feld[j, k]) for k in range(size))
            c, d = oddeven(row, 1)
            feld.update(c)
            newlog1.update(d)
        if len(newlog) + len(newlog1) == 0:
            break
        if len(newlog) > 0:
            for i in log:
                log[i].append(newlog.get(i, '_'))
        if len(newlog1) > 0:
            for i in log:
                log[i].append(newlog1.get(i, '_'))
    balken.end()
    print()
    print("Sortiert in %s Schritten." % len(log[0, 0]))
    return log, maxdiff


def bewertefeld(f):
    '''
    Das übergebene Feld wird bewertet. Diese ist eine laufzeitkritische
    Methode und wurde deshalb vollständig per Hand programmiert.
    '''
    m = 0
    anz = 0
    for i in f:
        t = (i[0] - f[i][0]) * size
        t += i[1] if i[0] % 2 == 0 else (size - 1 - i[1])
        t -= f[i][1] if f[i][0] % 2 == 0 else (size - 1 - f[i][1])
        t = abs(t)
        # t ist die Distanz von dem Paket an Position i zu seinem Ziel
        if t > m:
            anz = 1
            m = t
        elif t == m:
            anz += 1
    return (m, anz)


def main(filename, maxlen, turned=False, quadrate=False):
    feld = lese(filename, turned=turned)
    global sortedkeys
    sortedkeys = sorted(feld, key=lambda x: wert(x))
    log = dict((i, []) for i in feld)
    if not turned:
        print("Es wird das richtig orientierte Feld sortiert:\n")
    else:
        print("Es wird das gespiegelte Feld sortiert:\n")
    maxdiff = max(abs(diff(i, feld[i])[0]) +
                  abs(diff(i, feld[i])[1]) for i in feld)
    print(
        "Die minimale Anzahl an Schritten, dieses Tohuwabohu zu sortieren, beträgt %s." %
        maxdiff)
    print("Beginne mit der Sortierung...\n")
    bewertung = bewertefeld(feld)
    balken = fortschritt.balken(bewertung[0], size=60, turned=True)
    while bewertung[0] > 0:
        if len(log[0, 0]) > maxlen:
            # So wird keine Zeit mehr für offensichtlich schlechtere Ansätze
            # mehr verschwendet
            balken.cancel()
            print("Dieser Algorithmus ist schlechter als ein vorhergehender.")
            return log, maxdiff
        odd = oddeven(feld, 1)
        even = oddeven(feld, 0)
        horiz = hor(feld)
        m = min(horiz, odd, even, key=lambda x: bewertefeld(x[0]))
        for i in log:
            log[i].append(m[1].get(i, '_'))
        feld = m[0]
        bewertung = bewertefeld(feld)
        balken.update(bewertung[0])
        if not quadrate:
            continue
        m = square(feld, log)
        if m[2] < bewertung:
            feld.update(m[0])
            for i in log:
                log[i][-1] = m[1][i]
            bewertung = m[2]
            balken.update(bewertung[0])
    out = []
    print("\nSortiert in %d Schritten." % len(log[0, 0]))
    swap = {'S': 'O', 'N': 'W', 'O': 'S', 'W': 'N', '_': '_'}
    if turned:
        newlog = {}
        for i in log:
            newlog.update({(i[1], i[0]): [swap[j] for j in log[i]]})
        log = newlog
    return log, maxdiff


def main1(filename, quadrate):
    c = shearsort(filename) + ('der Shearsort-Algorithmus als der',)
    print("________________________________________________\n")
    maxlen = len(c[0][0, 0])
    a = main(filename, maxlen, False, quadrate) + \
        ('die Sortierung mit normaler Orientierung als die',)
    maxlen = min(maxlen, len(a[0][0, 0]))
    print("________________________________________________\n")
    b = main(filename, maxlen, True, quadrate) + \
        ('die Sortierung mit gespiegelter Orientierung als die',)
    out = min(a, b, c, key=lambda x: len(x[0][0, 0]))
    print(
        "\nNachdem alle Algorithmen evaluiert wurden, erscheint " +
        "%s Beste mit einer Länge von %s." %
        (out[2], len(out[0][0, 0])))
    return out


if __name__ == "__main__":
    filename = input("Eingabefeld?\n")
    quadrate = input(
        "Soll die Quadratsortierung angwandt werden? (y,n)\n") == 'y'
    begin = datetime.now()
    out = main1(filename, quadrate)
    end = datetime.now()
    seconds = (end - begin).total_seconds()
    if seconds > 60:
        zeit = "%d Minuten und %f Sekunden" % (seconds // 60, seconds % 60)
    else:
        zeit = "%f Sekunden" % (seconds)
    print("Das Sortieren hat %s gedauert" % zeit)
    print("\n")
    aus = dict()
    for i in out[0]:
        aus.update({i: ''.join(out[0][i])})
    output = '\n'.join('%s %s %s' % (i, j, aus[i, j]) for i in range(size)
                       for j in range(size))
    if quadrate:
        # Um die Ausgaben zu trennen
        sq = "(mitsquares)"
    else:
        sq = ""
    with open(filename + sq + '.out', 'w') as f:
        f.write(output)
    print("Die Ausgabe wurde nach %s%s.out geschrieben.\n" % (filename, sq))
    animiert = input(
        "Wollen Sie den Ablauf animiert haben? " +
        "Dies ist bei Feldgrößen > 20 weniger sinnvoll. (y, n)\n") == 'y'
    if animiert:
        import animation
        animation.main(filename, dirlog=out[0])
