from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class VentanaJustificacion(QWidget):
    """
    Ventana que muestra la justificación del diagnóstico
    """
    
    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setWindowTitle("Justificación del Diagnóstico")
        self.setGeometry(150, 150, 650, 500)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.init_ui()
        self.actualizar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("<h2>Justificación del diagnóstico</h2>")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Pestañas para organizar la información
        tabs = QTabWidget()
        
        # Pestaña: Explicación
        tab_explicacion = QWidget()
        tab_layout = QVBoxLayout(tab_explicacion)
        
        self.texto_justificacion = QTextEdit()
        self.texto_justificacion.setReadOnly(True)
        tab_layout.addWidget(self.texto_justificacion)
        
        tabs.addTab(tab_explicacion, "Explicación")
        
        # Pestaña: Síntomas considerados
        tab_sintomas = QWidget()
        tab_layout2 = QVBoxLayout(tab_sintomas)
        
        self.lista_sintomas = QListWidget()
        tab_layout2.addWidget(self.lista_sintomas)
        
        tabs.addTab(tab_sintomas, "Síntomas considerados")
        
        # Pestaña: Evidencias (PDFs)
        tab_evidencias = QWidget()
        tab_layout3 = QVBoxLayout(tab_evidencias)
        
        self.lista_evidencias = QListWidget()
        tab_layout3.addWidget(self.lista_evidencias)
        
        tabs.addTab(tab_evidencias, "Evidencias (PDFs)")
        
        layout.addWidget(tabs)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_datos)
        botones_layout.addWidget(btn_actualizar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones_layout.addWidget(btn_cerrar)
        
        layout.addLayout(botones_layout)
    
    def actualizar_datos(self):
        """Actualiza la justificación desde el modelo"""
        # Justificación
        justificacion = self.controlador.modelo.justificacion
        if justificacion:
            self.texto_justificacion.setText(justificacion)
        else:
            self.texto_justificacion.setText("No hay justificación disponible.")
        
        # Síntomas considerados
        self.lista_sintomas.clear()
        sintomas = self.controlador.modelo.sintomas
        for clave, valor in sintomas.items():
            self.lista_sintomas.addItem(f"• {clave}: {valor}")
        
        # Evidencias de PDFs
        self.lista_evidencias.clear()
        for pdf in self.controlador.modelo.pdfs:
            tamano = pdf.get('tamano')
            if tamano is None:
                tamano = pdf.get('tamaño', 0)
            self.lista_evidencias.addItem(f"📄 {pdf['nombre']} ({tamano/1024:.1f} KB)")