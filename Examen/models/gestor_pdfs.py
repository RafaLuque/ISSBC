import os
import json
import pickle
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject

class GestorPDFs(QObject):
    """
    Gestiona la carga y procesamiento de archivos PDF locales.
    Ahora con persistencia entre sesiones.
    """
    
    def __init__(self, modelo):
        super().__init__()
        self.modelo = modelo
        self.ruta_persistencia = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "pdfs_cache.json"
        )
        
        # Cargar PDFs guardados al iniciar
        self.cargar_pdfs_guardados()
    
    def seleccionar_pdfs(self, parent_widget):
        """
        Abre diálogo para seleccionar múltiples PDFs
        """
        archivos, _ = QFileDialog.getOpenFileNames(
            parent_widget,
            "Seleccionar archivos PDF",
            "",
            "Archivos PDF (*.pdf)"
        )
        
        for archivo in archivos:
            if archivo.lower().endswith('.pdf'):
                nombre = os.path.basename(archivo)
                tamaño = os.path.getsize(archivo)
                self.modelo.agregar_pdf(archivo, nombre, tamaño)
        
        # Guardar lista actualizada
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
                        'tamaño': pdf['tamaño']
                    })
            
            with open(self.ruta_persistencia, 'w', encoding='utf-8') as f:
                json.dump(pdfs_para_guardar, f, indent=2, ensure_ascii=False)
                
            print(f"✅ PDFs guardados: {len(pdfs_para_guardar)} archivos")
            
        except Exception as e:
            print(f"❌ Error guardando PDFs: {e}")
    
    def cargar_pdfs_guardados(self):
        """
        Carga los PDFs guardados en la sesión anterior
        """
        try:
            if os.path.exists(self.ruta_persistencia):
                with open(self.ruta_persistencia, 'r', encoding='utf-8') as f:
                    pdfs_guardados = json.load(f)
                
                # Verificar qué archivos siguen existiendo
                for pdf in pdfs_guardados:
                    if os.path.exists(pdf['ruta']):
                        self.modelo.agregar_pdf(
                            pdf['ruta'],
                            pdf['nombre'],
                            pdf['tamaño']
                        )
                    else:
                        print(f"⚠️ Archivo no encontrado: {pdf['ruta']}")
                
                print(f"✅ Cargados {len(self.modelo.pdfs)} PDFs de sesión anterior")
            else:
                print("ℹ️ No hay PDFs guardados de sesiones anteriores")
                
        except Exception as e:
            print(f"❌ Error cargando PDFs guardados: {e}")