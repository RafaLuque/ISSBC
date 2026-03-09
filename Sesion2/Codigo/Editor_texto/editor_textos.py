
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Editor de Texto Sencillo - Practica 2
Operaciones: Nuevo, Abrir, Guardar, Guardar como
Autor: Rafael Luque Laplana
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, 
                             QApplication, QFileDialog, QMessageBox)
from PyQt5.QtGui import QIcon

class EditorSencillo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ruta_archivo = None
        self.initUI()

    def initUI(self):
        # Widget central
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)

        # Crear acciones
        self.crear_acciones()

        # Crear menu (solo Archivo)
        self.crear_menu()

        # Configuracion ventana
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Editor Sencillo')
        self.show()

    def crear_acciones(self):
        # Accion Nuevo
        self.nuevoAct = QAction('&Nuevo', self)
        self.nuevoAct.setShortcut('Ctrl+N')
        self.nuevoAct.triggered.connect(self.nuevo_documento)
        self.nuevoAct.setIcon(QIcon("Imagenes/nuevo.png"))

        # Accion Abrir
        self.abrirAct = QAction('&Abrir...', self)
        self.abrirAct.setShortcut('Ctrl+O')
        self.abrirAct.triggered.connect(self.abrir_documento)
        self.abrirAct.setIcon(QIcon("Imagenes/abrir.png"))


        # Accion Guardar
        self.guardarAct = QAction('&Guardar', self)
        self.guardarAct.setShortcut('Ctrl+S')
        self.guardarAct.triggered.connect(self.guardar_documento)
        self.guardarAct.setIcon(QIcon("Imagenes/guardar.png"))


        # Accion Guardar como
        self.guardarComoAct = QAction('Guardar &como...', self)
        self.guardarComoAct.setShortcut('Ctrl+Shift+S')
        self.guardarComoAct.triggered.connect(self.guardar_como_documento)

        # Accion Salir
        self.salirAct = QAction('&Salir', self)
        self.salirAct.setShortcut('Ctrl+Q')
        self.salirAct.triggered.connect(self.close)
        self.salirAct.setIcon(QIcon("Imagenes/salir.png"))

    def crear_menu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Archivo')
        fileMenu.addAction(self.nuevoAct)
        fileMenu.addAction(self.abrirAct)
        fileMenu.addAction(self.guardarAct)
        fileMenu.addAction(self.guardarComoAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.salirAct)

    def nuevo_documento(self):
        if self.textEdit.document().isModified():
            reply = QMessageBox.question(self, 'Nuevo',
                                        'Crear nuevo sin guardar?',
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        self.textEdit.clear()
        self.ruta_archivo = None
        self.setWindowTitle('Editor Sencillo')

    def abrir_documento(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Abrir archivo',
                                               '.', 'Textos (*.txt)')
        if fname:
            with open(fname, 'r') as f:
                self.textEdit.setText(f.read())
            self.ruta_archivo = fname
            self.setWindowTitle(f'Editor Sencillo - {fname}')

    def guardar_documento(self):
        if self.ruta_archivo:
            with open(self.ruta_archivo, 'w') as f:
                f.write(self.textEdit.toPlainText())
        else:
            self.guardar_como_documento()

    def guardar_como_documento(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Guardar como',
                                               '.', 'Textos (*.txt)')
        if fname:
            with open(fname, 'w') as f:
                f.write(self.textEdit.toPlainText())
            self.ruta_archivo = fname
            self.setWindowTitle(f'Editor Sencillo - {fname}')

    def closeEvent(self, event):
        if self.textEdit.document().isModified():
            reply = QMessageBox.question(self, 'Salir',
                                        'Salir sin guardar?',
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()

def main():
    app = QApplication(sys.argv)
    ex = EditorSencillo()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()