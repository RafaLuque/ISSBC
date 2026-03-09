#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demostrador de Conceptos PyQt5 - Practica 2
Incluye: menus, submenus, toolbar, statusbar, layouts
Basado en los tutoriales de ZetCode
Autor: Rafael Luque Laplana
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton,
                             QCheckBox, QLineEdit, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QGridLayout,
                             QAction, QMenu, QApplication, QMessageBox, qApp)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class Demostrador(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal
        layout = QVBoxLayout()

        # 1. Label informativo (como en absolute.py)
        self.label = QLabel('Demostrador de conceptos PyQt5')
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # 2. Layout horizontal para botones (como en box_layout.py)
        hbox = QHBoxLayout()
        btn1 = QPushButton('Boton 1')
        btn2 = QPushButton('Boton 2')
        btn3 = QPushButton('Boton 3')
        hbox.addWidget(btn1)
        hbox.addWidget(btn2)
        hbox.addWidget(btn3)
        layout.addLayout(hbox)

        # 3. Layout en cuadricula (como en calculator.py y review.py)
        grid = QGridLayout()
        grid.setSpacing(10)

        # Labels y campos de texto
        grid.addWidget(QLabel('Nombre:'), 0, 0)
        self.nombreEdit = QLineEdit()
        grid.addWidget(self.nombreEdit, 0, 1)

        grid.addWidget(QLabel('Email:'), 1, 0)
        self.emailEdit = QLineEdit()
        grid.addWidget(self.emailEdit, 1, 1)

        grid.addWidget(QLabel('Comentarios:'), 2, 0)
        self.comentariosEdit = QTextEdit()
        grid.addWidget(self.comentariosEdit, 2, 1, 3, 1)  # Ocupa 3 filas

        layout.addLayout(grid)

        # 4. Checkbox (como en check_menu.py pero en ventana)
        self.cb = QCheckBox('Habilitar opciones avanzadas')
        self.cb.toggle()
        self.cb.stateChanged.connect(self.cambiar_estado)
        layout.addWidget(self.cb)

        central.setLayout(layout)

        # Crear menus (como en simple_menu.py, submenu.py, check_menu.py)
        self.crear_menus()

        # Crear toolbar (como en toolbar.py)
        self.crear_toolbar()

        # Barra de estado (como en statusbar.py)
        self.statusBar().showMessage('Listo')

        # Conectar botones a slots
        btn1.clicked.connect(lambda: self.boton_pulsado('Boton 1'))
        btn2.clicked.connect(lambda: self.boton_pulsado('Boton 2'))
        btn3.clicked.connect(lambda: self.boton_pulsado('Boton 3'))

        self.setGeometry(300, 300, 500, 400)
        self.setWindowTitle('Demostrador PyQt5')
        self.show()

    def crear_menus(self):
        menubar = self.menuBar()

        # Menu Archivo (como en simple_menu.py)
        fileMenu = menubar.addMenu('&Archivo')

        # Submenu Nuevo (como en submenu.py)
        nuevoMenu = QMenu('&Nuevo', self)
        nuevoMenu.addAction('Documento')
        nuevoMenu.addAction('Proyecto')
        nuevoMenu.addAction('Ventana')
        fileMenu.addMenu(nuevoMenu)

        fileMenu.addSeparator()

        # Accion Salir con icono y atajo
        exitAct = QAction('&Salir', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Salir de la aplicacion')
        exitAct.triggered.connect(self.close)
        fileMenu.addAction(exitAct)

        # Menu Ver con accion checkeable (como en check_menu.py)
        viewMenu = menubar.addMenu('&Ver')
        self.statusAct = QAction('Ver barra de estado', self, checkable=True)
        self.statusAct.setChecked(True)
        self.statusAct.setStatusTip('Mostrar u ocultar la barra de estado')
        self.statusAct.triggered.connect(self.toggle_statusbar)
        viewMenu.addAction(self.statusAct)

        # Menu Ayuda
        helpMenu = menubar.addMenu('Ay&uda')
        aboutAct = QAction('&Acerca de', self)
        aboutAct.setStatusTip('Informacion sobre la aplicacion')
        aboutAct.triggered.connect(self.acerca_de)
        helpMenu.addAction(aboutAct)

    def crear_toolbar(self):
        # Barra de herramientas (como en toolbar.py)
        toolbar = self.addToolBar('Principal')

        # Acciones para la toolbar
        resetAct = QAction('Reset', self)
        resetAct.setStatusTip('Reiniciar formulario')
        resetAct.triggered.connect(self.reset_formulario)
        toolbar.addAction(resetAct)

        toolbar.addSeparator()

        infoAct = QAction('Info', self)
        infoAct.setStatusTip('Mostrar informacion')
        infoAct.triggered.connect(self.mostrar_info)
        toolbar.addAction(infoAct)

    def boton_pulsado(self, texto):
        """Slot para los botones"""
        self.statusBar().showMessage(f'Has pulsado: {texto}', 2000)
        self.label.setText(f'Ultimo boton: {texto}')

    def cambiar_estado(self, state):
        """Slot para el checkbox"""
        if state == Qt.Checked:
            self.statusBar().showMessage('Opciones avanzadas habilitadas')
            self.nombreEdit.setPlaceholderText('Introduce tu nombre')
            self.emailEdit.setPlaceholderText('Introduce tu email')
        else:
            self.statusBar().showMessage('Opciones avanzadas deshabilitadas')
            self.nombreEdit.setPlaceholderText('')
            self.emailEdit.setPlaceholderText('')

    def reset_formulario(self):
        """Reinicia todos los campos"""
        self.nombreEdit.clear()
        self.emailEdit.clear()
        self.comentariosEdit.clear()
        self.cb.setChecked(True)
        self.label.setText('Demostrador de conceptos PyQt5')
        self.statusBar().showMessage('Formulario reiniciado', 2000)

    def mostrar_info(self):
        """Muestra informacion de la aplicacion"""
        QMessageBox.information(self, 'Informacion',
                               'Esta aplicacion demuestra:\n'
                               '- Menus y submenus (simple_menu.py, submenu.py)\n'
                               '- Acciones checkeables (check_menu.py)\n'
                               '- Menu contextual (context_menu.py)\n'
                               '- Barra de herramientas (toolbar.py)\n'
                               '- Barra de estado (statusbar.py)\n'
                               '- Layouts: QHBoxLayout, QVBoxLayout, QGridLayout\n'
                               '- Widgets: QLabel, QPushButton, QCheckBox\n'
                               '- QLineEdit y QTextEdit (review.py)')

    def toggle_statusbar(self, state):
        """Muestra u oculta la barra de estado"""
        if state:
            self.statusBar().show()
            self.statusBar().showMessage('Barra de estado visible')
        else:
            self.statusBar().hide()

    def contextMenuEvent(self, event):
        """Menu contextual (como en context_menu.py)"""
        cmenu = QMenu(self)

        resetAct = cmenu.addAction('Reset')
        infoAct = cmenu.addAction('Info')
        cmenu.addSeparator()
        quitAct = cmenu.addAction('Salir')

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == resetAct:
            self.reset_formulario()
        elif action == infoAct:
            self.mostrar_info()
        elif action == quitAct:
            self.close()

    def acerca_de(self):
        """Dialogo Acerca de (como en messagebox.py)"""
        QMessageBox.about(self, 'Acerca de',
                          '<h2>Demostrador PyQt5</h2>'
                          '<p>Practica 2 - ISSBC</p>'
                          '<p>Rafael Luque Laplana</p>'
                          '<p>Basado en los tutoriales de ZetCode</p>')

def main():
    app = QApplication(sys.argv)
    ex = Demostrador()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
