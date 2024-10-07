import sys
import multiprocessing
from app.assistant import Assistant

from PyQt6.QtWidgets import QApplication, QWidget
def main():
    app = QApplication(sys.argv)
    ex = Assistant()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
