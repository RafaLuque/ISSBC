from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal
from models.gestor_pdfs import GestorPDFs
from controllers.servicio_llm import ServicioLLM
from controllers.servicio_ollama import ServicioOllama
from controllers.motor_commonkads import MotorCommonKADS

class WorkerHipotesis(QThread):
    resultado_listo = pyqtSignal(list)
    
    def __init__(self, servicio_ollama, motor_commonkads, usar_llm, prompt, contexto_pdfs, datos_sintomas):
        super().__init__()
        self.servicio_ollama = servicio_ollama
        self.motor_commonkads = motor_commonkads
        self.usar_llm = usar_llm
        self.prompt = prompt
        self.contexto_pdfs = contexto_pdfs
        self.datos_sintomas = datos_sintomas
        
    def run(self):
        if self.usar_llm:
            hipotesis = self.servicio_ollama.generar_hipotesis(self.prompt, self.contexto_pdfs)
        else:
            hipotesis = self.motor_commonkads.generar_hipotesis(self.datos_sintomas)
        self.resultado_listo.emit(hipotesis)

class WorkerDiagnostico(QThread):
    resultado_listo = pyqtSignal(object, str, list)
    
    def __init__(self, servicio_ollama, motor_commonkads, usar_llm, prompt, contexto_pdfs, modo, datos, hipotesis_seleccionada):
        super().__init__()
        self.servicio_ollama = servicio_ollama
        self.motor_commonkads = motor_commonkads
        self.usar_llm = usar_llm
        self.prompt = prompt
        self.contexto_pdfs = contexto_pdfs
        self.modo = modo
        self.datos = datos
        self.hipotesis_seleccionada = hipotesis_seleccionada
        
    def run(self):
        if self.usar_llm:
            diagnostico, justificacion, fuentes = self.servicio_ollama.generar_diagnostico(
                self.prompt, self.contexto_pdfs, self.modo
            )
        else:
            diagnostico, justificacion, fuentes = self.motor_commonkads.generar_diagnostico(
                self.datos, self.hipotesis_seleccionada
            )
        self.resultado_listo.emit(diagnostico, justificacion, fuentes)

