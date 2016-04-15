#!/usr/bin/env python3
from collections import deque
try:
    from PIL import Image
    bildout = True
except:
    print("Pillow ist nicht installiert.")
    print("Die Bildausgabe ist nun leider unmöglich.")
    bildout = False

# Einige Konstanten um die Lesbarkeit zu verbessern

AUSGANG = 'E'
WAND = '#'
FREI = ' '
UNSICHER = 'U'
SICHER = 'S'
ZUWEIT = 'W'


if bildout:
    LINE = 1
    PIXEL = (20, 20)
    
    try:
        # Eigentlich sollten die Bilder da sein...
        door = Image.open('pictures/door.png')
        wall = Image.open('pictures/wall7.png')
        INTERIM = Image.open('pictures/interim.png')
    except:
        #... aber man weiß ja nie
        print("Eins oder mehrere Bilder wurden nicht gefunden.")
        print("Fahre mit Ersatzbildern fort...")
        door = Image.new('RGB', PIXEL, (0x0, 0xb3, 0xb3))
        wall = Image.new('RGB', PIXEL, (0xb3, 0xb3, 0xb3))
        # Zur Verbindung zwei nebeneinanderstehender Wände
        INTERIM = Image.new('RGB', (LINE, PIXEL[1]), (0xb3, 0xb3, 0xb3))

    BILDER = {WAND: wall,
              FREI: Image.new('RGB', PIXEL, (0xff, 0xff, 0xff)),
              AUSGANG: door,
              SICHER: Image.new('RGB', PIXEL, (0x40, 0xff, 0x40)),
              UNSICHER: Image.new('RGB', PIXEL, (0xff, 0x40, 0x40)),
              ZUWEIT: Image.new('RGB', PIXEL, (0xff, 0xa5, 0x00))}


def einlesen(filename, fallen):
    ''' Hier wird das Feld eingelesen und die Adjazenzliste aufgebaut. '''
    with open(filename) as f:
        lines = [i.rstrip() for i in f]
    for i in range(len(lines)):  # Hier werden die Zeilen durchgegangen...
        maxconnected(lines[i], y=i, fallen=fallen)
    for i in range(len(lines[0])):  # ... und hier die Spalten
        line = [lines[j][i] for j in range(len(lines))]
        maxconnected(line, x=i, fallen=fallen)

    global size
    size = (len(lines), len(lines[0]))


def maxconnected(oneline, y=None, x=None, fallen=False):
    ''' Hier werden die längsten zusammenhängenden Stücke freier 
    Felder gefunden '''
    start = None
    end = None
    inarow = []
    for i in range(len(oneline)):
        zeichen = oneline[i]
        if zeichen == WAND:
            if end is not None:  # Dann hat gerade ein Stück aufgehört
                if not feld[end] == AUSGANG:
                    # Damit end keine Kante auf sich selbst hat
                    inarow.pop()
                if end not in adjlist:
                    adjlist.update({end: []})
                adjlist[end].extend(inarow)
                end = None
                start = None
                inarow = []
            continue
        # Damit die Methode für Spalten und Zeilen nutzbar ist
        if y is not None:
            pos = (y, i)
        else:
            pos = (i, x)
        if start is None:
            # Es beginnt demnach grade ein neues Stück
            start = pos
            if start not in adjlist:
                adjlist.update({start: []})
        end = pos
        feld.update({pos: zeichen})
        # Mit einem Dictionary lässt sich leicher arbeiten
        if zeichen == AUSGANG:
            # Auf einen Ausgang verweisen keine Kanten, da ein Weg endet,
            # wenn er zu einem Ausgang kommt
            if fallen:
                # Hier wird simuliert, dass der Yamyam durch die Tür fällt
                if pos not in adjlist:
                    adjlist.update({pos: []})
                adjlist[pos].extend(inarow)
                start = pos
                inarow = []
            ausgaenge.add(pos)
        else:
            inarow.append(pos)
            if not pos == start:
                # Damit start keine Kante auf sich selbst hat
                adjlist[start].append(pos)


