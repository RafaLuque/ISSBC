# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Añadir directorios al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.controlador_principal import ControladorDiagnostico
from models.modelo_datos import ModeloDiagnostico
from config_loader import ConfigLoader
from views.ventana_principal import VentanaPrincipal

def main():
    # Configurar atributos de alto DPI para mejor visualización
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Diagnóstico PC")
    
    # Cargar configuración externa
    config = ConfigLoader.cargar_config()
    
    # Inicializar MVC
    modelo = ModeloDiagnostico()
    controlador = ControladorDiagnostico(modelo, config)
    vista = VentanaPrincipal(controlador, config)
    
    # Conectar señales del modelo a la vista
    modelo.datos_actualizados.connect(vista.actualizar_vistas)
    
    # Mostrar ventana principal
    vista.show()
    
    sys.exit(app.exec_())
    
    # Al cerrar la app, los PDFs ya se guardaron automáticamente
    # pero podemos añadir un manejador
    app.aboutToQuit.connect(guardar_pdfs_al_salir)
    
    sys.exit(app.exec_())

def guardar_pdfs_al_salir():
    """Función opcional para guardar al salir"""
    print("💾 Guardando estado antes de salir...")
    # No es necesario hacer nada aquí porque ya se guarda en cada operación    

if __name__ == "__main__":
    main()
    
    


