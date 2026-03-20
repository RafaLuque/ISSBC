# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QGridLayout,
                             QListWidget, QTextEdit, QFileDialog,
                             QMessageBox, QApplication)
from PyQt5.QtCore import Qt
import controlador as ctrl

class EditorMVC(QWidget):
    def __init__(self):
        super().__init__()
        self.directorio_actual = None
        self.archivo_actual = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Editor de archivos")
        self.setMinimumSize(700, 500)
        
        # --- Widgets ---
        # Fila de carpeta
        self.label_carpeta = QLabel("Carpeta:")
        self.line_carpeta = QLineEdit()
        self.line_carpeta.setReadOnly(True)
        self.boton_seleccionar = QPushButton("Seleccionar")
        
        # Lista de archivos
        self.label_archivos = QLabel("Archivos")
        self.lista_archivos = QListWidget()
        
        # Área de edición
        self.editor = QTextEdit()
        
        # Botones de acción
        self.boton_salvar = QPushButton("Salvar")
        self.boton_salvar_como = QPushButton("Salvar como")
        
        # --- Layouts ---
        # Layout para la fila de carpeta
        fila_carpeta = QHBoxLayout()
        fila_carpeta.addWidget(self.label_carpeta)
        fila_carpeta.addWidget(self.line_carpeta)
        fila_carpeta.addWidget(self.boton_seleccionar)
        
        # Layout para el área de archivos y editor
        area_principal = QHBoxLayout()
        
        # Layout izquierdo (lista de archivos)
        layout_izquierdo = QVBoxLayout()
        layout_izquierdo.addWidget(self.label_archivos)
        layout_izquierdo.addWidget(self.lista_archivos)
        
        # Layout derecho (editor)
        layout_derecho = QVBoxLayout()
        layout_derecho.addWidget(self.editor)
        
        area_principal.addLayout(layout_izquierdo, 1)
        area_principal.addLayout(layout_derecho, 3)
        
        # Layout para los botones de salvar
        fila_botones = QHBoxLayout()
        fila_botones.addStretch()
        fila_botones.addWidget(self.boton_salvar)
        fila_botones.addWidget(self.boton_salvar_como)
        fila_botones.addStretch()
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.addLayout(fila_carpeta)
        layout_principal.addLayout(area_principal)
        layout_principal.addLayout(fila_botones)
        
        self.setLayout(layout_principal)
        
        # --- Conexiones de eventos ---
        self.boton_seleccionar.clicked.connect(self.seleccionar_carpeta)
        self.lista_archivos.itemDoubleClicked.connect(self.abrir_archivo)
        self.boton_salvar.clicked.connect(self.guardar_archivo)
        self.boton_salvar_como.clicked.connect(self.guardar_como_archivo)
        
        self.setGeometry(300, 300, 800, 500)
        self.show()
    
    def seleccionar_carpeta(self):
        """Abre un diálogo para seleccionar una carpeta."""
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if directorio:
            self.directorio_actual = directorio
            self.line_carpeta.setText(directorio)
            self.actualizar_lista_archivos()
    
    def actualizar_lista_archivos(self):
        """Actualiza la lista de archivos del directorio actual."""
        if not self.directorio_actual:
            return
        
        archivos = ctrl.listar_archivos(self.directorio_actual)
        self.lista_archivos.clear()
        for archivo in archivos:
            self.lista_archivos.addItem(archivo)
    
    def abrir_archivo(self, item):
        """Abre el archivo seleccionado en el editor."""
        nombre_archivo = item.text()
        ruta_completa = os.path.join(self.directorio_actual, nombre_archivo)
        
        contenido = ctrl.abrir_archivo(ruta_completa)
        if contenido is not None:
            self.editor.setText(contenido)
            self.archivo_actual = ruta_completa
            self.setWindowTitle(f"Editor de archivos - {nombre_archivo}")
        else:
            QMessageBox.warning(self, "Error", f"No se pudo abrir el archivo:\n{ruta_completa}")
    
    def guardar_archivo(self):
        """Guarda el contenido en el archivo actual."""
        if not self.archivo_actual:
            self.guardar_como_archivo()
            return
        
        contenido = self.editor.toPlainText()
        if ctrl.guardar_archivo(self.archivo_actual, contenido):
            nombre_archivo = os.path.basename(self.archivo_actual)
            self.setWindowTitle(f"Editor de archivos - {nombre_archivo}")
            QMessageBox.information(self, "Guardado", "Archivo guardado correctamente.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar el archivo.")
    
    def guardar_como_archivo(self):
        """Guarda el contenido en un nuevo archivo."""
        if not self.directorio_actual:
            QMessageBox.warning(self, "Error", "Primero seleccione una carpeta.")
            return
        
        nombre_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo", self.directorio_actual, "Archivos de texto (*.txt)"
        )
        
        if nombre_archivo:
            contenido = self.editor.toPlainText()
            if ctrl.guardar_archivo(nombre_archivo, contenido):
                self.archivo_actual = nombre_archivo
                nombre = os.path.basename(nombre_archivo)
                self.setWindowTitle(f"Editor de archivos - {nombre}")
                self.actualizar_lista_archivos()
                QMessageBox.information(self, "Guardado", "Archivo guardado correctamente.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar el archivo.")

def main():
    app = QApplication(sys.argv)
    ventana = EditorMVC()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()