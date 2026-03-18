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
        self.vista_principal = None  # Referencia a la vista principal
    
    def set_vista_principal(self, vista):
        """Establece la referencia a la vista principal"""
        self.vista_principal = vista
        print("✅ Vista principal conectada al controlador")
    
    def cambiar_modo(self, modo):
        """Cambia el modo de conocimiento (Local/Web)"""
        print(f"🔍 Cambiando modo a: {modo}")
        self.modelo.modo_actual = modo
    
    def evaluar_hipotesis(self, datos_sintomas):
        """Genera hipótesis basadas en los síntomas ingresados"""
        self.modelo.sintomas = datos_sintomas
        prompt = self._construir_prompt_hipotesis(datos_sintomas)
        
        contexto_pdfs = ""
        if self.modelo.pdfs:
            contexto_pdfs = self._obtener_contexto_pdfs()
        
        hipotesis = self.servicio_llm.generar_hipotesis(prompt, contexto_pdfs)
        self.modelo.hipotesis = hipotesis
        
        if self.vista_principal:
            self.vista_principal.mostrar_ventana_hipotesis()
    
    def diagnosticar(self, hipotesis_seleccionada=None):
        """Genera diagnóstico final"""
        if not self.modelo.hipotesis and self.modelo.sintomas:
            self.evaluar_hipotesis(self.modelo.sintomas)
            QTimer.singleShot(100, lambda: self._continuar_diagnostico(hipotesis_seleccionada))
        else:
            self._continuar_diagnostico(hipotesis_seleccionada)
    
    def _continuar_diagnostico(self, hipotesis_seleccionada=None):
        """Continuación del diagnóstico"""
        prompt = self._construir_prompt_diagnostico(
            self.modelo.sintomas,
            hipotesis_seleccionada or (self.modelo.hipotesis[0] if self.modelo.hipotesis else {})
        )
        
        contexto_pdfs = ""
        if self.modelo.pdfs:
            contexto_pdfs = self._obtener_contexto_pdfs()
        
        diagnostico, justificacion, fuentes = self.servicio_llm.generar_diagnostico(
            prompt, contexto_pdfs, self.modelo.modo_actual
        )
        
        self.modelo.diagnostico_final = diagnostico
        self.modelo.justificacion = justificacion
        
        for fuente in fuentes:
            self.modelo.agregar_fuente_web(
                fuente.get('titulo', 'Sin título'),
                fuente.get('url', ''),
                fuente.get('fragmento', ''),
                fuente.get('fecha', '')
            )
        
        if self.vista_principal:
            self.vista_principal.mostrar_ventana_diagnostico()
            self.vista_principal.mostrar_ventana_justificacion()
            if self.modelo.modo_actual == "Web (PDFs + Internet)":
                self.vista_principal.mostrar_ventana_fuentes()
    
    def _construir_prompt_hipotesis(self, datos):
        """Construye el prompt para hipótesis"""
        prompt = "Eres un experto en hardware. Genera configuraciones posibles basadas en:\n"
        for clave, valor in datos.items():
            prompt += f"- {clave}: {valor}\n"
        return prompt
    
    def _construir_prompt_diagnostico(self, datos, hipotesis):
        """Construye el prompt para diagnóstico"""
        prompt = f"Eres un experto en hardware. Datos: {datos}. Hipótesis: {hipotesis}"
        return prompt
    
    def _obtener_contexto_pdfs(self):
        """Obtiene contexto de PDFs"""
        return "Información de PDFs cargados"