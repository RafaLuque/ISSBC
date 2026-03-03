#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ejercicio Final - Práctica 1
Aplicación integradora de conceptos PyQt5
Autor: Rafael Luque Laplana
Asignatura: ISSBC
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QMenu, 
                             QApplication, QMessageBox, qApp, QDialog,
                             QVBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

class VentanaEdicion(QDialog):
    """
    Ventana secundaria de edición de texto.
    Cada nueva ventana tiene su propio área de texto.
    """
    
    def __init__(self, titulo="Ventana nueva", texto_inicial=""):
        super().__init__()
        self.setWindowTitle(titulo)
        self.setGeometry(450, 150, 400, 300)
        
        # Tooltip para la ventana
        self.setToolTip('Ventana de edición independiente')
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Área de texto
        self.textEdit = QTextEdit()
        self.textEdit.setText(texto_inicial)
        self.textEdit.setToolTip('Escribe aquí tu texto')
        layout.addWidget(self.textEdit)
        
        # Botón para cerrar
        btn_cerrar = QPushButton('Cerrar ventana')
        btn_cerrar.setToolTip('Cerrar esta ventana')
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)
        
        self.setLayout(layout)

class VentanaPrincipal(QMainWindow):
    """
    Clase principal de la aplicación.
    Permite crear múltiples ventanas de edición.
    """
    
    def __init__(self):
        super().__init__()
        self.ventanas_secundarias = []  # Lista para mantener referencias
        self.initUI()
    
    def initUI(self):
        """Inicializa todos los elementos de la interfaz"""
        
        # Configuración básica de la ventana
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Visor de Ventanas - Práctica 1')
        
        # Tooltip para la ventana principal
        self.setToolTip('Ventana principal\nCrea nuevas ventanas desde el menú')
        
        # Intentar establecer un icono (si existe)
        try:
            self.setWindowIcon(QIcon('imagenes/icono.png'))
        except:
            pass
        
        
        # Crear todas las acciones
        self.crear_acciones()
        
        # Crear los menús
        self.crear_menus()
        
        # Crear la barra de herramientas
        self.crear_barra_herramientas()
        
        # Crear la barra de estado
        self.crear_barra_estado()
        
        self.show()
    
    def crear_acciones(self):
        """Crea todas las acciones QAction utilizadas en la aplicación"""
        
        # --- Acciones del menú Archivo ---
        
        # Acción Nueva ventana vacía
        self.nuevaVentanaAct = QAction('&Ventana vacía', self)
        self.nuevaVentanaAct.setShortcut('Ctrl+N')
        self.nuevaVentanaAct.setStatusTip('Crear una nueva ventana vacía')
        self.nuevaVentanaAct.setToolTip('Nueva ventana vacía (Ctrl+N)')
        self.nuevaVentanaAct.triggered.connect(self.crear_ventana_vacia)
        try:
            self.nuevaVentanaAct.setIcon(QIcon('imagenes/nuevo.png'))
        except:
            pass
        
        # Acción Nueva ventana con texto
        self.nuevaVentanaTextoAct = QAction('Ventana con &texto', self)
        self.nuevaVentanaTextoAct.setShortcut('Ctrl+T')
        self.nuevaVentanaTextoAct.setStatusTip('Crear una nueva ventana con texto de ejemplo')
        self.nuevaVentanaTextoAct.setToolTip('Nueva ventana con texto (Ctrl+T)')
        self.nuevaVentanaTextoAct.triggered.connect(self.crear_ventana_con_texto)
        
        # Acción Salir
        self.salirAct = QAction('&Salir', self)
        self.salirAct.setShortcut('Ctrl+Q')
        self.salirAct.setStatusTip('Salir de la aplicación')
        self.salirAct.setToolTip('Salir (Ctrl+Q)')
        self.salirAct.triggered.connect(self.cerrar_aplicacion)
        try:
            self.salirAct.setIcon(QIcon('imagenes/salir.png'))
        except:
            pass
        
        # --- Acción del menú Ver (checkeable) ---
        
        self.verStatusAct = QAction('Ver &barra de estado', self, checkable=True)
        self.verStatusAct.setChecked(True)
        self.verStatusAct.setStatusTip('Mostrar u ocultar la barra de estado')
        self.verStatusAct.triggered.connect(self.toggle_statusbar)
        
        # --- Acción del menú Ayuda ---
        
        self.acercaAct = QAction('&Acerca de', self)
        self.acercaAct.setStatusTip('Información sobre la aplicación')
        self.acercaAct.triggered.connect(self.acerca_de)
    
    def crear_menus(self):
        """Crea la barra de menú y todos los menús"""
        
        menubar = self.menuBar()
        
        # --- Menú Archivo con submenú ---
        fileMenu = menubar.addMenu('&Archivo')
        
        # Submenú "Nueva"
        nuevoMenu = QMenu('&Nueva', self)
        nuevoMenu.setToolTip('Crear nueva ventana')
        nuevoMenu.addAction(self.nuevaVentanaAct)
        nuevoMenu.addAction(self.nuevaVentanaTextoAct)
        
        fileMenu.addMenu(nuevoMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.salirAct)
        
        # --- Menú Ver ---
        viewMenu = menubar.addMenu('&Ver')
        viewMenu.addAction(self.verStatusAct)
        
        # --- Menú Ayuda ---
        helpMenu = menubar.addMenu('Ay&uda')
        helpMenu.addAction(self.acercaAct)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas con las acciones principales"""
        
        toolbar = self.addToolBar('Principal')
        toolbar.setToolTip('Barra de herramientas principal')
        
        toolbar.addAction(self.nuevaVentanaAct)
        toolbar.addAction(self.nuevaVentanaTextoAct)
        toolbar.addSeparator()
        toolbar.addAction(self.salirAct)
    
    def crear_barra_estado(self):
        """Crea la barra de estado"""
        self.actualizar_barra_estado()
        
        # Asignar mensajes de estado a las acciones
        self.nuevaVentanaAct.setStatusTip('Crear una nueva ventana vacía')
        self.nuevaVentanaTextoAct.setStatusTip('Crear una nueva ventana con texto de ejemplo')
        self.salirAct.setStatusTip('Salir de la aplicación')
        self.verStatusAct.setStatusTip('Mostrar u ocultar la barra de estado')
        self.acercaAct.setStatusTip('Información sobre la aplicación')
    
    def actualizar_barra_estado(self):
        """Actualiza el mensaje de la barra de estado"""
        num_ventanas = len(self.ventanas_secundarias)
        mensaje = f'Listo - Ventanas abiertas: {num_ventanas}'
        self.statusBar().showMessage(mensaje)
    
    def contextMenuEvent(self, event):
        """Método para crear el menú contextual (clic derecho)"""
        cmenu = QMenu(self)
        
        nuevoMenu = cmenu.addMenu('Nueva ventana')
        nuevoMenu.addAction(self.nuevaVentanaAct)
        nuevoMenu.addAction(self.nuevaVentanaTextoAct)
        
        cmenu.addSeparator()
        
        salirAct = cmenu.addAction('Salir')
        salirAct.triggered.connect(self.cerrar_aplicacion)
        
        cmenu.exec_(self.mapToGlobal(event.pos()))
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        self.cerrar_aplicacion()
        event.ignore()
    
    def crear_ventana_vacia(self):
        """Crea una nueva ventana vacía"""
        ventana = VentanaEdicion(f"Ventana {len(self.ventanas_secundarias) + 1}")
        
        # Conectar señal de cierre para actualizar contador
        ventana.destroyed.connect(self.actualizar_barra_estado)
        
        ventana.show()
        self.ventanas_secundarias.append(ventana)
        self.actualizar_barra_estado()
        self.statusBar().showMessage('Nueva ventana creada', 2000)
    
    def crear_ventana_con_texto(self):
        """Crea una nueva ventana con texto de ejemplo"""
        texto = "Este es un texto de ejemplo.\nPuedes modificarlo libremente."
        ventana = VentanaEdicion(f"Ventana {len(self.ventanas_secundarias) + 1}", texto)
        
        # Conectar señal de cierre para actualizar contador
        ventana.destroyed.connect(self.actualizar_barra_estado)
        
        ventana.show()
        self.ventanas_secundarias.append(ventana)
        self.actualizar_barra_estado()
        self.statusBar().showMessage('Nueva ventana con texto creada', 2000)
    
    def toggle_statusbar(self, state):
        """Muestra u oculta la barra de estado según el estado del check"""
        if state:
            self.statusBar().show()
            self.actualizar_barra_estado()
        else:
            self.statusBar().hide()
    
    def acerca_de(self):
        """Muestra información sobre la aplicación"""
        QMessageBox.about(self, 'Acerca de',
                         '<h2>Visor de Ventanas - Práctica 1</h2>'
                         '<p><b>Autor:</b> Rafael Luque Laplana</p>'
                         '<p><b>Asignatura:</b> ISSBC</p>'
                         '<p><b>Descripción:</b> Aplicación que permite crear '
                         'múltiples ventanas de edición independientes.</p>'
                         '<p><b>Conceptos demostrados:</b></p>'
                         '<ul>'
                         '<li>Ventana principal (QMainWindow)</li>'
                         '<li>Ventanas secundarias (QDialog)</li>'
                         '<li>Menús y submenús</li>'
                         '<li>Acciones checkeables</li>'
                         '<li>Menú contextual</li>'
                         '<li>Barra de herramientas</li>'
                         '<li>Barra de estado</li>'
                         '<li>Tooltips</li>'
                         '<li>Diálogos (QMessageBox)</li>'
                         '<li>Señales y slots</li>'
                         '</ul>')
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación con confirmación"""
        num_ventanas = len(self.ventanas_secundarias)
        
        
        mensaje = 'Si tiene alguna ventana abierta se cerrará junto a la aplicación\n¿Estás seguro de que quieres salir?'
        
        reply = QMessageBox.question(self, 'Confirmar salida',
                                    mensaje,
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            qApp.quit()

def main():
    app = QApplication(sys.argv)
    
    ex = VentanaPrincipal()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()