from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from process import *


class MainFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'gui.ui', self)
        self.init_ui()

    def init_ui(self):
        """инициализирует гуи"""
        self.show()
        self.calculate()

    def calculate(self):
        """высчитывает"""
        s = Substance(1,2,3,5)
        print(s.capacity)

