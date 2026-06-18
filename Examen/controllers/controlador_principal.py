from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal
from models.gestor_pdfs import GestorPDFs
from controllers.servicio_llm import ServicioLLM
from controllers.servicio_ollama import ServicioOllama
from controllers.motor_commonkads import MotorCommonKADS

class WorkerCompatibilidad(QThread):
    resultado_listo = pyqtSignal(bool, str)
    
    def __init__(self, servicio_ollama, motor_commonkads, usar_llm, componentes, contexto_pdfs):
        super().__init__()
        self.servicio_ollama = servicio_ollama
        self.motor_commonkads = motor_commonkads
        self.usar_llm = usar_llm
        self.componentes = componentes
        self.contexto_pdfs = contexto_pdfs
        
    def run(self):
        if self.usar_llm:
            es_compatible_llm, explicacion_llm = self.servicio_ollama.analizar_compatibilidad(
                self.componentes, self.contexto_pdfs
            )

            # Guardarraíl determinista (ontología): evita falsos compatibles del LLM
            explicacion_reglas = self.motor_commonkads.analizar_compatibilidad(self.componentes)
            veredicto_reglas = explicacion_reglas.upper()
            es_compatible_reglas = "INCOMPATIBLE" not in veredicto_reglas and "NO DETERMINADO" not in veredicto_reglas

            es_compatible = es_compatible_llm and es_compatible_reglas

            if es_compatible:
                explicacion = explicacion_llm
            elif not es_compatible_reglas:
                explicacion = (
                    "⚠️ El análisis por reglas/ontología detecta incompatibilidad (o falta de datos). "
                    "Se prioriza este resultado frente al LLM.\n\n"
                    f"{explicacion_reglas}"
                )
            else:
                explicacion = explicacion_llm
        else:
            explicacion = self.motor_commonkads.analizar_compatibilidad(self.componentes)
            veredicto = explicacion.upper()
            es_compatible = "INCOMPATIBLE" not in veredicto and "NO DETERMINADO" not in veredicto
        self.resultado_listo.emit(es_compatible, explicacion)

