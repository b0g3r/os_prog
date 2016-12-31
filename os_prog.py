
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from gui import MainFrame



def display_error(error):
    global error_dialog
    error_dialog.setText(str(error))
    error_dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Warning)
    error_dialog.setWindowTitle("Критическая ошибка")

    sys._excepthook = sys.excepthook
    def my_exception_hook(exctype, value, traceback):
        # fix unhandled exception
        display_error(value)
        sys._excepthook(exctype, value, traceback)

    sys.excepthook = my_exception_hook
    ex = MainFrame()
    sys.exit(app.exec_())