def schreiben(filename, besucht, unsicher, zuweit):
    ''' Die Ausgabemethode '''
    klein = size[0] * size[1] < 10000000
    klein = klein and bildout
    # Das Bild sollte nicht zu groß werden
    if klein:
        bild = Image.new('RGB',
                         (size[1] * (PIXEL[0] + LINE) + LINE,
                          size[0] * (PIXEL[1] + LINE) + LINE),
                         (0xb3, 0xb3, 0xb3))
    out = []
    for y in range(size[0]):
        last = ''
        for x in range(size[1]):
            # Da die Wände nicht abgespeichert sind
            zeichen = feld.get((y, x), WAND)
            if zeichen == WAND:
                pass
            elif zeichen == AUSGANG:
                pass
            elif (y, x) in zuweit:
                zeichen = ZUWEIT
            elif (y, x) in unsicher:
                zeichen = UNSICHER
            elif (y, x) not in besucht:
                zeichen = SICHER
            out.append(zeichen)

            if klein:
                bild.paste(BILDER[zeichen],
                           (x * (PIXEL[0] + LINE) + LINE,
                            y * (PIXEL[0] + LINE) + LINE))
                if last == WAND and zeichen == WAND:
                    bild.paste(INTERIM,
                               (x * (PIXEL[0] + LINE),
                                y * (PIXEL[1] + LINE) + LINE))

            last = zeichen

        out.append('\n')

    out = ''.join(out)
    print(out)
    with open(filename + '.out', 'w') as f:
        f.write(out)
    print('Die Ausgabe wurde nach %s.out geschrieben.' % (filename))
    if klein:
        bild.save(filename + '.png')
        print('Das Bild wurde nach %s.png geschrieben.' % filename)


def main(filename, fallen=False, togo=-1, riechen=False):
    ''' Der Beginn allen Übels '''
    global feld, adjlist, ausgaenge
    feld = {}
    adjlist = {}
    ausgaenge = set()
    einlesen(filename, fallen)
    tmp = set()
    if riechen:
        tmp.update(*(adjlist.get(i, set()) for i in ausgaenge))
    # Die erste Breitensuche, von den Ausgängen aus
    besucht = broad(ausgaenge, 2*togo)
    unsicher = set.difference(set(feld), besucht)
    
    # Die zweite Breitensuche, von den unsicheren Feldern aus
    besucht2 = broad(unsicher, togo, tmp)
    if togo > -1:
        umfeld = broad(ausgaenge, togo)
        entfernt = besucht.difference(umfeld)
    else:
        entfernt = set()
    if filename.endswith('.txt'):  # Niemand mag .txt.out
        filename = filename[:-4]
    if fallen:
        filename += ',fallen'
    if not togo == -1:
        filename += ',max%s'%togo
    if riechen:
        filename += ',riechen'
    schreiben(filename, besucht2, unsicher, entfernt)

def broad(start, togo, stopper=set()):
    ''' Eine iterative Breitensuche ohne Ziel '''
    besucht = set()
    rand = deque()
    for i in start:
        rand.append(i)
        besucht.add(i)
    togo -= 1
    rand.append(togo)
    while len(rand) > 0:
        current = rand.popleft()
        if isinstance(current, int):
            # Nach jeder Tiefe wird eine Zahl eingefügt um so
            # eine maximale Tiefe bestimmen zu können
            if current == 0 or len(rand) == 0:
                return besucht
            current = rand.popleft()
            togo -= 1
            rand.append(togo)
        for i in adjlist.get(current, set()):
            if i not in besucht and i not in stopper:
                besucht.add(i)
                rand.append(i)
    return besucht
        

if __name__ == '__main__':
    filename = input("Datei:\n")
    fallen = input("Kann der Yamyam durch Türen fallen? (y/n)\n") == "y"
    togo = int(input("Wie weit kann der Yamyam maximal gehen? (-1 = beliebig)\n"))
    riechen = input("Kann der Yamyam Türen aus der Nähe erkennen? (y/n)\n") == "y"
    main(filename, fallen = fallen, togo = togo, riechen = riechen)
