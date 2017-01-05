import io
import json
import os
from threading import Thread

import matplotlib.pyplot as plt
import sys
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSizePolicy

from gl import GLWidget
from process import *


def run_in_thread(func):
    def thread_func(ins):
        func_hl = Thread(target=func, args=(ins,))
        func_hl.start()
        return func_hl
    return thread_func

text = """$\\mathbf{Количество\,\,удаляемого\,\,растворителя:}$
  $W=G_{\\mathrm{н}}(1-\\frac{x_{\\mathrm{н}}}{x_{\\mathrm{к}}})$
  $W=%s\\left(1-\\frac{%s}{%s}\\right)=%s\\frac{\\mathrm{к}\\mathrm{г}}{\\mathrm{с}}$
$\\mathbf{Тепловой\,\,поток:}$
  $Q=1.05*(G_{\\mathrm{н}}c_{\\mathrm{н}}\\left(t_k-t_{\\mathrm{н}}\\right)+W\\left(i_{\\mathrm{в}\\mathrm{т}.\\mathrm{п}.}-c_{\\mathrm{в}}t_{\\mathrm{к}}\\right))$
  $Q=1.05*(%s*%s(%s-%s)+$
    $%s(%s-%s*%s))=%s\\ \\mathrm{В}\\mathrm{Т}$
$\\mathbf{Необходимый\,\,расход\,\,пара:}$
  $G_{\\mathrm{г}.\\mathrm{п}}=\\frac{Q}{r_{\\mathrm{г}.\\mathrm{п}}*x}$
  $G_{\\mathrm{г}.\\mathrm{п}}=\\frac{%s}{%s*%s}=%s\\ \\mathrm{к}\\mathrm{г}/\\mathrm{с}$
$\\mathbf{Удельный\,\,расход\,\,пара:}$
  $d=\\frac{G_{\\mathrm{г}.\\mathrm{п}}}{W}$
  $d=\\frac{%s}{%s}=%s$
$\\mathbf{Высота\,\,слоя\,\,раствора:}$
  $H_{\\mathrm{у}\\mathrm{р}}=[0.26+0.0014\\left({\\rho }_{\\mathrm{р}}-{\\rho }_{\\mathrm{в}}\\right)]H_{\\mathrm{т}\\mathrm{р}}$
  $H_{\\mathrm{у}\\mathrm{р}}=\\left[0.26+0.0014\\left(%s-1000\\right)\\right]4=%s \\mathrm{м}$
$\\mathbf{Необходимая\,\,площадь\,\,теплопередачи:}$
  $F=\\frac{Q}{K\\Delta t_{\\mathrm{п}\\mathrm{о}\\mathrm{л}}}$
  $F=\\frac{%s}{%s*%s}=%s \\mathrm{м}^2$"""


