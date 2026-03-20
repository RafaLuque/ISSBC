# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from vista import EditorMVC

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = EditorMVC()
    ventana.show()
    sys.exit(app.exec_())