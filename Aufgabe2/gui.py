from PyQt4.QtGui import *
from PyQt4.QtCore import *
from math import sqrt
import datetime


class Fenster(QMainWindow):

    fertig = pyqtSignal()

    def __init__(self, feld, log):
        super(Fenster, self).__init__()

        self.feld = feld
        self.current = feld.copy()
        self.log = log
        self.bloecke = {}
        self.add = lambda x, y: (x[0] + y[0], x[1] + y[1])

        self.breite = int(sqrt(len(feld)))
        self.slideTimer = QTimer(self)
        self.delayTimer = QTimer(self)
        self.steps = 50
        self.maxsteps = len(log[0, 0])
        self.stepcounter = 0
        self.slideTimer.setInterval(20)
        self.delayTimer.setInterval(1000)

        self.bestSize = 600 // self.breite
        self.delta = self.bestSize / self.steps
        if self.delta < 1:
            self.delta = 1
            self.steps = self.bestSize
            self.slideTimer.setInterval(1000 // self.steps)
        self.maxwert = max(map(self.wert, self.feld))

        self.view = QGraphicsView()
        self.view.setFixedSize(650, 650)
        self.setFixedSize(self.sizeHint())
        self.startButton = QPushButton("Start")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.startButton)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.layout)
        self.setWindowTitle("Animation")

        viewRechteck = self.view.rect()
        viewRechteck.setSize(QSize(600, 600))
        self.szene = QGraphicsScene(QRectF(viewRechteck), self.view)
        self.view.setScene(self.szene)

        self.startButton.clicked.connect(self.main)
        self.slideTimer.timeout.connect(self.animier)
        self.delayTimer.timeout.connect(self.main)
        self.fertig.connect(self.delayTimer.start)

        self.erstellen()
        self.fill()

    def erstellen(self):
        for i in range(self.breite):
            for j in range(self.breite):
                block = QGraphicsRectItem(0, 0, self.bestSize, self.bestSize)
                block.setPos(i * self.bestSize, j * self.bestSize)
                self.szene.addItem(block)
                self.bloecke.update({(j, i): block})

    def wert(self, pos):
        return abs(pos[0] - self.feld[pos][0]) + \
            abs(pos[1] - self.feld[pos][1])

    def farbe(self, pos):
        return int(120 * (1 - self.wert(pos) / self.maxwert))

    def fill(self):
        self.maxwert = max(map(self.wert, self.feld))
        if self.maxwert == 0:
            # Niemand hat die Absicht durch 0 zu teilen
            self.maxwert = 1
        for j in range(self.breite):
            for i in range(self.breite):
                col = self.farbe((i, j))
                block = self.bloecke[i, j]
                bound = block.boundingRect()

                pos = (self.feld[i, j][0], self.feld[i, j][1])
                text = QGraphicsSimpleTextItem(str(pos), block)
                font = text.font()
                font.setPixelSize(self.bestSize // 4)
                text.setFont(font)
                textBound = text.boundingRect()
                text_x = bound.width() / 2 - textBound.width() / 2
                text_y = bound.height() / 2 - textBound.height() / 2
                text.setPos(text_x, text_y)
                block.setBrush(QColor.fromHsv(col, 0xff, 0xff, 0x90))

    def ende(self):
        self.startButton.setText("Schließen")
        self.startButton.setEnabled(True)
        self.startButton.clicked.connect(self.close)

    @pyqtSlot()
    def main(self):
        self.stepcounter += 1
        self.startButton.setEnabled(False)
        self.delayTimer.stop()
        self.move = {}
        if len(self.log[0, 0]) == 0:
            self.ende()
            return
        self.setWindowTitle(
            "Frame %s von %s" %
            (self.stepcounter, self.maxsteps))
        newfeld = {}
        for i in self.log:
            self.move.update({i: self.log[i].pop(0)})
            newfeld.update({self.add(i, self.move[i]): self.feld[i]})
        self.feld = newfeld
        self.counter = 0
        self.slideTimer.start()

    def animier(self):
        if self.counter == self.steps:
            for i in self.bloecke:
                self.szene.removeItem(self.bloecke[i])
            self.erstellen()
            self.fill()
            self.slideTimer.stop()
            self.fertig.emit()
        else:
            self.counter += 1
            for i in self.move:
                pos = self.bloecke[i].pos() + QPointF(self.delta * self.move[i][1],
                                                      self.delta * self.move[i][0])
                self.bloecke[i].setPos(pos)