class WorkerHipotesis(QThread):
    resultado_listo = pyqtSignal(list)
    
    def __init__(self, servicio_ollama, motor_commonkads, usar_llm, prompt, contexto_pdfs, datos_sintomas, modo="Local (solo PDFs)"):
        super().__init__()
        self.servicio_ollama = servicio_ollama
        self.motor_commonkads = motor_commonkads
        self.usar_llm = usar_llm
        self.prompt = prompt
        self.contexto_pdfs = contexto_pdfs
        self.datos_sintomas = datos_sintomas
        self.modo = modo
        
    def run(self):
        if self.usar_llm:
            hipotesis = self.servicio_ollama.generar_hipotesis(self.prompt, self.contexto_pdfs, self.modo)
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
        self.worker_compatibilidad = None
    
    def set_vista_principal(self, vista):
        self.vista_principal = vista
    
    def cambiar_modo(self, modo):
        self.modelo.modo_actual = modo
    
    def cambiar_modelo_conocimiento(self, usar_llm):
        """Cambia entre CommonKADS y LLM"""
        self.usar_llm = usar_llm
    
    def evaluar_compatibilidad(self, componentes, usar_llm, callback):
        contexto_pdfs = self._obtener_contexto_pdfs() if usar_llm else ""
        
        self.worker_compatibilidad = WorkerCompatibilidad(
            self.servicio_ollama, self.motor_commonkads, usar_llm, componentes, contexto_pdfs
        )
        self.worker_compatibilidad.resultado_listo.connect(lambda ok, msg: callback(ok, msg))
        self.worker_compatibilidad.start()

    def verificar_compatibilidad_y_generar(self, datos_sintomas, callback_compatible, callback_incompatible):
        """Verifica compatibilidad de componentes existentes antes de generar hipótesis"""
        componentes = datos_sintomas.get('componentes_actuales', {})
        # Filtrar solo componentes con modelo real especificado
        componentes_reales = {k: v for k, v in componentes.items() 
                              if v and v != "Modelo no especificado"}
        
        if len(componentes_reales) < 2:
            # Con 0 o 1 componente no puede haber incompatibilidad
            callback_compatible()
            return
        
        usar_llm = datos_sintomas.get('conocimiento', {}).get('modelo', {}).get('tipo') == 'llm'
        contexto_pdfs = self._obtener_contexto_pdfs() if usar_llm else ""
        
        self.worker_compatibilidad = WorkerCompatibilidad(
            self.servicio_ollama, self.motor_commonkads, usar_llm, componentes_reales, contexto_pdfs
        )
        self.worker_compatibilidad.resultado_listo.connect(
            lambda ok, msg: callback_compatible() if ok else callback_incompatible(msg)
        )
        self.worker_compatibilidad.start()

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
            
        modo = self.modelo.modo_actual or "Local (solo PDFs)"
        self.worker_hipotesis = WorkerHipotesis(
            self.servicio_ollama, self.motor_commonkads, usar_llm, prompt, contexto_pdfs, datos_sintomas, modo
        )
        self.worker_hipotesis.resultado_listo.connect(lambda h: self._al_terminar_hipotesis(h, callback))
        self.worker_hipotesis.start()
        
    def _al_terminar_hipotesis(self, hipotesis, callback):
        self.modelo.hipotesis = hipotesis
        
        if self.vista_principal:
            if hasattr(self.vista_principal, 'label_estado'):
                self.vista_principal.label_estado.setText("✅ Hipótesis generadas de manera exitosa")
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
        prompt = ""
        
        # Perfil del usuario
        perfil = datos.get('perfil', {})
        if perfil:
            prompt += "PERFIL DEL USUARIO:\n"
            prompt += f"- Presupuesto: {perfil.get('presupuesto', 'No especificado')}€\n"
            prompt += f"- Prioridad: {perfil.get('prioridad', 'No especificada')}\n\n"
        
        # Componentes que YA TIENE el usuario (clave para reutilizar)
        componentes_actuales = datos.get('componentes_actuales', {})
        if componentes_actuales:
            prompt += "COMPONENTES QUE EL USUARIO YA POSEE (DEBEN REUTILIZARSE OBLIGATORIAMENTE):\n"
            for comp, modelo in componentes_actuales.items():
                prompt += f"- {comp}: {modelo}\n"
            prompt += "\n"
        else:
            prompt += "COMPONENTES ACTUALES: El usuario NO tiene ningún componente previo.\n\n"
        
        # Uso principal
        uso = datos.get('uso', {})
        if uso:
            prompt += f"USO PRINCIPAL: {uso.get('principal', 'No especificado')}\n"
            detalles = uso.get('detalles', '').strip()
            if detalles:
                prompt += f"Detalles adicionales: {detalles}\n"
            prompt += "\n"
        
        return prompt
    
    def _construir_prompt_diagnostico(self, datos, hipotesis):
        prompt = ""
        
        # Perfil
        perfil = datos.get('perfil', {})
        if perfil:
            prompt += "PERFIL DEL USUARIO:\n"
            prompt += f"- Presupuesto: {perfil.get('presupuesto', 'No especificado')}€\n"
            prompt += f"- Prioridad: {perfil.get('prioridad', 'No especificada')}\n\n"
        
        # Componentes que YA TIENE (crucial)
        componentes_actuales = datos.get('componentes_actuales', {})
        if componentes_actuales:
            prompt += "COMPONENTES QUE EL USUARIO YA POSEE (OBLIGATORIO INCLUIRLOS EN LA CONFIGURACIÓN FINAL):\n"
            for comp, modelo in componentes_actuales.items():
                prompt += f"- {comp}: {modelo}\n"
            prompt += "\n"
        else:
            prompt += "COMPONENTES ACTUALES: Ninguno, hay que proponer todos desde cero.\n\n"
        
        # Uso
        uso = datos.get('uso', {})
        if uso:
            prompt += f"USO PRINCIPAL: {uso.get('principal', 'No especificado')}\n"
            detalles = uso.get('detalles', '').strip()
            if detalles:
                prompt += f"Detalles: {detalles}\n"
            prompt += "\n"
        
        # Hipótesis seleccionada
        if hipotesis:
            prompt += f"HIPÓTESIS SELECCIONADA: {hipotesis.get('nombre', 'Ninguna')}\n"
            if hipotesis.get('detalles'):
                prompt += f"Detalles: {hipotesis['detalles']}\n"
            prompt += "\n"
        
        return prompt
    
    def _obtener_contexto_pdfs(self):
        """Obtiene el contenido real de texto de los PDFs cargados"""
        contexto = "INFORMACION EXTRAIDA DE PDFS LOCALES:\n"
        
        if not self.modelo.pdfs:
            contexto += "No hay PDFs cargados.\n"
            return contexto
        
        for pdf in self.modelo.pdfs:
            nombre = pdf['nombre']
            contenido = self.gestor_pdfs.obtener_contenido_texto(pdf['ruta'])
            # Limitar a ~3000 caracteres por PDF para no saturar el prompt
            if len(contenido) > 3000:
                contenido = contenido[:3000] + "\n... [contenido truncado por longitud]"
            contexto += f"\n{'='*40}\n📄 {nombre}\n{'='*40}\n{contenido}\n"
        
        return contexto