class MainFrame(QMainWindow):
    showErrorMessage = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        filename = 'gui.ui'
        if hasattr(sys, '_MEIPASS'):
            filename = os.path.join(sys._MEIPASS, filename)
        uic.loadUi(filename, self)
        self.init_ui()

    def init_ui(self):
        """инициализирует гуи"""
        self.imageLabel.resizeEvent = self.draw_pixmap
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.progressBar.hide()
        self.showErrorMessage.connect(self.display_error)
        self.pushButton_calculate.clicked.connect(self.calculate)
        self.action_load.triggered.connect(self.load_data)
        self.action_save.triggered.connect(self.save_data)
        self.action_about.triggered.connect(self.show_about)
        self.action_calculate.triggered.connect(self.calculate)

        self.glWidget = GLWidget()
        self.horizontalLayout.removeWidget(self.graphicsView)
        self.graphicsView.deleteLater()
        self.horizontalLayout.addWidget(self.glWidget)
        self.glWidget.setFixedWidth(350)
        self.glWidget.setXRotation(85 * 16)
        self.glWidget.setYRotation(180 * 16)
        self.glWidget.setZRotation(90 * 16)

        self.show()

    def show_about(self):
        about = QMessageBox()
        about.setWindowTitle("О программе")
        about.setText('Программа, разработанная в рамках курса "Теория и технология программирования", Дмитрий Богер'
                      '\nИсходный код: github.com/b0g3r/prog_cw')
        about.exec_()

    def save_data(self):
        """сохраняет в json"""
        data = {
            'solvent': {
                "capacity": self.dsb_solvent_capacity.value(),
                "density": self.dsb_solvent_density.value(),
                "molar_mass": self.dsb_solvent_molar_mass.value(),
                "boil_temp": self.dsb_solvent_boil_temp.value(),
                "tough": self.dsb_solvent_tough.value()
            },
            'solute': {
                "capacity": self.dsb_solute_capacity.value(),
                "density": self.dsb_solute_density.value(),
                "molar_mass": self.dsb_solute_molar_mass.value(),
                "boil_temp": self.dsb_solute_boil_temp.value(),
                "melting_temp": self.dsb_solute_melting_temp.value(),
                "solubility": self.dsb_solute_solubility.value()
            },
            'solution': {
                "start_conc": self.dsb_solution_start_conc.value(),
                "final_conc": self.dsb_solution_final_conc.value(),
                "start_temp": self.dsb_solution_start_temp.value(),
                "final_temp": self.dsb_solution_final_temp.value(),
                "start_consumption": self.dsb_solution_start_consumption.value()
            },
            'steam': {
                "start_temp": self.dsb_steam_start_temp.value(),
                "final_temp": self.dsb_steam_final_temp.value(),
                "consumption": self.dsb_steam_consumption.value()
            },
            'machine': {
                "pipe_height": self.dsb_machine_pipe_height.value(),
                "height": self.dsb_machine_height.value(),
                "pipe_diameter": self.dsb_machine_pipe_diameter.value()
            }
        }
        json.dump(data,
                  open(QFileDialog().getSaveFileName(self, 'Save file', os.getcwd(), "process files (*.json)")[0], 'w'),
                  indent=4)

    def load_data(self):
        fname = QFileDialog().getOpenFileName(self, 'Open file',
                                              os.getcwd(), "process files (*.json)")[0]
        self.set_gui_fields(json.load(open(fname)))

    def display_error(self, error):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setWindowTitle("Ошибка")
        error_dialog.setText(str(error))
        error_dialog.exec_()

    def create_process(self):
        try:
            solvent = Solvent(capacity=self.dsb_solvent_capacity.value(),
                              density=self.dsb_solvent_density.value(),
                              molar_mass=self.dsb_solvent_molar_mass.value(),
                              boil_temp=self.dsb_solvent_boil_temp.value(),
                              tough=self.dsb_solvent_tough.value())
            solute = Solute(capacity=self.dsb_solute_capacity.value(),
                            density=self.dsb_solute_density.value(),
                            molar_mass=self.dsb_solute_molar_mass.value(),
                            boil_temp=self.dsb_solute_boil_temp.value(),
                            melting_temp=self.dsb_solute_melting_temp.value(),
                            solubility=self.dsb_solute_solubility.value())
            solution = Solution(solute=solute,
                                solvent=solvent,
                                start_conc=self.dsb_solution_start_conc.value(),
                                final_conc=self.dsb_solution_final_conc.value(),
                                start_temp=self.dsb_solution_start_temp.value(),
                                final_temp=self.dsb_solution_final_temp.value(),
                                start_consumption=self.dsb_solution_start_consumption.value())
            steam = Steam(start_temp=self.dsb_steam_start_temp.value(),
                          final_temp=self.dsb_steam_final_temp.value(),
                          consumption=self.dsb_steam_consumption.value())
            machine = Machine(pipe_height=self.dsb_machine_pipe_height.value(),
                              height=self.dsb_machine_height.value(),
                              pipe_diameter=self.dsb_machine_pipe_diameter.value())
        except PropertyError as e:
            self.showErrorMessage.emit(e.message)
            return None
        else:
            solution.other['enthalpy'] = steam.enthalpy
            steam.other['Q'] = solution.Q
            steam.other['W'] = solution.W
            machine.other['start_conc'] = solution.start_conc
            machine.other['Q'] = solution.Q
            machine.other['start_temp'] = steam.start_temp
            return solvent, solute, solution, steam, machine

    def set_gui_fields(self, data: dict):
        for unit, data in data.items():
            for prop, val in data.items():
                getattr(self, 'dsb_%s_%s' % (unit, prop)).setValue(val)

    @pyqtSlot(name='calculate')
    @run_in_thread
    def calculate(self):
        """считает всё ;)"""
        self.progressBar.show()
        try:
            process = self.create_process()
            if process is not None:
                solvent, solute, solution, steam, machine = process
                self.pixmap = self.create_pixmap(solvent, solution, steam, machine)
                self.draw_pixmap()
        except Exception as e:
            self.showErrorMessage.emit(str(e))
        self.progressBar.hide()

    def create_pixmap(self, solvent: Solvent, solution: Solution,
                      steam: Steam, machine: Machine):
        """генерирует из latex пиксмап"""
        plt.cla()
        plt.rc('font', **{'family': 'Verdana', 'weight': 'normal'})

        plt.text(0, 0,
                 text % (
                     solution.start_consumption, solution.start_conc, solution.final_conc, solution.W,
                     solution.start_consumption, solution.start_capacity, solution.final_temp,
                     solution.start_temp, solution.W,
                     solution.other['enthalpy'], solvent.capacity, solution.final_temp, solution.Q,
                     solution.Q, steam.rgp, steam.x, round(steam.final_consumption, 4),
                     round(steam.final_consumption, 4), solution.W, round(steam.D, 4),
                     (machine.density + 10 * (solution.start_conc * 100 - 1)), round(machine.level, 4),
                     solution.Q, machine.K, (steam.start_temp - machine.boil_temp), round(machine.F, 4)),
                 fontsize=14, clip_on=False)
        # hide axes
        fig = plt.gca()
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)
        fig.axes.axis('off')
        fig.patch.set_visible(False)
        bytes_io = io.BytesIO()
        plt.savefig(bytes_io, format='png', bbox_inches='tight')
        bytes_io.seek(0)
        return QPixmap().fromImage(QImage().fromData(bytes_io.read()))

    def draw_pixmap(self, event=None):
        if hasattr(self, 'pixmap'):
            self.imageLabel.setPixmap(
                self.pixmap.scaled(self.imageLabel.width(),
                                   self.imageLabel.height(),
                                   Qt.KeepAspectRatioByExpanding,
                                   Qt.SmoothTransformation
            ))


