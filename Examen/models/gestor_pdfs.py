import os
import json
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject
from utils.rutas import obtener_ruta_relativa

class GestorPDFs(QObject):
    def __init__(self, modelo):
        super().__init__()
        self.modelo = modelo
        # Usar ruta genérica para el caché
        self.ruta_persistencia = obtener_ruta_relativa("config/pdfs_cache.json")
        self.cargar_pdfs_guardados()
    
    def seleccionar_pdfs(self, parent_widget):
        """
        Abre diálogo para seleccionar múltiples PDFs
        """
        # Abrir diálogo en la carpeta de pdfs_utilizados por defecto
        carpeta_pdfs = obtener_ruta_relativa("pdfs_utilizados")
        if not os.path.exists(carpeta_pdfs):
            os.makedirs(carpeta_pdfs, exist_ok=True)
        
        archivos, _ = QFileDialog.getOpenFileNames(
            parent_widget,
            "Seleccionar archivos PDF",
            carpeta_pdfs,  # <-- Carpeta por defecto
            "Archivos PDF (*.pdf)"
        )
        
        for archivo in archivos:
            if archivo.lower().endswith('.pdf'):
                nombre = os.path.basename(archivo)
                tamano = os.path.getsize(archivo)
                self.modelo.agregar_pdf(archivo, nombre, tamano)
        
        self.guardar_pdfs()
        return len(archivos)
        
    def eliminar_pdf_seleccionado(self, indice):
        """Elimina un PDF por su índice"""
        self.modelo.eliminar_pdf(indice)
        self.guardar_pdfs()  # Guardar cambios
    
    def vaciar_todos(self):
        """Elimina todos los PDFs"""
        self.modelo.vaciar_pdfs()
        self.guardar_pdfs()  # Guardar cambios
    
    def obtener_contenido_texto(self, ruta_pdf):
        """
        Simula la extracción de texto de un PDF.
        En una implementación real usarías PyPDF2 o similar.
        """
        # Simulación - en producción usarías una librería como PyPDF2
        return f"[Contenido simulado del PDF: {os.path.basename(ruta_pdf)}]"
    
    def guardar_pdfs(self):
        """
        Guarda la lista de PDFs en un archivo para persistencia
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.ruta_persistencia), exist_ok=True)
            
            # Guardar solo las rutas (los archivos en sí no, solo referencias)
            pdfs_para_guardar = []
            for pdf in self.modelo.pdfs:
                # Verificar que el archivo sigue existiendo
                if os.path.exists(pdf['ruta']):
                    pdfs_para_guardar.append({
                        'ruta': pdf['ruta'],
                        'nombre': pdf['nombre'],
                        'tamano': pdf['tamano']
                    })
            
            with open(self.ruta_persistencia, 'w', encoding='utf-8') as f:
                json.dump(pdfs_para_guardar, f, indent=2, ensure_ascii=False)
                
            print(f"✅ PDFs guardados: {len(pdfs_para_guardar)} archivos")
            
        except Exception as e:
            print(f"❌ Error guardando PDFs: {e}")
    
    def cargar_pdfs_guardados(self):
        """Carga los PDFs guardados en la sesión anterior"""
        try:
            if os.path.exists(self.ruta_persistencia):
                with open(self.ruta_persistencia, 'r', encoding='utf-8') as f:
                    pdfs_guardados = json.load(f)
                
                for pdf in pdfs_guardados:
                    if os.path.exists(pdf['ruta']):
                        # Normalizar: asegurar que la clave es 'tamano'
                        tamano = pdf.get('tamano')
                        if tamano is None:
                            tamano = pdf.get('tamaño', 0)
                        
                        # Agregar con clave unificada
                        self.modelo.agregar_pdf(
                            pdf['ruta'], 
                            pdf['nombre'], 
                            tamano
                        )
        except Exception as e:
            print(f"Error cargando PDFs: {e}")

    def normalizar_pdfs(self):
        """Normaliza todos los PDFs para usar 'tamano' en lugar de 'tamaño'"""
        for i, pdf in enumerate(self.modelo._pdfs):
            if 'tamaño' in pdf and 'tamano' not in pdf:
                self.modelo._pdfs[i]['tamano'] = pdf['tamaño']
                # Opcional: eliminar la clave antigua
                # del self.modelo._pdfs[i]['tamaño']
        
        self.guardar_pdfs()