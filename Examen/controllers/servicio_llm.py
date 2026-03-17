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
    
    def generar_diagnostico(self, prompt, contexto_pdfs="", modo="Local"):
        """
        Genera diagnóstico simulado
        """
        # Simular diferentes diagnósticos según el contexto
        if "Gaming" in prompt:
            diagnostico = """**COMPONENTES RECOMENDADOS:**
- **CPU**: AMD Ryzen 5 7600X (6 núcleos, 12 hilos)
- **GPU**: NVIDIA RTX 4060 Ti 8GB
- **RAM**: 16GB DDR5-6000MHz (2x8GB)
- **Placa base**: MSI B650M PRO
- **Almacenamiento**: SSD NVMe 1TB
- **Fuente**: 650W 80+ Bronze
- **Caja**: Con buen flujo de aire

**PRECIO APROXIMADO:** 1100-1200€"""
            
            justificacion = """**JUSTIFICACIÓN:**
- La combinación Ryzen 5 + RTX 4060 Ti ofrece excelente rendimiento en 1080p/1440p
- 16GB RAM es el estándar actual para juegos
- SSD NVMe garantiza tiempos de carga mínimos
- Fuente de 650W proporciona margen suficiente

**EVIDENCIAS CONSIDERADAS:**
- Presupuesto del usuario: compatible
- Uso principal: Gaming - prioriza GPU
- Relación calidad-precio óptima en gama media"""
        
        elif "edición" in prompt.lower() or "video" in prompt.lower():
            diagnostico = """**COMPONENTES RECOMENDADOS:**
- **CPU**: Intel Core i7-13700K (16 núcleos, 24 hilos)
- **GPU**: NVIDIA RTX 4070 12GB
- **RAM**: 32GB DDR5-5600MHz (2x16GB)
- **Placa base**: ASUS PRIME Z790-P
- **Almacenamiento**: SSD NVMe 2TB + HDD 2TB
- **Fuente**: 750W 80+ Gold
- **Caja**: Silenciosa con buen flujo

**PRECIO APROXIMADO:** 1700-1900€"""
            
            justificacion = """**JUSTIFICACIÓN:**
- CPU con muchos núcleos ideal para renderizado
- 32GB RAM necesarios para edición 4K
- GPU con 12GB VRAM para efectos y exportación
- Almacenamiento dual: SSD para proyecto activo, HDD para archivo

**EVIDENCIAS CONSIDERADAS:**
- Requisitos de software de edición
- Flujo de trabajo con archivos grandes
- Tiempos de exportación críticos"""
        
        else:
            diagnostico = """**COMPONENTES RECOMENDADOS:**
- **CPU**: AMD Ryzen 5 5600G (con gráficos integrados)
- **RAM**: 16GB DDR4-3200MHz
- **Placa base**: B550M
- **Almacenamiento**: SSD 500GB
- **Fuente**: 500W 80+
- **Caja**: Básica

**PRECIO APROXIMADO:** 500-600€"""
            
            justificacion = """**JUSTIFICACIÓN:**
- Gráficos integrados suficientes para ofimática/programación
- Configuración equilibrada y económica
- Ampliable en el futuro si es necesario"""
        
        # Simular fuentes web si estamos en modo Web
        fuentes = []
        if modo == "Web (PDFs + Internet)":
            hoy = datetime.datetime.now().strftime("%d/%m/%Y")
            fuentes = [
                {
                    "titulo": "Guía de componentes gaming 2025",
                    "url": "https://www.pccomponentes.com/guia-gaming-2025",
                    "fragmento": "Las RTX 4060 ofrecen el mejor rendimiento por euro en 1080p",
                    "fecha": hoy
                },
                {
                    "titulo": "Foro de hardware - Configuraciones recomendadas",
                    "url": "https://foro.hardware.com/configuraciones/",
                    "fragmento": "Ryzen 5 7600X es la opción más equilibrada para gaming",
                    "fecha": hoy
                }
            ]
        
        return diagnostico, justificacion, fuentes