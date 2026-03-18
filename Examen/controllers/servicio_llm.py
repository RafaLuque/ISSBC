import random
import datetime

class ServicioLLM:
    """
    Servicio que simula las respuestas de un LLM.
    En producción, aquí iría la integración real con Ollama.
    """
    
    def __init__(self, config):
        self.config = config
    
    def generar_hipotesis(self, prompt, contexto_pdfs=""):
        """
        Genera hipótesis simuladas basadas en el prompt
        """
        # Simular diferentes hipótesis según el uso principal
        uso = "Gaming"  # Valor por defecto
        if "Gaming" in prompt:
            uso = "Gaming"
        elif "Edición" in prompt:
            uso = "Edición"
        elif "Programación" in prompt:
            uso = "Programación"
        
        hipotesis = []
        
        if uso == "Gaming":
            hipotesis = [
                {"nombre": "Configuración Gaming 1080p", "probabilidad": 0.85, "estado": "posible"},
                {"nombre": "Configuración Gaming 1440p", "probabilidad": 0.70, "estado": "posible"},
                {"nombre": "Configuración Gaming económica", "probabilidad": 0.60, "estado": "posible"},
                {"nombre": "Configuración Workstation", "probabilidad": 0.30, "estado": "descartada"}
            ]
        elif uso == "Edición":
            hipotesis = [
                {"nombre": "Workstation edición video", "probabilidad": 0.90, "estado": "posible"},
                {"nombre": "Configuración Gaming + edición", "probabilidad": 0.75, "estado": "posible"},
                {"nombre": "Configuración ofimática", "probabilidad": 0.25, "estado": "descartada"}
            ]
        else:
            hipotesis = [
                {"nombre": "Configuración programación", "probabilidad": 0.80, "estado": "posible"},
                {"nombre": "Configuración ofimática", "probabilidad": 0.65, "estado": "posible"},
                {"nombre": "Workstation", "probabilidad": 0.50, "estado": "posible"}
            ]
        
        return hipotesis
    
    def buscar_en_internet(self, consulta):
        """
        Simula una búsqueda en internet.
        En una implementación real, aquí iría una API de búsqueda.
        """
        # Simular resultados de búsqueda según la consulta
        resultados = []
        
        if "gaming" in consulta.lower() or "juegos" in consulta.lower():
            resultados = [
                {
                    "titulo": "Mejores componentes para gaming 2025",
                    "url": "https://www.pccomponentes.com/guia-gaming",
                    "fragmento": "Las RTX 4060 y RX 7600 ofrecen el mejor rendimiento por euro en 1080p",
                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                },
                {
                    "titulo": "Foro: Configuraciones gaming por presupuesto",
                    "url": "https://foro.hardware.com/gaming-configs",
                    "fragmento": "Para 1000€, recomendamos Ryzen 5 7600 + RTX 4060",
                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                }
            ]
        elif "edición" in consulta.lower() or "video" in consulta.lower():
            resultados = [
                {
                    "titulo": "Workstations para edición de video",
                    "url": "https://www.pccomponentes.com/edicion-video",
                    "fragmento": "Intel i7 o Ryzen 7 con 32GB RAM son ideales para edición 4K",
                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                }
            ]
        else:
            resultados = [
                {
                    "titulo": "Guía general de compatibilidad",
                    "url": "https://www.pccomponentes.com/compatibilidad",
                    "fragmento": "Verifica siempre el socket de la CPU con la placa base",
                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                }
            ]
        
        return resultados
    
    def generar_diagnostico(self, prompt, contexto_pdfs="", modo="Local (solo PDFs)"):
        """
        Genera diagnóstico simulado con búsqueda web si es modo Web
        """
        print(f"🔍 Modo recibido en servicio_llm: {modo}")
        
        # Simular diferentes diagnósticos según el contexto
        if "Gaming" in prompt:
            diagnostico = """**COMPONENTES RECOMENDADOS:**
    - **CPU**: AMD Ryzen 5 7600X
    - **GPU**: NVIDIA RTX 4060 Ti 8GB
    - **RAM**: 16GB DDR5-6000MHz
    - **Placa base**: MSI B650M PRO
    - **Almacenamiento**: SSD NVMe 1TB
    - **Fuente**: 650W 80+ Bronze"""
            
            justificacion = """**JUSTIFICACIÓN:**
    - La combinación Ryzen 5 + RTX 4060 Ti ofrece excelente rendimiento en 1080p/1440p
    - 16GB RAM es el estándar actual para juegos
    - SSD NVMe garantiza tiempos de carga mínimos"""
        else:
            diagnostico = """**COMPONENTES RECOMENDADOS:**
    - **CPU**: AMD Ryzen 5 5600G
    - **RAM**: 16GB DDR4-3200MHz
    - **Placa base**: B550M
    - **Almacenamiento**: SSD 500GB
    - **Fuente**: 500W 80+"""
            
            justificacion = """**JUSTIFICACIÓN:**
    - Gráficos integrados suficientes para ofimática/programación
    - Configuración equilibrada y económica"""
        
        # Si es modo Web, realizar búsqueda en internet
        fuentes = []
        if modo == "Web (PDFs + Internet)":  # Comparación exacta
            print("🔍 MODO WEB ACTIVADO - Buscando fuentes...")
            # Extraer consulta del prompt
            consulta = prompt[:100]
            fuentes = self.buscar_en_internet(consulta)
            print(f"🔍 Fuentes encontradas: {len(fuentes)}")
        else:
            print("🔍 MODO LOCAL - No se buscan fuentes web")
        
        return diagnostico, justificacion, fuentes