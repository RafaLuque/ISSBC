import json
import os

class ConfigLoader:
    """Carga la configuración desde archivo externo JSON"""
    
    @staticmethod
    def cargar_config(ruta_archivo="config/config_diagnostico.json"):
        """
        Carga la configuración desde un archivo JSON.
        Si no existe, usa configuración por defecto.
        """
        try:
            # Intentar cargar desde la ruta especificada
            if os.path.exists(ruta_archivo):
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Intentar desde la raíz del proyecto
                ruta_base = os.path.join(os.path.dirname(__file__), ruta_archivo)
                if os.path.exists(ruta_base):
                    with open(ruta_base, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    print(f"Archivo de configuración no encontrado: {ruta_archivo}")
                    print("Usando configuración por defecto...")
                    return ConfigLoader._config_default()
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return ConfigLoader._config_default()
    
    @staticmethod
    def _config_default():
        """Configuración por defecto si no existe archivo externo"""
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
                    },
                    {
                        "nombre": "Nivel de experiencia",
                        "tipo": "seleccion_unica",
                        "opciones": ["Principiante", "Intermedio", "Avanzado"],
                        "por_defecto": "Intermedio"
                    }
                ],
                "observables": [
                    {
                        "nombre": "Presupuesto (€)",
                        "tipo": "rango",
                        "min": 300,
                        "max": 5000,
                        "por_defecto": 1000
                    },
                    {
                        "nombre": "¿Tiene componentes actuales?",
                        "tipo": "booleano",
                        "por_defecto": False
                    },
                    {
                        "nombre": "¿Prioriza rendimiento sobre presupuesto?",
                        "tipo": "booleano",
                        "por_defecto": True
                    }
                ]
            },
            "componentes_recomendados": [
                {"nombre": "CPU", "requerido": True},
                {"nombre": "GPU", "requerido": False},
                {"nombre": "RAM", "requerido": True},
                {"nombre": "Placa base", "requerido": True},
                {"nombre": "Almacenamiento", "requerido": True},
                {"nombre": "Fuente de alimentación", "requerido": True},
                {"nombre": "Caja", "requerido": False},
                {"nombre": "Refrigeración", "requerido": False}
            ],
            "modos_conocimiento": ["Local (solo PDFs)", "Web (PDFs + Internet)"],
            "modo_por_defecto": "Local (solo PDFs)",
            "colores": {
                "primario": "#2c3e50",
                "secundario": "#3498db",
                "exito": "#27ae60",
                "peligro": "#e74c3c",
                "fondo": "#ecf0f1"
            }
        }