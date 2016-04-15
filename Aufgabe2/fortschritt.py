class balken:

    def __init__(self, maxlen, size=20, turned=False):
        self.maxlen = maxlen
        self.size = size
        self.turned = turned
        self.fertig = False
        if self.turned:
            self.aktuell = self.maxlen
            self.update(self.maxlen)
        else:
            self.aktuell = 0
            self.update(0)

    def end(self):
        self.update(self.maxlen)

    def cancel(self):
        print("  Abbruch.", flush=True)
        self.fertig = True

    def update(self, wert):
        if self.fertig:
            return
        if self.turned:
            wert = self.maxlen - wert
        if not wert == self.aktuell:
            self.aktuell = (self.size * wert) // self.maxlen
        self.repaint()
        if self.aktuell == self.size:
            print("  Fertig.", flush=True)
            self.fertig = True

    def repaint(self):
        print('\b' * (self.size + 2), end='', flush=True)
        print('[' + '#' * (self.aktuell) + '_' *
              (self.size - self.aktuell) + ']', end='', flush=True)
