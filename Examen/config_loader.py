import json
import os
from utils.rutas import obtener_ruta_relativa

class ConfigLoader:
    @staticmethod
    def cargar_config(ruta_archivo="config/config_diagnostico.json"):
        try:
            # Usar ruta relativa al proyecto
            ruta_completa = obtener_ruta_relativa(ruta_archivo)
            
            if os.path.exists(ruta_completa):
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Archivo de configuración no encontrado: {ruta_completa}")
                print("Usando configuración por defecto...")
                return ConfigLoader._config_default()
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return ConfigLoader._config_default()
    
    @staticmethod
    def _config_default():
        return {
            "dominio": "configuracion_pc",
            "titulo": "Sistema de Diagnóstico para Configuración de PC",
            "sintomas": {
                "categorias": [
                    {
                        "nombre": "Uso principal",
                        "tipo": "seleccion_unica",
                        "opciones": ["Gaming", "Edición de video", "Programación", "Ofimática", "Diseño 3D"],
                        "por_defecto": "Gaming"
                    }
                ],
                "observables": [
                    {
                        "nombre": "Presupuesto",
                        "tipo": "rango",
                        "min": 300,
                        "max": 5000,
                        "por_defecto": 1000
                    }
                ]
            },
            "modos_conocimiento": ["Local (solo PDFs)", "Web (PDFs + Internet)"],
            "modo_por_defecto": "Local (solo PDFs)"
        }