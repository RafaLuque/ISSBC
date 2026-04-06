from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class VentanaPDFs(QWidget):
    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.controlador = controlador
        self.setWindowTitle("Gestión de PDFs - Conocimiento Local")
        self.setGeometry(150, 150, 600, 400)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.init_ui()
        self.actualizar_lista()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        titulo = QLabel("<h2>Gestión de archivos PDF</h2>")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        self.lista_pdfs = QListWidget()
        self.lista_pdfs.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.lista_pdfs)
        
        self.label_info = QLabel("0 archivos cargados")
        self.label_info.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label_info)
        
        botones_layout = QHBoxLayout()
        
        btn_anadir = QPushButton("➕ Añadir PDFs")
        btn_anadir.clicked.connect(self.anadir_pdfs)
        botones_layout.addWidget(btn_anadir)
        
        btn_eliminar = QPushButton("➖ Eliminar seleccionados")
        btn_eliminar.clicked.connect(self.eliminar_seleccionados)
        botones_layout.addWidget(btn_eliminar)
        
        btn_vaciar = QPushButton("🗑️ Vaciar todo")
        btn_vaciar.clicked.connect(self.vaciar_todo)
        botones_layout.addWidget(btn_vaciar)
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_lista)
        botones_layout.addWidget(btn_actualizar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones_layout.addWidget(btn_cerrar)
        
        layout.addLayout(botones_layout)
    
    def anadir_pdfs(self):
        num = self.controlador.gestor_pdfs.seleccionar_pdfs(self)
        if num > 0:
            self.actualizar_lista()
            QMessageBox.information(self, "Éxito", f"Se añadieron {num} archivo(s)")
    
    def eliminar_seleccionados(self):
        seleccionados = self.lista_pdfs.selectedItems()
        if not seleccionados:
            QMessageBox.warning(self, "Aviso", "Selecciona al menos un PDF")
            return
        
        for item in reversed(seleccionados):
            fila = self.lista_pdfs.row(item)
            self.controlador.gestor_pdfs.eliminar_pdf_seleccionado(fila)
        
        self.actualizar_lista()
    
    def vaciar_todo(self):
        if self.controlador.modelo.pdfs:
            reply = QMessageBox.question(
                self, "Confirmar", 
                "¿Estás seguro de eliminar todos los PDFs?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.controlador.gestor_pdfs.vaciar_todos()
                self.actualizar_lista()
    
    def actualizar_lista(self):
        """Actualiza la lista con los PDFs del modelo"""
        self.lista_pdfs.clear()
        pdfs = self.controlador.modelo.pdfs
        
        for pdf in pdfs:
            # Compatibilidad: puede venir como 'tamano' o 'tamaño'
            tamano = pdf.get('tamano')
            if tamano is None:
                tamano = pdf.get('tamaño', 0)
            
            item_text = f"{pdf['nombre']} ({tamano/1024:.1f} KB)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, pdf['ruta'])
            self.lista_pdfs.addItem(item)
        
        self.label_info.setText(f"{len(pdfs)} archivo(s) cargados")