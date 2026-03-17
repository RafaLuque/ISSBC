from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class VentanaFuentes(QWidget):
    """
    Ventana para mostrar las fuentes web utilizadas en el diagnóstico
    """
    
    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setWindowTitle("Fuentes Web Consultadas")
        self.setGeometry(150, 150, 700, 400)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.init_ui()
        self.actualizar_tabla()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("<h2>Fuentes web utilizadas</h2>")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabla de fuentes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Título", "URL", "Fragmento relevante", "Fecha acceso"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setWordWrap(True)
        layout.addWidget(self.tabla)
        
        # Información
        self.label_info = QLabel("Modo actual: Local - No se han usado fuentes web")
        self.label_info.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label_info)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_tabla)
        botones_layout.addWidget(btn_actualizar)
        
        btn_exportar = QPushButton("Exportar fuentes")
        btn_exportar.clicked.connect(self.exportar_fuentes)
        botones_layout.addWidget(btn_exportar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones_layout.addWidget(btn_cerrar)
        
        layout.addLayout(botones_layout)
    
    def actualizar_tabla(self):
        """Actualiza la tabla con las fuentes del modelo"""
        fuentes = self.controlador.modelo.fuentes_web
        modo = self.controlador.modelo.modo_actual
        
        # Actualizar info
        if modo == "Web (PDFs + Internet)":
            self.label_info.setText(f"Modo actual: Web - {len(fuentes)} fuente(s) consultada(s)")
        else:
            self.label_info.setText("Modo actual: Local - No se han usado fuentes web")
        
        # Llenar tabla
        self.tabla.setRowCount(len(fuentes))
        
        for i, fuente in enumerate(fuentes):
            # Título
            item_titulo = QTableWidgetItem(fuente.get('titulo', ''))
            item_titulo.setFlags(item_titulo.flags() & ~Qt.ItemIsEditable)
            self.tabla.setItem(i, 0, item_titulo)
            
            # URL (como enlace)
            item_url = QTableWidgetItem(fuente.get('url', ''))
            item_url.setFlags(item_url.flags() & ~Qt.ItemIsEditable)
            item_url.setForeground(QBrush(QColor(0, 0, 255)))
            item_url.setFont(QFont("Arial", weight=QFont.Bold))
            self.tabla.setItem(i, 1, item_url)
            
            # Fragmento
            item_frag = QTableWidgetItem(fuente.get('fragmento', ''))
            item_frag.setFlags(item_frag.flags() & ~Qt.ItemIsEditable)
            self.tabla.setItem(i, 2, item_frag)
            
            # Fecha
            item_fecha = QTableWidgetItem(fuente.get('fecha', ''))
            item_fecha.setFlags(item_fecha.flags() & ~Qt.ItemIsEditable)
            self.tabla.setItem(i, 3, item_fecha)
        
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnWidth(2, 300)  # Dar más espacio al fragmento
    
    def exportar_fuentes(self):
        """Exporta las fuentes a un archivo"""
        fuentes = self.controlador.modelo.fuentes_web
        if not fuentes:
            QMessageBox.warning(self, "Aviso", "No hay fuentes para exportar")
            return
        
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar fuentes", "fuentes_web.txt", "Archivos de texto (*.txt)"
        )
        
        if ruta:
            try:
                with open(ruta, 'w', encoding='utf-8') as f:
                    f.write("=== FUENTES WEB CONSULTADAS ===\n\n")
                    for i, fuente in enumerate(fuentes, 1):
                        f.write(f"{i}. {fuente.get('titulo', 'Sin título')}\n")
                        f.write(f"   URL: {fuente.get('url', '')}\n")
                        f.write(f"   Fragmento: {fuente.get('fragmento', '')}\n")
                        f.write(f"   Fecha: {fuente.get('fecha', '')}\n\n")
                QMessageBox.information(self, "Éxito", "Fuentes exportadas correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar: {str(e)}")