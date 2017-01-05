
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from gui import MainFrame





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainFrame()

    sys._excepthook = sys.excepthook
    def my_exception_hook(exctype, value, traceback):
        # fix unhandled exception
        ex.showErrorMessage.emit(str(value))
        sys._excepthook(exctype, value, traceback)

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())