class ControladorDiagnostico(QObject):
    def __init__(self, modelo, config):
        super().__init__()
        self.modelo = modelo
        self.config = config
        self.gestor_pdfs = GestorPDFs(modelo)
        
        # Inicializar motores con rutas genéricas
        self.motor_commonkads = MotorCommonKADS("config/reglas_commonkads.xml")
        self.servicio_ollama = ServicioOllama(config)
        self.servicio_llm = ServicioLLM(config)
        
        self.vista_principal = None
        self.worker_hipotesis = None
        self.worker_diagnostico = None
    
    def set_vista_principal(self, vista):
        self.vista_principal = vista
    
    def cambiar_modo(self, modo):
        self.modelo.modo_actual = modo
    
    def cambiar_modelo_conocimiento(self, usar_llm):
        """Cambia entre CommonKADS y LLM"""
        self.usar_llm = usar_llm
    
    def evaluar_hipotesis(self, datos_sintomas, callback=None):
        self.modelo.sintomas = datos_sintomas
        usar_llm = datos_sintomas.get('conocimiento', {}).get('modelo', {}).get('tipo') == 'llm'
        
        prompt = ""
        contexto_pdfs = ""
        if usar_llm:
            print("🤖 Usando LLM (Ollama) para generar hipótesis [HILO DE FONDO]")
            prompt = self._construir_prompt_hipotesis(datos_sintomas)
            contexto_pdfs = self._obtener_contexto_pdfs()
        else:
            print("📊 Usando CommonKADS para generar hipótesis [HILO DE FONDO]")
            
        self.worker_hipotesis = WorkerHipotesis(
            self.servicio_ollama, self.motor_commonkads, usar_llm, prompt, contexto_pdfs, datos_sintomas
        )
        self.worker_hipotesis.resultado_listo.connect(lambda h: self._al_terminar_hipotesis(h, callback))
        self.worker_hipotesis.start()
        
    def _al_terminar_hipotesis(self, hipotesis, callback):
        print(f"📥 Hipótesis recibidas del hilo: {len(hipotesis) if hipotesis else 0}")
        self.modelo.hipotesis = hipotesis
        
        if self.vista_principal:
            if hasattr(self.vista_principal, 'label_estado'):
                self.vista_principal.label_estado.setText("✅ Hipótesis generadas exitosamente")
            
            # Asegurar que la ventana se abre AHORA, después de tener los datos
            self.vista_principal.mostrar_ventana_hipotesis()
            self.vista_principal.actualizar_vistas()
            
        if callback:
            callback()
    
    def diagnosticar(self, hipotesis_seleccionada=None):
        if not self.modelo.hipotesis and self.modelo.sintomas:
            # Encadenar asincrónicamente
            self.evaluar_hipotesis(self.modelo.sintomas, callback=lambda: self._continuar_diagnostico(hipotesis_seleccionada))
        else:
            self._continuar_diagnostico(hipotesis_seleccionada)
    
    def _continuar_diagnostico(self, hipotesis_seleccionada=None):
        datos = self.modelo.sintomas
        usar_llm = datos.get('conocimiento', {}).get('modelo', {}).get('tipo') == 'llm'
        modo = self.modelo.modo_actual
        
        prompt = ""
        contexto_pdfs = ""
        if usar_llm:
            print("🤖 Usando LLM (Ollama) para diagnóstico [HILO DE FONDO]")
            prompt = self._construir_prompt_diagnostico(
                datos,
                hipotesis_seleccionada or (self.modelo.hipotesis[0] if self.modelo.hipotesis else {})
            )
            contexto_pdfs = self._obtener_contexto_pdfs()
        else:
            print("📊 Usando CommonKADS para diagnóstico [HILO DE FONDO]")
            
        self.worker_diagnostico = WorkerDiagnostico(
            self.servicio_ollama, self.motor_commonkads, usar_llm, 
            prompt, contexto_pdfs, modo, datos, hipotesis_seleccionada
        )
        self.worker_diagnostico.resultado_listo.connect(self._al_terminar_diagnostico)
        self.worker_diagnostico.start()
        
    def _al_terminar_diagnostico(self, diagnostico, justificacion, fuentes):
        self.modelo.diagnostico_final = diagnostico
        self.modelo.justificacion = justificacion
        
        for fuente in fuentes:
            self.modelo.agregar_fuente_web(
                fuente.get('titulo', 'Sin titulo'),
                fuente.get('url', ''),
                fuente.get('fragmento', ''),
                fuente.get('fecha', '')
            )
        
        if self.vista_principal:
            if hasattr(self.vista_principal, 'label_estado'):
                self.vista_principal.label_estado.setText("✅ Diagnóstico completado exitosamente")
            self.vista_principal.mostrar_ventana_diagnostico()
            self.vista_principal.mostrar_ventana_justificacion()
            if self.modelo.modo_actual == "Web (PDFs + Internet)":
                self.vista_principal.mostrar_ventana_fuentes()
            self.vista_principal.actualizar_vistas()
    
    def _construir_prompt_hipotesis(self, datos):
        prompt = "Eres un experto en hardware. Genera configuraciones posibles basadas en:\n"
        for clave, valor in datos.items():
            prompt += f"- {clave}: {valor}\n"
        return prompt
    
    def _construir_prompt_diagnostico(self, datos, hipotesis):
        return f"Eres un experto en hardware. Datos: {datos}. Hipotesis: {hipotesis}"
    
    def _obtener_contexto_pdfs(self):
        """Obtiene texto de los PDFs cargados"""
        contexto = "INFORMACION DE PDFS LOCALES:\n"
        for pdf in self.modelo.pdfs:
            # Compatibilidad con 'tamano' y 'tamaño'
            tamano = pdf.get('tamano')
            if tamano is None:
                tamano = pdf.get('tamaño', 0)
            
            contexto += f"- {pdf['nombre']} ({tamano/1024:.1f} KB)\n"
        
        if not self.modelo.pdfs:
            contexto += "No hay PDFs cargados.\n"
        
        return contexto