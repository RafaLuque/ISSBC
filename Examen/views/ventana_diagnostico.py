from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class VentanaDiagnostico(QWidget):
    """
    Ventana que muestra el diagnóstico final
    """
    
    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setWindowTitle("Diagnóstico - Configuración Recomendada")
        self.setGeometry(150, 150, 600, 500)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.init_ui()
        self.actualizar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("<h2>Diagnóstico: Configuración recomendada</h2>")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Área de texto con el diagnóstico
        self.texto_diagnostico = QTextEdit()
        self.texto_diagnostico.setReadOnly(True)
        self.texto_diagnostico.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.texto_diagnostico)
        
        # Nivel de confianza (simulado)
        self.label_confianza = QLabel()
        self.label_confianza.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_confianza)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_exportar = QPushButton("Exportar diagnóstico")
        btn_exportar.clicked.connect(self.exportar_diagnostico)
        botones_layout.addWidget(btn_exportar)
        
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_datos)
        botones_layout.addWidget(btn_actualizar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones_layout.addWidget(btn_cerrar)
        
        layout.addLayout(botones_layout)
    
    def actualizar_datos(self):
        """Actualiza el diagnóstico desde el modelo"""
        diagnostico = self.controlador.modelo.diagnostico_final
        if diagnostico:
            self.texto_diagnostico.setText(diagnostico)
            self.label_confianza.setText("🔵 Nivel de confianza: 85% (simulado)")
        else:
            self.texto_diagnostico.setText("No hay diagnóstico disponible. Genera uno primero.")
            self.label_confianza.setText("")
    
    def exportar_diagnostico(self):
        """Exporta el diagnóstico a un archivo de texto"""
        diagnostico = self.controlador.modelo.diagnostico_final
        if not diagnostico:
            QMessageBox.warning(self, "Aviso", "No hay diagnóstico para exportar")
            return
        
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar diagnóstico", "diagnostico_pc.txt", "Archivos de texto (*.txt)"
        )
        
        if ruta:
            try:
                with open(ruta, 'w', encoding='utf-8') as f:
                    f.write("=== DIAGNÓSTICO DE CONFIGURACIÓN DE PC ===\n\n")
                    f.write(diagnostico)
                    f.write(f"\n\n---\nGenerado el: {QDateTime.currentDateTime().toString('dd/MM/yyyy hh:mm')}")
                QMessageBox.information(self, "Éxito", "Diagnóstico exportado correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar: {str(e)}")# -*- coding: utf-8 -*-

