from PyQt5.QtCore import QObject, QTimer
from models.gestor_pdfs import GestorPDFs
from controllers.servicio_llm import ServicioLLM

class ControladorDiagnostico(QObject):
    """
    Controlador MVC: Coordina el flujo de la aplicación.
    Recibe eventos de la vista, actualiza el modelo e invoca al LLM.
    """
    
    def __init__(self, modelo, config):
        super().__init__()
        self.modelo = modelo
        self.config = config
        self.gestor_pdfs = GestorPDFs(modelo)
        self.servicio_llm = ServicioLLM(config)
        self.vista_principal = None
    
    def set_vista_principal(self, vista):
        """Establece la referencia a la vista principal"""
        self.vista_principal = vista
    
    def evaluar_hipotesis(self, datos_sintomas):
        """
        Genera hipótesis basadas en los síntomas ingresados
        """
        # Actualizar modelo con síntomas
        self.modelo.sintomas = datos_sintomas
        
        # Construir prompt según el modo seleccionado
        prompt = self._construir_prompt_hipotesis(datos_sintomas)
        
        # Obtener contexto de PDFs si estamos en modo Local
        contexto_pdfs = ""
        if self.modelo.modo_actual == "Local (solo PDFs)" and self.modelo.pdfs:
            contexto_pdfs = self._obtener_contexto_pdfs()
        
        # Llamar al LLM (o stub) para generar hipótesis
        hipotesis = self.servicio_llm.generar_hipotesis(prompt, contexto_pdfs)
        
        # Actualizar modelo
        self.modelo.hipotesis = hipotesis
        
        # Mostrar ventana de hipótesis
        if self.vista_principal:
            self.vista_principal.mostrar_ventana_hipotesis()
    
    def diagnosticar(self, hipotesis_seleccionada=None):
        """
        Genera diagnóstico final basado en la hipótesis seleccionada
        """
        # Si no hay hipótesis, generar primero
        if not self.modelo.hipotesis and self.modelo.sintomas:
            self.evaluar_hipotesis(self.modelo.sintomas)
            # Programar diagnóstico después de un breve retraso
            QTimer.singleShot(100, lambda: self._continuar_diagnostico(hipotesis_seleccionada))
        else:
            self._continuar_diagnostico(hipotesis_seleccionada)
    
    def _continuar_diagnostico(self, hipotesis_seleccionada):
        """Continuación del diagnóstico después de tener hipótesis"""
        # Construir prompt para diagnóstico
        prompt = self._construir_prompt_diagnostico(
            self.modelo.sintomas,
            hipotesis_seleccionada or (self.modelo.hipotesis[0] if self.modelo.hipotesis else {})
        )
        
        # Obtener contexto
        contexto_pdfs = ""
        if self.modelo.modo_actual == "Local (solo PDFs)" and self.modelo.pdfs:
            contexto_pdfs = self._obtener_contexto_pdfs()
        
        # Llamar al LLM
        diagnostico, justificacion, fuentes = self.servicio_llm.generar_diagnostico(
            prompt, contexto_pdfs, self.modelo.modo_actual
        )
        
        # Actualizar modelo
        self.modelo.diagnostico_final = diagnostico
        self.modelo.justificacion = justificacion
        
        # Añadir fuentes web si estamos en modo Web
        if self.modelo.modo_actual == "Web (PDFs + Internet)" and fuentes:
            for fuente in fuentes:
                self.modelo.agregar_fuente_web(
                    fuente.get('titulo', 'Sin título'),
                    fuente.get('url', ''),
                    fuente.get('fragmento', ''),
                    fuente.get('fecha', '')
                )
        
        # Mostrar ventanas de resultados
        if self.vista_principal:
            self.vista_principal.mostrar_ventana_diagnostico()
            self.vista_principal.mostrar_ventana_justificacion()
            if self.modelo.modo_actual == "Web (PDFs + Internet)":
                self.vista_principal.mostrar_ventana_fuentes()
    
    def ver_justificacion(self):
        """Muestra la justificación del diagnóstico actual"""
        if self.vista_principal:
            self.vista_principal.mostrar_ventana_justificacion()
    
    def cambiar_modo(self, modo):
        """Cambia el modo de conocimiento (Local/Web)"""
        self.modelo.modo_actual = modo
    
    def _construir_prompt_hipotesis(self, datos):
        """Construye el prompt para generar hipótesis"""
        prompt = f"""
Eres un experto en hardware de ordenadores. Basándote en los siguientes datos del usuario, genera una lista de 3-5 hipótesis sobre qué configuración de componentes sería más adecuada.

DATOS DEL USUARIO:
"""
        for clave, valor in datos.items():
            prompt += f"- {clave}: {valor}\n"
        
        prompt += """
Formato de respuesta requerido (lista de hipótesis en formato JSON):
[
    {"nombre": "Configuración Gaming", "probabilidad": 0.85, "estado": "posible"},
    {"nombre": "Configuración Workstation", "probabilidad": 0.65, "estado": "posible"}
]
"""
        return prompt
    
    def _construir_prompt_diagnostico(self, datos, hipotesis):
        """Construye el prompt para el diagnóstico final"""
        prompt = f"""
Eres un experto en hardware. Realiza un diagnóstico completo para:

DATOS DEL USUARIO:
"""
        for clave, valor in datos.items():
            prompt += f"- {clave}: {valor}\n"
        
        prompt += f"\nHIPÓTESIS PRINCIPAL: {hipotesis.get('nombre', 'No especificada')}\n"
        
        prompt += """
Proporciona:
1. DIAGNÓSTICO: Lista detallada de componentes recomendados
2. JUSTIFICACIÓN: Explica por qué estos componentes son adecuados
3. FUENTES: Si usaste información externa, indica las fuentes

Formato de respuesta:
DIAGNÓSTICO: [texto con lista de componentes]
JUSTIFICACIÓN: [explicación detallada]
FUENTES: [lista de fuentes si aplica]
"""
        return prompt
    
    def _obtener_contexto_pdfs(self):
        """Obtiene texto de los PDFs cargados"""
        contexto = "INFORMACIÓN DE PDFS LOCALES:\n"
        for pdf in self.modelo.pdfs:
            # Aquí usarías el gestor para extraer texto real
            contexto += f"- {pdf['nombre']}\n"
        return contexto
    
    def _get_modelo_conocimiento(self, datos):
        """
        Determina qué modelo de conocimiento se está usando
        y prepara el contexto adecuado
        """
        modelo_info = datos.get('modelo_conocimiento', {})
        tipo = modelo_info.get('tipo', 'commonkads')
        
        if tipo == 'llm':
            modelo = modelo_info.get('llm_modelo', 'qwen2.5:7b')
            return {
                'tipo': 'llm',
                'modelo': modelo,
                'descripcion': f'Generando con LLM ({modelo})'
            }
        else:
            archivo = modelo_info.get('archivo_reglas', 'reglas_default.xml')
            return {
                'tipo': 'commonkads',
                'archivo': archivo,
                'descripcion': f'Inferencia con reglas CommonKADS: {archivo}'
            }