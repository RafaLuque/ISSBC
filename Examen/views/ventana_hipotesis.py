from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class VentanaHipotesis(QWidget):
    """
    Ventana para mostrar las hipótesis generadas.
    Implementa Model/View para mostrar datos estructurados.
    """
    
    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setWindowTitle("Hipótesis - Diagnóstico PC")
        self.setGeometry(150, 150, 600, 400)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.init_ui()
        self.actualizar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("<h2>Hipótesis de configuración</h2>")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabla de hipótesis
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Hipótesis", "Probabilidad", "Estado"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        layout.addWidget(self.tabla)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_seleccionar = QPushButton("Seleccionar para diagnóstico")
        btn_seleccionar.clicked.connect(self.seleccionar_hipotesis)
        botones_layout.addWidget(btn_seleccionar)
        
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_datos)
        botones_layout.addWidget(btn_actualizar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones_layout.addWidget(btn_cerrar)
        
        layout.addLayout(botones_layout)
    
    def actualizar_datos(self):
        """Actualiza la tabla con las hipótesis del modelo"""
        hipotesis = self.controlador.modelo.hipotesis
        
        self.tabla.setRowCount(len(hipotesis))
        
        for i, h in enumerate(hipotesis):
            # Hipótesis
            item_nombre = QTableWidgetItem(h.get('nombre', ''))
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable)
            self.tabla.setItem(i, 0, item_nombre)
            
            # Probabilidad
            prob = h.get('probabilidad', 0)
            item_prob = QTableWidgetItem(f"{prob:.1%}")
            item_prob.setFlags(item_prob.flags() & ~Qt.ItemIsEditable)
            
            # Colorear según probabilidad
            if prob >= 0.8:
                item_prob.setBackground(QColor(0, 255, 0, 50))  # Verde claro
            elif prob >= 0.5:
                item_prob.setBackground(QColor(255, 255, 0, 50))  # Amarillo claro
            else:
                item_prob.setBackground(QColor(255, 0, 0, 50))  # Rojo claro
            
            self.tabla.setItem(i, 1, item_prob)
            
            # Estado
            estado = h.get('estado', '')
            item_estado = QTableWidgetItem(estado)
            item_estado.setFlags(item_estado.flags() & ~Qt.ItemIsEditable)
            self.tabla.setItem(i, 2, item_estado)
        
        self.tabla.resizeColumnsToContents()
    
    def seleccionar_hipotesis(self):
        """Selecciona la hipótesis actual para diagnóstico"""
        fila = self.tabla.currentRow()
        if fila >= 0:
            hipotesis = self.controlador.modelo.hipotesis[fila]
            self.controlador.diagnosticar(hipotesis)
            QMessageBox.information(self, "Información", 
                                   f"Hipótesis seleccionada: {hipotesis.get('nombre', '')}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecciona una hipótesis")# -*- coding: utf-8 -*-

